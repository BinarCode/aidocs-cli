"""File system watcher for auto-syncing documentation."""

import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .chunker import (
    calculate_file_hash,
    chunk_file,
    get_chunks_path,
    load_manifest,
    save_chunks,
    save_manifest,
)
from .embeddings import generate_embedding, get_openai_api_key, load_last_sync, save_last_sync

console = Console()


class WatchState:
    """Shared state for the watcher."""

    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.pending_files: set[Path] = set()
        self.lock = threading.Lock()
        self.last_process_time: Optional[datetime] = None
        self.total_files = 0
        self.total_chunks = 0
        self.total_embeddings = 0
        self.recent_files: list[tuple[str, int, str]] = []  # (path, chunks, status)
        self.api_key: Optional[str] = None
        self.embeddings_enabled = False


class MarkdownEventHandler(FileSystemEventHandler):
    """Handle file system events for markdown files."""

    def __init__(
        self,
        state: WatchState,
        debounce_seconds: float,
        process_callback: callable,
    ):
        super().__init__()
        self.state = state
        self.debounce_seconds = debounce_seconds
        self.process_callback = process_callback
        self.timer: Optional[threading.Timer] = None
        self.timer_lock = threading.Lock()

    def _should_process(self, path: Path) -> bool:
        """Check if a file should be processed."""
        # Only process .md files
        if path.suffix.lower() != ".md":
            return False

        # Skip hidden directories and files
        try:
            rel_path = path.relative_to(self.state.docs_dir)
            parts = rel_path.parts
            if any(p.startswith(".") for p in parts):
                return False
        except ValueError:
            return False

        # Skip .chunks.json files
        if ".chunks" in path.name:
            return False

        return True

    def _schedule_processing(self):
        """Schedule file processing after debounce delay."""
        with self.timer_lock:
            if self.timer:
                self.timer.cancel()

            self.timer = threading.Timer(
                self.debounce_seconds,
                self.process_callback,
            )
            self.timer.start()

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return

        path = Path(event.src_path)
        if self._should_process(path):
            with self.state.lock:
                self.state.pending_files.add(path)
            self._schedule_processing()

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return

        path = Path(event.src_path)
        if self._should_process(path):
            with self.state.lock:
                self.state.pending_files.add(path)
            self._schedule_processing()

    def on_deleted(self, event: FileSystemEvent) -> None:
        # For deleted files, we just remove from pending
        # The manifest will be updated on next full sync
        if event.is_directory:
            return

        path = Path(event.src_path)
        with self.state.lock:
            self.state.pending_files.discard(path)


def process_pending_files(
    state: WatchState,
    skip_vectors: bool,
    table_name: str,
    on_update: Optional[callable] = None,
) -> None:
    """Process all pending files."""
    with state.lock:
        files_to_process = list(state.pending_files)
        state.pending_files.clear()

    if not files_to_process:
        return

    # Load manifest
    manifest = load_manifest(state.docs_dir)
    last_sync = load_last_sync(state.docs_dir) if state.embeddings_enabled else None

    processed_count = 0
    chunks_count = 0
    embeddings_count = 0
    recent = []

    for file_path in files_to_process:
        if not file_path.exists():
            continue

        # Chunk the file
        chunks_data = chunk_file(file_path)
        if not chunks_data:
            continue

        # Save chunks
        chunks_path = save_chunks(chunks_data)
        processed_count += 1
        file_chunks = chunks_data["total_chunks"]
        chunks_count += file_chunks

        # Update manifest
        rel_path = str(file_path.relative_to(state.docs_dir.parent) if state.docs_dir.parent != file_path.parent else file_path)
        file_hash = calculate_file_hash(file_path)

        manifest["files"][rel_path] = {
            "hash": file_hash,
            "chunks_file": str(chunks_path),
            "chunk_count": file_chunks,
            "modified_at": datetime.now().isoformat(),
        }

        status = "chunked"

        # Generate embeddings if enabled
        if state.embeddings_enabled and not skip_vectors and state.api_key:
            for chunk in chunks_data["chunks"]:
                embedding = generate_embedding(chunk["content"], state.api_key)
                if embedding:
                    embeddings_count += 1

            # Update sync state
            if last_sync:
                last_sync["files"][rel_path] = {
                    "hash": file_hash,
                    "chunk_count": file_chunks,
                    "synced_at": datetime.now().isoformat(),
                }
            status = "synced"

        # Track recent file
        try:
            display_path = str(file_path.relative_to(state.docs_dir))
        except ValueError:
            display_path = file_path.name
        recent.append((display_path, file_chunks, status))

    # Save manifest
    manifest["last_run"] = datetime.now().isoformat()
    save_manifest(state.docs_dir, manifest)

    # Save sync state if embeddings were generated
    if last_sync and embeddings_count > 0:
        last_sync["synced_at"] = datetime.now().isoformat()
        save_last_sync(state.docs_dir, last_sync)

    # Update state
    with state.lock:
        state.last_process_time = datetime.now()
        state.total_files += processed_count
        state.total_chunks += chunks_count
        state.total_embeddings += embeddings_count

        # Keep only last 5 recent files
        state.recent_files = (recent + state.recent_files)[:5]

    if on_update:
        on_update()


