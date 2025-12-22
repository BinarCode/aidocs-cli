"""Markdown chunking utilities for vector DB import."""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def calculate_file_hash(path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return f"sha256:{sha256.hexdigest()[:16]}"


def parse_markdown_headings(content: str) -> list[dict]:
    """Parse markdown content and extract heading structure.

    Returns list of headings with their level and position.
    """
    headings = []
    lines = content.split("\n")

    for i, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append({
                "level": level,
                "title": title,
                "line": i,
            })

    return headings


def get_hierarchy(headings: list[dict], current_index: int) -> list[str]:
    """Get the hierarchy context for a heading (parent headings)."""
    if current_index < 0 or current_index >= len(headings):
        return []

    current = headings[current_index]
    hierarchy = [current["title"]]

    # Look backwards for parent headings
    for i in range(current_index - 1, -1, -1):
        if headings[i]["level"] < current["level"]:
            hierarchy.insert(0, headings[i]["title"])
            current = headings[i]

    return hierarchy


def split_by_headings(content: str, split_level: int = 2) -> list[dict]:
    """Split markdown content into chunks at the specified heading level.

    Args:
        content: Markdown content
        split_level: Heading level to split at (default: 2 for ##)

    Returns:
        List of chunks with title, content, hierarchy, and metadata.
    """
    headings = parse_markdown_headings(content)
    lines = content.split("\n")
    chunks = []

    if not headings:
        # No headings - return entire content as single chunk
        return [{
            "chunk_index": 0,
            "title": "Content",
            "hierarchy": [],
            "content": content.strip(),
            "char_count": len(content),
            "metadata": {
                "headings": [],
                "has_code": "```" in content,
                "has_images": "![" in content,
            }
        }]

    # Find split points (headings at the specified level)
    split_indices = [i for i, h in enumerate(headings) if h["level"] == split_level]

    if not split_indices:
        # No headings at split level - return entire content as single chunk
        return [{
            "chunk_index": 0,
            "title": headings[0]["title"] if headings else "Content",
            "hierarchy": [headings[0]["title"]] if headings else [],
            "content": content.strip(),
            "char_count": len(content),
            "metadata": {
                "headings": [f"{'#' * h['level']} {h['title']}" for h in headings],
                "has_code": "```" in content,
                "has_images": "![" in content,
            }
        }]

    # Extract content before first split heading (if any)
    first_split_line = headings[split_indices[0]]["line"]
    if first_split_line > 0:
        intro_content = "\n".join(lines[:first_split_line]).strip()
        if intro_content:
            # Find the title (first H1 if exists)
            intro_title = "Introduction"
            for h in headings:
                if h["line"] < first_split_line and h["level"] == 1:
                    intro_title = h["title"]
                    break

            chunks.append({
                "chunk_index": 0,
                "title": intro_title,
                "hierarchy": [intro_title],
                "content": intro_content,
                "char_count": len(intro_content),
                "metadata": {
                    "headings": [f"{'#' * h['level']} {h['title']}"
                                for h in headings if h["line"] < first_split_line],
                    "has_code": "```" in intro_content,
                    "has_images": "![" in intro_content,
                }
            })

    # Extract content for each split heading
    for i, split_idx in enumerate(split_indices):
        heading = headings[split_idx]
        start_line = heading["line"]

        # Find end line (next split heading or end of file)
        if i + 1 < len(split_indices):
            end_line = headings[split_indices[i + 1]]["line"]
        else:
            end_line = len(lines)

        chunk_content = "\n".join(lines[start_line:end_line]).strip()
        hierarchy = get_hierarchy(headings, split_idx)

        # Find nested headings within this chunk
        nested_headings = [
            f"{'#' * h['level']} {h['title']}"
            for h in headings
            if start_line <= h["line"] < end_line
        ]

        chunks.append({
            "chunk_index": len(chunks),
            "title": heading["title"],
            "hierarchy": hierarchy,
            "content": chunk_content,
            "char_count": len(chunk_content),
            "metadata": {
                "headings": nested_headings,
                "has_code": "```" in chunk_content,
                "has_images": "![" in chunk_content,
            }
        })

    return chunks


def chunk_file(path: Path) -> Optional[dict]:
    """Process a single markdown file and return chunk data.

    Args:
        path: Path to the markdown file

    Returns:
        Dict with file info and chunks, or None if file is empty/invalid.
    """
    if not path.exists() or not path.is_file():
        return None

    if path.suffix.lower() != ".md":
        return None

    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return None

    if not content.strip():
        return None

    file_hash = calculate_file_hash(path)
    chunks = split_by_headings(content)

    return {
        "file_path": str(path),
        "file_hash": file_hash,
        "chunked_at": datetime.now(timezone.utc).isoformat(),
        "total_chunks": len(chunks),
        "chunks": chunks,
    }


def load_manifest(docs_dir: Path) -> dict:
    """Load the chunks manifest file."""
    manifest_path = docs_dir / ".chunks" / "manifest.json"

    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    return {
        "version": "1.0",
        "last_run": None,
        "files": {},
    }


def save_manifest(docs_dir: Path, manifest: dict) -> None:
    """Save the chunks manifest file."""
    chunks_dir = docs_dir / ".chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = chunks_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )


def get_chunks_path(md_path: Path) -> Path:
    """Get the path for the chunks JSON file corresponding to a markdown file."""
    return md_path.with_suffix(".chunks.json")


def save_chunks(chunks_data: dict) -> Path:
    """Save chunks data to a JSON file alongside the markdown file."""
    md_path = Path(chunks_data["file_path"])
    chunks_path = get_chunks_path(md_path)

    chunks_path.write_text(
        json.dumps(chunks_data, indent=2),
        encoding="utf-8",
    )

    return chunks_path


def chunk_directory(
    docs_dir: Path,
    force: bool = False,
    dry: bool = False,
) -> dict:
    """Process all markdown files in a directory.

    Args:
        docs_dir: Directory to process
        force: Re-chunk all files regardless of hash
        dry: Preview only, don't write files

    Returns:
        Summary dict with stats and file list.
    """
    manifest = load_manifest(docs_dir)

    # Find all markdown files (excluding hidden dirs and .knowledge)
    md_files = []
    for md_file in docs_dir.rglob("*.md"):
        # Skip hidden directories and .knowledge
        parts = md_file.relative_to(docs_dir).parts
        if any(p.startswith(".") for p in parts):
            continue
        md_files.append(md_file)

    stats = {
        "total_files": len(md_files),
        "processed": 0,
        "skipped": 0,
        "chunks_created": 0,
        "files": [],
    }

    for md_file in sorted(md_files):
        rel_path = str(md_file.relative_to(docs_dir.parent) if docs_dir.parent != md_file.parent else md_file)
        current_hash = calculate_file_hash(md_file)

        # Check if file changed
        cached = manifest["files"].get(rel_path)
        if not force and cached and cached.get("hash") == current_hash:
            stats["skipped"] += 1
            stats["files"].append({
                "path": rel_path,
                "status": "unchanged",
                "chunks": cached.get("chunk_count", 0),
            })
            continue

        # Chunk the file
        chunks_data = chunk_file(md_file)
        if not chunks_data:
            continue

        if not dry:
            chunks_path = save_chunks(chunks_data)

            # Update manifest
            manifest["files"][rel_path] = {
                "hash": current_hash,
                "chunks_file": str(chunks_path),
                "chunk_count": chunks_data["total_chunks"],
                "modified_at": datetime.now(timezone.utc).isoformat(),
            }

        stats["processed"] += 1
        stats["chunks_created"] += chunks_data["total_chunks"]
        stats["files"].append({
            "path": rel_path,
            "status": "new" if not cached else "updated",
            "chunks": chunks_data["total_chunks"],
        })

    if not dry:
        manifest["last_run"] = datetime.now(timezone.utc).isoformat()
        save_manifest(docs_dir, manifest)

    return stats
