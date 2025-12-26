"""MCP server for exposing documentation via tools."""

import json
import re
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .chunker import chunk_file, parse_markdown_headings


def load_chunks_for_file(md_path: Path) -> dict | None:
    """Load chunks for a markdown file (from .chunks.json or generate on-the-fly)."""
    chunks_path = md_path.with_suffix(".chunks.json")

    if chunks_path.exists():
        try:
            return json.loads(chunks_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    return chunk_file(md_path)


def find_markdown_files(docs_dir: Path) -> list[Path]:
    """Find all markdown files in docs directory."""
    md_files = []
    for md_file in docs_dir.rglob("*.md"):
        parts = md_file.relative_to(docs_dir).parts
        if any(p.startswith(".") for p in parts):
            continue
        md_files.append(md_file)
    return sorted(md_files)


def search_chunks(docs_dir: Path, query: str, limit: int = 10) -> list[dict]:
    """Search through all chunks for matching content."""
    query_lower = query.lower()
    query_terms = query_lower.split()
    results = []

    for md_file in find_markdown_files(docs_dir):
        chunks_data = load_chunks_for_file(md_file)
        if not chunks_data:
            continue

        rel_path = str(md_file.relative_to(docs_dir))

        for chunk in chunks_data.get("chunks", []):
            content_lower = chunk.get("content", "").lower()
            title_lower = chunk.get("title", "").lower()

            score = 0
            for term in query_terms:
                title_matches = title_lower.count(term)
                content_matches = content_lower.count(term)
                score += (title_matches * 3) + content_matches

            if score > 0:
                content = chunk.get("content", "")
                preview = content[:300] + "..." if len(content) > 300 else content

                results.append({
                    "file_path": rel_path,
                    "chunk_index": chunk.get("chunk_index", 0),
                    "title": chunk.get("title", "Untitled"),
                    "hierarchy": chunk.get("hierarchy", []),
                    "content_preview": preview,
                    "score": score,
                })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def get_doc_structure(docs_dir: Path, file_path: str | None = None) -> dict:
    """Get the hierarchical structure of documentation."""
    if file_path:
        md_path = docs_dir / file_path
        if not md_path.exists():
            return {"error": f"File not found: {file_path}"}

        content = md_path.read_text(encoding="utf-8")
        headings = parse_markdown_headings(content)

        return {
            "file_path": file_path,
            "headings": [
                {"level": h["level"], "title": h["title"], "line": h["line"]}
                for h in headings
            ],
        }

    structure = {"files": []}
    for md_file in find_markdown_files(docs_dir):
        rel_path = str(md_file.relative_to(docs_dir))
        content = md_file.read_text(encoding="utf-8")
        headings = parse_markdown_headings(content)

        title = headings[0]["title"] if headings else md_file.stem

        structure["files"].append({
            "file_path": rel_path,
            "title": title,
            "headings": [
                {"level": h["level"], "title": h["title"]}
                for h in headings
            ],
        })

    return structure


def create_server(docs_dir: Path) -> Server:
    """Create and configure the MCP server."""
    server = Server("aidocs")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="list_docs",
                description="List all documentation files in the docs directory",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="search_docs",
                description="Search through documentation chunks by keyword. Returns matching sections with relevance scores.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (keywords to match)",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 10)",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="read_doc",
                description="Read the full content of a documentation file or a specific chunk",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the markdown file (relative to docs dir)",
                        },
                        "chunk_index": {
                            "type": "integer",
                            "description": "Optional: specific chunk index to read",
                        },
                    },
                    "required": ["file_path"],
                },
            ),
            Tool(
                name="get_doc_structure",
                description="Get the hierarchical structure (headings) of documentation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Optional: specific file to get structure for",
                        },
                    },
                    "required": [],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "list_docs":
            files = []
            for md_file in find_markdown_files(docs_dir):
                rel_path = str(md_file.relative_to(docs_dir))
                chunks_data = load_chunks_for_file(md_file)

                title = rel_path
                chunk_count = 0
                if chunks_data:
                    chunks = chunks_data.get("chunks", [])
                    chunk_count = len(chunks)
                    if chunks:
                        title = chunks[0].get("title", rel_path)

                files.append({
                    "file_path": rel_path,
                    "title": title,
                    "chunk_count": chunk_count,
                })

            return [TextContent(type="text", text=json.dumps(files, indent=2))]

        elif name == "search_docs":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 10)

            if not query:
                return [TextContent(type="text", text=json.dumps({"error": "Query is required"}))]

            results = search_chunks(docs_dir, query, limit)
            return [TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "read_doc":
            file_path = arguments.get("file_path", "")
            chunk_index = arguments.get("chunk_index")

            if not file_path:
                return [TextContent(type="text", text=json.dumps({"error": "file_path is required"}))]

            md_path = docs_dir / file_path
            if not md_path.exists():
                return [TextContent(type="text", text=json.dumps({"error": f"File not found: {file_path}"}))]

            if chunk_index is not None:
                chunks_data = load_chunks_for_file(md_path)
                if not chunks_data:
                    return [TextContent(type="text", text=json.dumps({"error": "Could not load chunks"}))]

                chunks = chunks_data.get("chunks", [])
                if chunk_index < 0 or chunk_index >= len(chunks):
                    return [TextContent(type="text", text=json.dumps({"error": f"Invalid chunk_index: {chunk_index}"}))]

                chunk = chunks[chunk_index]
                return [TextContent(type="text", text=json.dumps({
                    "file_path": file_path,
                    "chunk_index": chunk_index,
                    "title": chunk.get("title", ""),
                    "hierarchy": chunk.get("hierarchy", []),
                    "content": chunk.get("content", ""),
                }, indent=2))]

            content = md_path.read_text(encoding="utf-8")
            return [TextContent(type="text", text=content)]

        elif name == "get_doc_structure":
            file_path = arguments.get("file_path")
            structure = get_doc_structure(docs_dir, file_path)
            return [TextContent(type="text", text=json.dumps(structure, indent=2))]

        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return server


async def run_server(docs_dir: Path) -> None:
    """Run the MCP server with stdio transport."""
    server = create_server(docs_dir)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
