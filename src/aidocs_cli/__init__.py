"""AI-powered documentation generator CLI for Claude Code projects."""

__version__ = "0.12.1"

from .cli import app


def main() -> None:
    """Entry point for the CLI."""
    app()
