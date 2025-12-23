"""AI-powered documentation generator CLI for Claude Code projects."""

__version__ = "0.14.0"

from .cli import app


def main() -> None:
    """Entry point for the CLI."""
    app()
