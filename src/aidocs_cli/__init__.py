"""AI-powered documentation generator CLI for Claude Code projects."""

from importlib.metadata import version

__version__ = version("aidocs")

from .cli import app


def main() -> None:
    """Entry point for the CLI."""
    app()