def create_status_panel(state: WatchState, skip_vectors: bool) -> Panel:
    """Create a Rich panel showing watcher status."""
    lines = []

    # Watching status
    lines.append(f"[bold cyan]Watching[/bold cyan] {state.docs_dir}/")
    lines.append("")

    # Last update time
    if state.last_process_time:
        time_str = state.last_process_time.strftime("%H:%M:%S")
        lines.append(f"[dim]Last update:[/dim] {time_str}")
    else:
        lines.append("[dim]Waiting for changes...[/dim]")

    # Stats
    stats_parts = [f"Files: {state.total_files}"]
    stats_parts.append(f"Chunks: {state.total_chunks}")
    if state.embeddings_enabled and not skip_vectors:
        stats_parts.append(f"Embeddings: {state.total_embeddings}")
    lines.append(" | ".join(stats_parts))
    lines.append("")

    # Embeddings status
    if skip_vectors:
        lines.append("[yellow]Embeddings: disabled (--skip-vectors)[/yellow]")
    elif state.embeddings_enabled:
        lines.append("[green]Embeddings: enabled[/green]")
    else:
        lines.append("[yellow]Embeddings: disabled (no API key)[/yellow]")
    lines.append("")

    # Recent files
    if state.recent_files:
        lines.append("[bold]Recent:[/bold]")
        for path, chunks, status in state.recent_files:
            if status == "synced":
                icon = "[green]✓[/green]"
            else:
                icon = "[blue]○[/blue]"
            lines.append(f"  {icon} {path} ({chunks} chunks)")
    else:
        lines.append("[dim]No files processed yet[/dim]")

    lines.append("")
    lines.append("[dim]Press Ctrl+C to stop[/dim]")

    content = "\n".join(lines)
    return Panel(
        content,
        title="[bold]aidocs watch[/bold]",
        border_style="blue",
    )


def watch_docs(
    docs_dir: Path,
    skip_vectors: bool = False,
    debounce_seconds: float = 2.0,
    table_name: str = "doc_embeddings",
) -> None:
    """Watch a documentation directory for changes and auto-sync.

    Args:
        docs_dir: Directory to watch
        skip_vectors: Skip embedding generation
        debounce_seconds: Wait time after last change before processing
        table_name: PostgreSQL table name for embeddings
    """
    state = WatchState(docs_dir)

    # Check for API key
    api_key = get_openai_api_key()
    if api_key and not skip_vectors:
        state.api_key = api_key
        state.embeddings_enabled = True

    # Count existing files and chunks
    manifest = load_manifest(docs_dir)
    state.total_files = len(manifest.get("files", {}))
    state.total_chunks = sum(
        f.get("chunk_count", 0) for f in manifest.get("files", {}).values()
    )

    # Create Live display
    live_update_event = threading.Event()

    def on_update():
        live_update_event.set()

    def do_process():
        process_pending_files(state, skip_vectors, table_name, on_update)

    # Set up file watcher
    event_handler = MarkdownEventHandler(state, debounce_seconds, do_process)
    observer = Observer()
    observer.schedule(event_handler, str(docs_dir), recursive=True)
    observer.start()

    try:
        with Live(
            create_status_panel(state, skip_vectors),
            console=console,
            refresh_per_second=1,
        ) as live:
            while True:
                # Wait for update or timeout
                live_update_event.wait(timeout=1.0)
                live_update_event.clear()

                # Update display
                live.update(create_status_panel(state, skip_vectors))

    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping watcher...[/yellow]")
    finally:
        observer.stop()
        observer.join()

    console.print("[green]Watcher stopped.[/green]")
