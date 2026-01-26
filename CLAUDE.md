# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

aidocs is a Python CLI tool that generates AI-powered documentation for web applications. It installs slash commands into Claude Code projects (e.g., `/docs:generate`, `/docs:flow`) that combine vision analysis, codebase analysis, and interactive UI exploration to produce comprehensive documentation.

## Development Commands

```bash
# Setup development environment
uv venv && uv pip install -e .

# Run CLI
aidocs check              # Check environment/dependencies
aidocs init .             # Install docs module in current project
aidocs version            # Show version

# RAG/Embeddings workflow
aidocs rag-chunks docs/   # Chunk markdown files for vector DB
aidocs rag-vectors        # Generate embeddings (requires OPENAI_API_KEY)

# Documentation server
aidocs serve              # Serve docs with MkDocs Material
aidocs serve --build      # Build static site

# MCP server (expose docs to Claude Code)
aidocs mcp docs/          # Start MCP server for docs directory

# PDF export
aidocs export-pdf docs/page.md

# Watch mode (auto-sync on file changes)
aidocs watch              # Watch docs/ and auto-chunk on changes
aidocs watch --with-vectors  # Also generate embeddings

# Documentation coverage analysis
aidocs coverage           # Show coverage report
aidocs coverage --format json  # Machine-readable output
aidocs coverage --ci      # Exit code 1 if below 80%
```

## Architecture

```
src/aidocs_cli/
├── __init__.py       # Version and entry point
├── cli.py            # Typer CLI commands (init, check, serve, rag-*, export-pdf, watch, coverage)
├── installer.py      # Copies templates to target project (.claude/commands/, .claude/workflows/)
├── chunker.py        # Splits markdown at ## headings for RAG
├── coverage.py       # Documentation coverage analysis (routes, components, models detection)
├── embeddings.py     # OpenAI embeddings + SQL generation for pgvector
├── server.py         # MkDocs config generation and nav discovery
├── pdf_exporter.py   # Markdown→HTML→PDF with Chrome/Playwright
├── mcp_server.py     # MCP server exposing docs via tools (list, search, read)
├── watcher.py        # File system watcher for auto-sync (watchdog + Rich Live)
└── templates/
    ├── commands/docs/    # Slash command definitions (*.md)
    └── workflows/        # Workflow implementations per command
```

### Key Components

- **CLI (cli.py)**: Uses Typer with Rich for terminal UI. Entry point is `app()`.
- **Installer**: Copies command/workflow templates to target project's `.claude/` directory (or `.cursor/` for Cursor).
- **Chunker**: Creates `.chunks.json` files alongside markdown, tracks changes via `docs/.chunks/manifest.json`.
- **Coverage**: Analyzes codebase for routes/components/models, matches against docs, reports coverage with visual progress bars.
- **Embeddings**: Calls OpenAI API (text-embedding-3-small, 1536 dimensions), outputs `docs/.chunks/sync.sql` for pgvector import.
- **Server**: Auto-discovers nav structure from folder hierarchy, generates ephemeral `mkdocs.yml`.

### Slash Commands Flow

When `aidocs init` runs:
1. Templates from `src/aidocs_cli/templates/` are copied to project's `.claude/commands/docs/` and `.claude/workflows/docs/`
2. Each command (e.g., `generate.md`) references a workflow that defines the multi-step process
3. Workflows use Playwright MCP for browser automation when needed

## Version Management

Version is defined in two places (keep in sync):
- `pyproject.toml` → `version = "X.Y.Z"`
- `src/aidocs_cli/__init__.py` → `__version__ = "X.Y.Z"`

## Release Process

1. Update version in both files
2. Commit and push to main
3. Create GitHub release → triggers `.github/workflows/publish.yml` (PyPI) and `.github/workflows/update-homebrew.yml`

## Dependencies

Core: typer, rich, httpx, mkdocs, mkdocs-material, pyyaml, mcp, watchdog, python-dotenv

Python 3.11+ required. Build system uses hatchling.

## Environment Variables

- `OPENAI_API_KEY`: Required for `rag-vectors` command (embedding generation)
