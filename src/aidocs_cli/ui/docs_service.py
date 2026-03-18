"""File operations for the docs editor."""

from __future__ import annotations

import re
from pathlib import Path


def list_docs(docs_dir: Path) -> list[dict]:
    """Walk docs directory and return list of markdown files with published status."""
    files: list[dict] = []
    _walk_directory(docs_dir, docs_dir, files)
    return files


def _walk_directory(root: Path, current: Path, files: list[dict]) -> None:
    if not current.is_dir():
        return

    for item in sorted(current.iterdir()):
        if item.is_file() and item.suffix == ".md":
            relative = str(item.relative_to(root))
            content = item.read_text(encoding="utf-8")
            published = False
            m = re.match(r"\A---\s*\n(.+?)\n---", content, re.DOTALL)
            if m:
                published = bool(re.search(r"^published:\s*true\s*$", m.group(1), re.MULTILINE))
            files.append({
                "path": relative,
                "name": item.name,
                "published": published,
            })
        elif item.is_dir() and not item.name.startswith((".", "_")):
            _walk_directory(root, item, files)


def get_file_content(docs_dir: Path, relative_path: str) -> str:
    """Read a markdown file and return its content."""
    full_path = docs_dir / relative_path
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {relative_path}")
    return full_path.read_text(encoding="utf-8")


def write_file(docs_dir: Path, relative_path: str, content: str) -> None:
    """Write content to a markdown file, creating directories as needed."""
    full_path = docs_dir / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")


def list_folders(docs_dir: Path) -> list[str]:
    """List all folder paths under docs_dir (including root)."""
    folders = [""]
    _walk_folders(docs_dir, docs_dir, folders)
    folders.sort()
    return folders


def _walk_folders(root: Path, current: Path, folders: list[str]) -> None:
    if not current.is_dir():
        return
    for item in sorted(current.iterdir()):
        if item.is_dir() and not item.name.startswith((".", "_")):
            relative = str(item.relative_to(root))
            folders.append(relative)
            _walk_folders(root, item, folders)


def parse_frontmatter(raw: str) -> dict:
    """Parse YAML frontmatter from markdown content."""
    if not raw.strip().startswith("---"):
        return {"meta": {}, "body": raw}

    parts = re.split(r"^---\s*$", raw, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        return {"meta": {}, "body": raw}

    meta: dict = {}
    for line in parts[1].strip().splitlines():
        m = re.match(r'^(\w+):\s*"?(.+?)"?\s*$', line)
        if m:
            key, value = m.group(1), m.group(2)
            if value == "true":
                value = True
            elif value == "false":
                value = False
            meta[key] = value

    return {"meta": meta, "body": parts[2].lstrip("\n")}


def build_markdown(meta: dict, body: str) -> str:
    """Build markdown content with YAML frontmatter."""
    if not meta:
        return body

    lines = ["---"]
    for key, value in meta.items():
        if isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        else:
            lines.append(f'{key}: "{value}"')
    lines.append("---")
    lines.append("")

    return "\n".join(lines) + "\n" + body
