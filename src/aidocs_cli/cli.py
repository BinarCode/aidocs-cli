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
from .installer import check_tools, install_docs_module

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"aidocs-cli version {__version__}")
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
    console.print(f"aidocs-cli version {__version__}")


GITHUB_REPO = "git+https://github.com/BinarCode/aidocs-cli.git"


@app.command()
def update(
    github: bool = typer.Option(
        False,
        "--github",
        help="Install latest from GitHub instead of PyPI.",
    ),
) -> None:
    """Update aidocs-cli to the latest version.

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
            cmd = ["uv", "tool", "install", "--force", "aidocs-cli", "--from", GITHUB_REPO]
        elif pipx_path:
            console.print("[dim]Using pipx to install from GitHub...[/dim]")
            cmd = ["pipx", "install", "--force", GITHUB_REPO]
        else:
            console.print("[dim]Using pip to install from GitHub...[/dim]")
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", GITHUB_REPO]
    else:
        if uv_path:
            console.print("[dim]Using uv to update...[/dim]")
            cmd = ["uv", "tool", "upgrade", "aidocs-cli"]
        elif pipx_path:
            console.print("[dim]Using pipx to update...[/dim]")
            cmd = ["pipx", "upgrade", "aidocs-cli"]
        else:
            console.print("[dim]Using pip to update...[/dim]")
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "aidocs-cli"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            console.print()
            console.print(Panel.fit(
                "[green]aidocs-cli updated successfully![/green]\n\n"
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
            console.print(f"  [cyan]uv tool install aidocs-cli --from {GITHUB_REPO}[/cyan]")
        else:
            console.print("  [cyan]uv tool upgrade aidocs-cli[/cyan]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error updating: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def chunk(
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
        aidocs chunk                  # Chunk all files in docs/
        aidocs chunk docs/users       # Chunk specific directory
        aidocs chunk --force          # Re-chunk all files
        aidocs chunk --dry            # Preview only
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
                f"[dim]Run /docs:sync to generate embeddings and SQL.[/dim]",
                title="Success",
                border_style="green",
            ))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
