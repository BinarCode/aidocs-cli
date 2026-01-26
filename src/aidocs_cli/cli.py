"""CLI commands for aidocs."""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from . import __version__
from .chunker import chunk_directory
from .coverage import analyze_coverage, save_coverage_report, CoverageReport
from .embeddings import generate_sync_sql, get_openai_api_key
from .installer import check_tools, install_docs_module
from .pdf_exporter import export_markdown_to_pdf
from .server import generate_mkdocs_config, validate_docs_directory, write_mkdocs_config

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"aidocs version {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="aidocs",
    help="AI-powered documentation generator for web applications.",
    no_args_is_help=True,
)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """AI-powered documentation generator for web applications."""
    pass


@app.command()
def init(
    project_name: Optional[str] = typer.Argument(
        None,
        help="Project name or path. Use '.' for current directory.",
    ),
    ai: str = typer.Option(
        "claude",
        "--ai",
        help="AI assistant to configure for (claude, cursor, copilot).",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files.",
    ),
    no_git: bool = typer.Option(
        False,
        "--no-git",
        help="Skip git initialization.",
    ),
) -> None:
    """Initialize docs module in a project.

    Examples:
        aidocs init .              # Current directory
        aidocs init my-project     # New directory
        aidocs init . --force      # Overwrite existing
    """
    if project_name is None or project_name == ".":
        target_dir = Path.cwd()
        console.print(f"[blue]Initializing docs module in current directory...[/blue]")
    else:
        target_dir = Path.cwd() / project_name
        if not target_dir.exists():
            target_dir.mkdir(parents=True)
            console.print(f"[blue]Created directory: {project_name}[/blue]")
        console.print(f"[blue]Initializing docs module in {project_name}...[/blue]")

    try:
        install_docs_module(target_dir, ai=ai, force=force, no_git=no_git)

        console.print()
        console.print(Panel.fit(
            "[green]Docs module installed successfully![/green]\n\n"
            "[bold]Next steps:[/bold]\n"
            "1. Run [cyan]/docs:init[/cyan] in Claude Code to configure your project\n"
            "2. Run [cyan]/docs:generate <url>[/cyan] to document a page\n\n"
            "[dim]Requires Playwright MCP for browser automation.[/dim]",
            title="Success",
            border_style="green",
        ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def check() -> None:
    """Check for required tools and dependencies."""
    console.print("[blue]Checking environment...[/blue]")
    console.print()

    results = check_tools()

    all_passed = all(results.values())

    console.print()
    if all_passed:
        console.print(Panel.fit(
            "[green]All checks passed![/green]\n\n"
            "You're ready to use aidocs.",
            title="Environment Check",
            border_style="green",
        ))
    else:
        console.print(Panel.fit(
            "[yellow]Some checks failed.[/yellow]\n\n"
            "Install missing tools to use all features.",
            title="Environment Check",
            border_style="yellow",
        ))


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"aidocs version {__version__}")


GITHUB_REPO = "git+https://github.com/BinarCode/aidocs-cli.git"


@app.command()
def update(
    github: bool = typer.Option(
        False,
        "--github",
        help="Install latest from GitHub instead of PyPI.",
    ),
) -> None:
    """Update aidocs to the latest version.

    Examples:
        aidocs update              # Update from PyPI
        aidocs update --github     # Update from GitHub (latest)
    """
    console.print(f"[blue]Current version: {__version__}[/blue]")
    source = "GitHub" if github else "PyPI"
    console.print(f"[blue]Updating from {source}...[/blue]")
    console.print()

    uv_path = shutil.which("uv")
    pipx_path = shutil.which("pipx")

    if github:
        if uv_path:
            console.print("[dim]Using uv to install from GitHub...[/dim]")
            cmd = ["uv", "tool", "install", "--force", "aidocs", "--from", GITHUB_REPO]
        elif pipx_path:
            console.print("[dim]Using pipx to install from GitHub...[/dim]")
            cmd = ["pipx", "install", "--force", GITHUB_REPO]
        else:
            console.print("[dim]Using pip to install from GitHub...[/dim]")
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", GITHUB_REPO]
    else:
        if uv_path:
            console.print("[dim]Using uv to update...[/dim]")
            cmd = ["uv", "tool", "upgrade", "aidocs"]
        elif pipx_path:
            console.print("[dim]Using pipx to update...[/dim]")
            cmd = ["pipx", "upgrade", "aidocs"]
        else:
            console.print("[dim]Using pip to update...[/dim]")
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "aidocs"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            console.print()
            console.print(Panel.fit(
                "[green]aidocs updated successfully![/green]\n\n"
                f"[dim]{result.stdout.strip() if result.stdout.strip() else 'Up to date'}[/dim]",
                title="Update Complete",
                border_style="green",
            ))
        else:
            console.print(f"[yellow]Update output:[/yellow]")
            if result.stdout:
                console.print(result.stdout)
            if result.stderr:
                console.print(f"[red]{result.stderr}[/red]")

            if "already" in result.stderr.lower() or "no updates" in result.stderr.lower():
                console.print("[green]Already at the latest version![/green]")
            else:
                raise typer.Exit(1)

    except FileNotFoundError:
        console.print("[red]Error: Could not find package manager.[/red]")
        console.print("Try running manually:")
        if github:
            console.print(f"  [cyan]uv tool install aidocs --from {GITHUB_REPO}[/cyan]")
        else:
            console.print("  [cyan]uv tool upgrade aidocs[/cyan]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error updating: {e}[/red]")
        raise typer.Exit(1)


@app.command("rag-chunks")
def rag_chunks(
    docs_dir: Optional[str] = typer.Argument(
        "docs",
        help="Directory containing markdown files to chunk.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Re-chunk all files (ignore manifest cache).",
    ),
    dry: bool = typer.Option(
        False,
        "--dry",
        help="Preview what would be chunked without writing files.",
    ),
) -> None:
    """Chunk markdown files for vector DB import.

    Splits markdown files at ## headings and creates .chunks.json files
    alongside each .md file. Tracks changes via manifest.json.

    Examples:
        aidocs rag-chunks                  # Chunk all files in docs/
        aidocs rag-chunks docs/users       # Chunk specific directory
        aidocs rag-chunks --force          # Re-chunk all files
        aidocs rag-chunks --dry            # Preview only
    """
    target_dir = Path(docs_dir)

    if not target_dir.exists():
        console.print(f"[red]Error: Directory not found: {docs_dir}[/red]")
        raise typer.Exit(1)

    if not target_dir.is_dir():
        console.print(f"[red]Error: Not a directory: {docs_dir}[/red]")
        raise typer.Exit(1)

    mode = "[yellow]DRY RUN[/yellow] - " if dry else ""
    console.print(f"{mode}[blue]Chunking markdown files in {docs_dir}...[/blue]")
    console.print()

    try:
        stats = chunk_directory(target_dir, force=force, dry=dry)

        # Display results
        for file_info in stats["files"]:
            status = file_info["status"]
            path = file_info["path"]
            chunks = file_info["chunks"]

            if status == "unchanged":
                console.print(f"  [dim]○ {path} (unchanged)[/dim]")
            elif status == "new":
                console.print(f"  [green]+ {path}[/green] ({chunks} chunks)")
            else:
                console.print(f"  [yellow]↻ {path}[/yellow] ({chunks} chunks)")

        console.print()

        if dry:
            console.print(Panel.fit(
                f"[yellow]DRY RUN - No files written[/yellow]\n\n"
                f"Would process: {stats['processed']} files\n"
                f"Would skip: {stats['skipped']} unchanged files\n"
                f"Would create: {stats['chunks_created']} chunks\n\n"
                f"[dim]Run without --dry to create chunk files.[/dim]",
                title="Preview",
                border_style="yellow",
            ))
        else:
            console.print(Panel.fit(
                f"[green]Chunking complete![/green]\n\n"
                f"Processed: {stats['processed']} files\n"
                f"Skipped: {stats['skipped']} unchanged files\n"
                f"Created: {stats['chunks_created']} chunks\n\n"
                f"[dim]Manifest saved to {docs_dir}/.chunks/manifest.json[/dim]\n"
                f"[dim]Run [cyan]aidocs rag-vectors[/cyan] to generate embeddings.[/dim]",
                title="Success",
                border_style="green",
            ))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("rag-vectors")
def rag_vectors(
    docs_dir: Optional[str] = typer.Argument(
        "docs",
        help="Directory containing chunked documentation.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Re-sync all files (ignore last sync state).",
    ),
    dry: bool = typer.Option(
        False,
        "--dry",
        help="Preview what would be synced without generating embeddings.",
    ),
    table: str = typer.Option(
        "doc_embeddings",
        "--table",
        "-t",
        help="Target table name in PostgreSQL.",
    ),
) -> None:
    """Generate embeddings and SQL for vector DB import.

    Reads chunk files, calls OpenAI API to generate embeddings,
    and creates a SQL file for importing into PostgreSQL with pgvector.

    Requires OPENAI_API_KEY environment variable.

    Examples:
        aidocs rag-vectors                  # Generate embeddings and SQL
        aidocs rag-vectors --dry            # Preview only
        aidocs rag-vectors --force          # Re-sync all files
        aidocs rag-vectors --table my_docs  # Custom table name
    """
    target_dir = Path(docs_dir)

    if not target_dir.exists():
        console.print(f"[red]Error: Directory not found: {docs_dir}[/red]")
        raise typer.Exit(1)

    # Check for API key (unless dry run)
    if not dry and not get_openai_api_key():
        console.print(Panel.fit(
            "[red]OPENAI_API_KEY not set[/red]\n\n"
            "Set the environment variable:\n"
            "  [cyan]export OPENAI_API_KEY=sk-...[/cyan]\n\n"
            "Or run with [cyan]--dry[/cyan] to preview.",
            title="Error",
            border_style="red",
        ))
        raise typer.Exit(1)

    mode = "[yellow]DRY RUN[/yellow] - " if dry else ""
    console.print(f"{mode}[blue]Generating embeddings for {docs_dir}...[/blue]")
    console.print()

    # Progress callback
    def on_progress(current: int, total: int, message: str) -> None:
        console.print(f"  [{current + 1}/{total}] {message}")

    def on_status(message: str) -> None:
        console.print(f"[dim]{message}[/dim]")

    try:
        result = generate_sync_sql(
            target_dir,
            force=force,
            dry=dry,
            table_name=table,
            on_progress=on_progress if not dry else None,
            on_status=on_status,
        )

        if not result["success"]:
            console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
            raise typer.Exit(1)

        stats = result["stats"]
        console.print()

        if dry:
            console.print(Panel.fit(
                f"[yellow]DRY RUN - No embeddings generated[/yellow]\n\n"
                f"Unchanged: {stats.get('unchanged', 0)} files (would skip)\n"
                f"To sync: {stats.get('to_sync', 0)} files\n"
                f"To delete: {stats.get('to_delete', 0)} files\n"
                f"Total chunks: {stats.get('total_chunks', 0)}\n\n"
                f"Estimated cost: ${stats.get('estimated_cost', 0):.4f}\n\n"
                f"[dim]Run without --dry to generate embeddings.[/dim]",
                title="Preview",
                border_style="yellow",
            ))
        elif result.get("message"):
            console.print(Panel.fit(
                f"[green]{result['message']}[/green]",
                title="Up to Date",
                border_style="green",
            ))
        else:
            sql_file = result.get("sql_file", f"{docs_dir}/.chunks/sync.sql")
            console.print(Panel.fit(
                f"[green]Embeddings generated![/green]\n\n"
                f"Files synced: {stats.get('to_sync', 0)}\n"
                f"Files deleted: {stats.get('to_delete', 0)}\n"
                f"Embeddings: {stats.get('embeddings_generated', 0)}\n"
                f"Tokens used: ~{stats.get('tokens_used', 0):,}\n\n"
                f"[bold]SQL file:[/bold] {sql_file}\n\n"
                f"[dim]Import to database:[/dim]\n"
                f"  [cyan]psql $DATABASE_URL -f {sql_file}[/cyan]",
                title="Success",
                border_style="green",
            ))

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("rag")
def rag(
    docs_dir: Optional[str] = typer.Argument(
        "docs",
        help="Directory containing documentation.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Re-chunk and re-sync all files.",
    ),
    dry: bool = typer.Option(
        False,
        "--dry",
        help="Preview what would happen without making changes.",
    ),
    table: str = typer.Option(
        "doc_embeddings",
        "--table",
        "-t",
        help="Target table name in PostgreSQL.",
    ),
    skip_vectors: bool = typer.Option(
        False,
        "--skip-vectors",
        help="Only chunk files, skip embedding generation.",
    ),
) -> None:
    """Prepare documentation for RAG: chunk and generate embeddings.

    Combines rag-chunks and rag-vectors into a single command.
    Perfect for preparing docs before starting the MCP server.

    Examples:
        aidocs rag                      # Chunk and generate embeddings
        aidocs rag --dry                # Preview only
        aidocs rag --force              # Re-process everything
        aidocs rag --skip-vectors       # Only chunk, no embeddings
    """
    target_dir = Path(docs_dir)

    if not target_dir.exists():
        console.print(f"[red]Error: Directory not found: {docs_dir}[/red]")
        raise typer.Exit(1)

    mode = "[yellow]DRY RUN[/yellow] - " if dry else ""

    # Step 1: Chunk files
    console.print(f"{mode}[blue]Step 1/2: Chunking markdown files...[/blue]")
    console.print()

    try:
        stats = chunk_directory(target_dir, force=force, dry=dry)

        if dry:
            for f in stats["files"]:
                status_icon = {"new": "+", "updated": "~", "unchanged": " "}
                icon = status_icon.get(f["status"], "?")
                console.print(f"  [{icon}] {f['path']} ({f['chunks']} chunks)")
            console.print()
            console.print(f"  [dim]Would process: {stats['processed']} files[/dim]")
            console.print(f"  [dim]Would skip: {stats['skipped']} unchanged files[/dim]")
        else:
            console.print(f"  [green]Processed:[/green] {stats['processed']} files")
            console.print(f"  [dim]Skipped:[/dim] {stats['skipped']} unchanged files")
            console.print(f"  [green]Created:[/green] {stats['chunks_created']} chunks")

        console.print()

    except Exception as e:
        console.print(f"[red]Error chunking: {e}[/red]")
        raise typer.Exit(1)

    # Step 2: Generate embeddings (unless skipped)
    if skip_vectors:
        console.print(f"[dim]Step 2/2: Skipped (--skip-vectors)[/dim]")
        console.print()
        console.print(Panel.fit(
            f"[green]Chunking complete![/green]\n\n"
            f"Chunks created: {stats['chunks_created']}\n\n"
            f"[dim]Run [cyan]aidocs rag-vectors[/cyan] to generate embeddings.[/dim]\n"
            f"[dim]Or run [cyan]aidocs mcp {docs_dir}[/cyan] to start MCP server.[/dim]",
            title="Success",
            border_style="green",
        ))
        return

    # Check for API key
    if not dry and not get_openai_api_key():
        console.print(Panel.fit(
            "[yellow]Chunking complete, but OPENAI_API_KEY not set[/yellow]\n\n"
            f"Chunks created: {stats['chunks_created']}\n\n"
            "To generate embeddings, set the environment variable:\n"
            "  [cyan]export OPENAI_API_KEY=sk-...[/cyan]\n\n"
            f"Or start MCP server without embeddings:\n"
            f"  [cyan]aidocs mcp {docs_dir}[/cyan]",
            title="Partial Success",
            border_style="yellow",
        ))
        return

    console.print(f"{mode}[blue]Step 2/2: Generating embeddings...[/blue]")
    console.print()

    def on_progress(current: int, total: int, message: str) -> None:
        console.print(f"  [{current + 1}/{total}] {message}")

    def on_status(message: str) -> None:
        console.print(f"  [dim]{message}[/dim]")

    try:
        result = generate_sync_sql(
            target_dir,
            force=force,
            dry=dry,
            table_name=table,
            on_progress=on_progress if not dry else None,
            on_status=on_status,
        )

        if not result["success"]:
            console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
            raise typer.Exit(1)

        vec_stats = result["stats"]
        console.print()

        if dry:
            console.print(Panel.fit(
                f"[yellow]DRY RUN - Preview only[/yellow]\n\n"
                f"Chunks: {stats['chunks_created']} (from {stats['processed']} files)\n"
                f"Embeddings to generate: {vec_stats.get('total_chunks', 0)}\n"
                f"Estimated cost: ${vec_stats.get('estimated_cost', 0):.4f}\n\n"
                f"[dim]Run without --dry to execute.[/dim]",
                title="Preview",
                border_style="yellow",
            ))
        elif result.get("message"):
            console.print(Panel.fit(
                f"[green]RAG preparation complete![/green]\n\n"
                f"Chunks: {stats['chunks_created']}\n"
                f"Embeddings: up to date\n\n"
                f"[dim]Start MCP server:[/dim]\n"
                f"  [cyan]aidocs mcp {docs_dir}[/cyan]",
                title="Success",
                border_style="green",
            ))
        else:
            sql_file = result.get("sql_file", f"{docs_dir}/.chunks/sync.sql")
            console.print(Panel.fit(
                f"[green]RAG preparation complete![/green]\n\n"
                f"Chunks: {stats['chunks_created']}\n"
                f"Embeddings: {vec_stats.get('embeddings_generated', 0)}\n"
                f"SQL file: {sql_file}\n\n"
                f"[dim]Import to database:[/dim]\n"
                f"  [cyan]psql $DATABASE_URL -f {sql_file}[/cyan]\n\n"
                f"[dim]Or start MCP server:[/dim]\n"
                f"  [cyan]aidocs mcp {docs_dir}[/cyan]",
                title="Success",
                border_style="green",
            ))

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error generating embeddings: {e}[/red]")
        raise typer.Exit(1)


@app.command("export-pdf")
def export_pdf(
    markdown_file: str = typer.Argument(
        ...,
        help="Path to the markdown file to export.",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output PDF path (default: docs/exports/{name}.pdf).",
    ),
) -> None:
    """Export markdown documentation to PDF.

    Converts a markdown file to a styled PDF with auto-generated
    table of contents. Uses Chrome/Chromium for rendering.

    Examples:
        aidocs export-pdf docs/projects/index.md
        aidocs export-pdf docs/flows/sync-users.md -o manual.pdf
    """
    md_path = Path(markdown_file)
    out_path = Path(output) if output else None

    console.print(f"[blue]Exporting {markdown_file} to PDF...[/blue]")
    console.print()

    def on_status(msg: str) -> None:
        console.print(f"  [dim]{msg}[/dim]")

    try:
        result = export_markdown_to_pdf(md_path, out_path, on_status=on_status)

        if not result["success"]:
            console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
            raise typer.Exit(1)

        stats = result["stats"]
        console.print()
        console.print(Panel.fit(
            f"[green]PDF exported successfully![/green]\n\n"
            f"[bold]Title:[/bold] {stats['title']}\n"
            f"[bold]TOC entries:[/bold] {stats['toc_entries']}\n"
            f"[bold]Size:[/bold] {stats['size_kb']} KB\n\n"
            f"[bold]Output:[/bold] {result['output_path']}\n\n"
            f"[dim]Open with:[/dim]\n"
            f"  [cyan]open {result['output_path']}[/cyan]",
            title="Success",
            border_style="green",
        ))

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def serve(
    docs_dir: Optional[str] = typer.Argument(
        "docs",
        help="Directory containing markdown documentation.",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Port to serve documentation on.",
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="Host to bind to.",
    ),
    open_browser: bool = typer.Option(
        True,
        "--open/--no-open",
        help="Open browser automatically.",
    ),
    build_only: bool = typer.Option(
        False,
        "--build",
        "-b",
        help="Build static site only (no server).",
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for built site (default: docs/_site).",
    ),
) -> None:
    """Serve documentation with live reload using MkDocs Material.

    Examples:
        aidocs serve                    # Serve docs/ on port 8000
        aidocs serve --port 3000        # Custom port
        aidocs serve docs/users         # Serve specific subdirectory
        aidocs serve --build            # Build static site only
        aidocs serve --build -o ./site  # Build to custom output
    """
    import tempfile
    import threading
    import webbrowser

    target_dir = Path(docs_dir)

    is_valid, error_msg = validate_docs_directory(target_dir)
    if not is_valid:
        console.print(Panel.fit(
            f"[red]{error_msg}[/red]",
            title="Error",
            border_style="red",
        ))
        raise typer.Exit(1)

    site_output = Path(output_dir) if output_dir else target_dir / "_site"

    console.print("[blue]Discovering documentation structure...[/blue]")
    mkdocs_config = generate_mkdocs_config(
        target_dir,
        output_dir=site_output if build_only else None,
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        config_path = Path(tmp_dir) / "mkdocs.yml"
        write_mkdocs_config(mkdocs_config, config_path)

        if build_only:
            console.print(f"[blue]Building static site to {site_output}...[/blue]")

            try:
                result = subprocess.run(
                    [sys.executable, "-m", "mkdocs", "build", "-f", str(config_path)],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    console.print()
                    console.print(Panel.fit(
                        f"[green]Site built successfully![/green]\n\n"
                        f"Output: {site_output}\n\n"
                        "[dim]Deploy with any static hosting service.[/dim]",
                        title="Build Complete",
                        border_style="green",
                    ))
                else:
                    console.print("[red]Build failed:[/red]")
                    if result.stderr:
                        console.print(result.stderr)
                    raise typer.Exit(1)

            except FileNotFoundError:
                console.print("[red]Error: Failed to run mkdocs. Try reinstalling aidocs.[/red]")
                raise typer.Exit(1)
        else:
            url = f"http://{host}:{port}"
            console.print()
            console.print(Panel.fit(
                f"[green]Starting documentation server...[/green]\n\n"
                f"URL: [cyan]{url}[/cyan]\n"
                f"Docs: {target_dir}\n\n"
                "[dim]Press Ctrl+C to stop[/dim]",
                title="MkDocs Server",
                border_style="green",
            ))

            try:
                cmd = [
                    sys.executable, "-m", "mkdocs", "serve",
                    "-f", str(config_path),
                    "-a", f"{host}:{port}",
                    "--watch", str(target_dir.resolve()),
                    "--livereload",
                ]

                if open_browser:
                    def open_after_delay() -> None:
                        import time
                        time.sleep(1.5)
                        webbrowser.open(url)
                    threading.Thread(target=open_after_delay, daemon=True).start()

                subprocess.run(cmd)

            except FileNotFoundError:
                console.print("[red]Error: Failed to run mkdocs. Try reinstalling aidocs.[/red]")
                raise typer.Exit(1)
            except KeyboardInterrupt:
                console.print("\n[yellow]Server stopped.[/yellow]")


@app.command("mcp")
def mcp_command(
    docs_dir: str = typer.Argument(
        "docs",
        help="Documentation directory to serve",
    ),
) -> None:
    """Start MCP server to expose documentation via tools.

    Exposes documentation through MCP tools:
    - list_docs: List all documentation files
    - search_docs: Search through documentation by keyword
    - read_doc: Read full content of a file or chunk
    - get_doc_structure: Get heading hierarchy

    Example usage in .mcp.json:
        {
          "mcpServers": {
            "aidocs": {
              "command": "aidocs",
              "args": ["mcp", "docs/"]
            }
          }
        }
    """
    import asyncio

    from .mcp_server import run_server

    target_dir = Path(docs_dir)
    if not target_dir.exists():
        console.print(f"[red]Error: Directory not found: {docs_dir}[/red]")
        raise typer.Exit(1)

    if not target_dir.is_dir():
        console.print(f"[red]Error: Not a directory: {docs_dir}[/red]")
        raise typer.Exit(1)

    asyncio.run(run_server(target_dir))


@app.command("watch")
def watch(
    docs_dir: Optional[str] = typer.Argument(
        "docs",
        help="Directory containing documentation to watch.",
    ),
    with_vectors: bool = typer.Option(
        False,
        "--with-vectors",
        help="Enable embedding generation (requires OPENAI_API_KEY).",
    ),
    debounce: float = typer.Option(
        10.0,
        "--debounce",
        "-d",
        help="Seconds to wait after last change before processing.",
    ),
    table: str = typer.Option(
        "doc_embeddings",
        "--table",
        "-t",
        help="Target table name for embeddings.",
    ),
) -> None:
    """Watch documentation directory and auto-sync on changes.

    Monitors the docs directory for markdown file changes and automatically:
    - Re-chunks modified files
    - Generates embeddings (if --with-vectors and OPENAI_API_KEY is set)
    - Updates manifest and sync state

    Uses debouncing to batch rapid changes (default: 10 seconds).

    Examples:
        aidocs watch                    # Watch docs/, chunk only
        aidocs watch --with-vectors     # Also generate embeddings
        aidocs watch --debounce 5       # Wait 5 seconds before processing
        aidocs watch docs/users         # Watch specific subdirectory
    """
    from .watcher import watch_docs

    target_dir = Path(docs_dir)

    if not target_dir.exists():
        console.print(f"[red]Error: Directory not found: {docs_dir}[/red]")
        raise typer.Exit(1)

    if not target_dir.is_dir():
        console.print(f"[red]Error: Not a directory: {docs_dir}[/red]")
        raise typer.Exit(1)

    try:
        watch_docs(
            target_dir,
            with_vectors=with_vectors,
            debounce_seconds=debounce,
            table_name=table,
        )
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _render_progress_bar(percent: float, width: int = 12) -> str:
    """Render a text-based progress bar."""
    filled = int(width * percent / 100)
    empty = width - filled
    return "█" * filled + "░" * empty


def _get_coverage_color(percent: float) -> str:
    """Get color based on coverage percentage."""
    if percent >= 80:
        return "green"
    elif percent >= 50:
        return "yellow"
    else:
        return "red"


@app.command("coverage")
def coverage(
    docs_dir: Optional[str] = typer.Argument(
        "docs",
        help="Directory containing documentation.",
    ),
    codebase: Optional[str] = typer.Option(
        None,
        "--codebase",
        "-c",
        help="Path to codebase root (default: parent of docs dir).",
    ),
    format_output: str = typer.Option(
        "summary",
        "--format",
        "-f",
        help="Output format: summary, json, or csv.",
    ),
    threshold: Optional[float] = typer.Option(
        None,
        "--threshold",
        "-t",
        help="Minimum coverage percentage (exit 1 if below).",
    ),
    ci: bool = typer.Option(
        False,
        "--ci",
        help="CI mode: exit 1 if coverage below 80%% (shorthand for --threshold 80).",
    ),
    save: bool = typer.Option(
        True,
        "--save/--no-save",
        help="Save report to .chunks/coverage.json.",
    ),
    show_all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show all items (documented and undocumented).",
    ),
) -> None:
    """Analyze documentation coverage for your codebase.

    Scans your codebase for routes, components, and models, then checks
    which items are mentioned in your documentation.

    Examples:
        aidocs coverage                     # Show coverage summary
        aidocs coverage --format json       # Machine-readable output
        aidocs coverage --ci                # Exit 1 if below 80%
        aidocs coverage --threshold 70      # Custom threshold
        aidocs coverage -c ./src            # Specify codebase path
        aidocs coverage --all               # Show all items
    """
    import json as json_module

    target_docs = Path(docs_dir)

    if not target_docs.exists():
        console.print(f"[red]Error: Documentation directory not found: {docs_dir}[/red]")
        raise typer.Exit(1)

    if not target_docs.is_dir():
        console.print(f"[red]Error: Not a directory: {docs_dir}[/red]")
        raise typer.Exit(1)

    # Determine codebase directory
    if codebase:
        codebase_dir = Path(codebase)
    else:
        # Default: parent of docs dir (or current dir if docs is at root)
        codebase_dir = target_docs.parent
        if codebase_dir == target_docs:
            codebase_dir = Path.cwd()

    if not codebase_dir.exists():
        console.print(f"[red]Error: Codebase directory not found: {codebase_dir}[/red]")
        raise typer.Exit(1)

    # Set threshold for CI mode
    effective_threshold = threshold
    if ci and threshold is None:
        effective_threshold = 80.0

    # JSON format - minimal output
    if format_output == "json":
        def on_status(msg: str) -> None:
            pass  # Suppress status messages for JSON output

        try:
            report = analyze_coverage(codebase_dir, target_docs, on_status=on_status)

            if save:
                save_coverage_report(report, target_docs)

            console.print(json_module.dumps(report.to_dict(), indent=2))

            # Check threshold
            if effective_threshold is not None:
                if report.overall_coverage < effective_threshold:
                    raise typer.Exit(1)

        except typer.Exit:
            raise
        except Exception as e:
            error_output = {"success": False, "error": str(e)}
            console.print(json_module.dumps(error_output))
            raise typer.Exit(1)

        return

    # CSV format
    if format_output == "csv":
        def on_status(msg: str) -> None:
            pass

        try:
            report = analyze_coverage(codebase_dir, target_docs, on_status=on_status)

            if save:
                save_coverage_report(report, target_docs)

            # Print CSV header
            console.print("category,name,file,line,documented")

            for cat_name, category in report.categories.items():
                for item in category.items:
                    doc_status = "yes" if item.documented else "no"
                    # Escape commas in names/paths
                    name = f'"{item.name}"' if "," in item.name else item.name
                    file_path = f'"{item.file_path}"' if "," in item.file_path else item.file_path
                    console.print(f"{cat_name},{name},{file_path},{item.line_number},{doc_status}")

            # Check threshold
            if effective_threshold is not None:
                if report.overall_coverage < effective_threshold:
                    raise typer.Exit(1)

        except typer.Exit:
            raise
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

        return

    # Summary format (default) - rich output
    console.print("[blue]Analyzing documentation coverage...[/blue]")
    console.print()

    def on_status(msg: str) -> None:
        console.print(f"  [dim]{msg}[/dim]")

    try:
        report = analyze_coverage(codebase_dir, target_docs, on_status=on_status)
        console.print()

        if save:
            report_path = save_coverage_report(report, target_docs)

        # Check if we found anything
        if not report.categories:
            console.print(Panel.fit(
                "[yellow]No documentable items found in codebase[/yellow]\n\n"
                f"Searched: {codebase_dir}\n\n"
                "[dim]Ensure the codebase path is correct and contains\n"
                "routes, components, or models.[/dim]",
                title="Coverage Analysis",
                border_style="yellow",
            ))
            return

        # Build summary output
        summary_lines = []
        overall_color = _get_coverage_color(report.overall_coverage)

        for cat_name, category in report.categories.items():
            color = _get_coverage_color(category.coverage_percent)
            bar = _render_progress_bar(category.coverage_percent)
            percent = f"{category.coverage_percent:.0f}%"
            ratio = f"{category.documented}/{category.total}"

            # Pad category name for alignment
            display_name = category.name + ":"
            summary_lines.append(
                f"  [{color}]{display_name:<12}[/{color}] {ratio:>6}  ({percent:>4})  {bar}"
            )

        summary_text = "\n".join(summary_lines)

        # Overall coverage line
        overall_bar = _render_progress_bar(report.overall_coverage)
        overall_text = (
            f"\n  [bold]Overall:[/bold]     "
            f"{report.total_documented}/{report.total_items}  "
            f"([{overall_color}]{report.overall_coverage:.0f}%[/{overall_color}])  {overall_bar}"
        )

        console.print(Panel.fit(
            f"[bold]Documentation Coverage Report[/bold]\n"
            f"{'─' * 45}\n\n"
            f"{summary_text}\n"
            f"{overall_text}",
            border_style=overall_color,
        ))

        # Show undocumented items
        has_undocumented = any(cat.undocumented for cat in report.categories.values())

        if has_undocumented:
            console.print()
            console.print("[bold]Missing documentation:[/bold]")

            for cat_name, category in report.categories.items():
                if category.undocumented:
                    console.print(f"\n  [dim]{category.name}:[/dim]")
                    # Show up to 10 items per category
                    items_to_show = category.undocumented[:10]
                    for item in items_to_show:
                        console.print(f"    [red]✗[/red] {item.name}")
                        console.print(f"      [dim]{item.file_path}:{item.line_number}[/dim]")

                    remaining = len(category.undocumented) - 10
                    if remaining > 0:
                        console.print(f"    [dim]... and {remaining} more[/dim]")

        # Show all items if requested
        if show_all:
            console.print()
            console.print("[bold]All items:[/bold]")

            for cat_name, category in report.categories.items():
                console.print(f"\n  [dim]{category.name}:[/dim]")
                for item in category.items:
                    icon = "[green]✓[/green]" if item.documented else "[red]✗[/red]"
                    console.print(f"    {icon} {item.name}")
                    console.print(f"      [dim]{item.file_path}:{item.line_number}[/dim]")

        # Show where report was saved
        if save:
            console.print()
            console.print(f"[dim]Report saved to: {report_path}[/dim]")

        # Check threshold
        if effective_threshold is not None:
            console.print()
            if report.overall_coverage >= effective_threshold:
                console.print(
                    f"[green]✓ Coverage {report.overall_coverage:.1f}% "
                    f"meets threshold of {effective_threshold}%[/green]"
                )
            else:
                console.print(
                    f"[red]✗ Coverage {report.overall_coverage:.1f}% "
                    f"is below threshold of {effective_threshold}%[/red]"
                )
                raise typer.Exit(1)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
