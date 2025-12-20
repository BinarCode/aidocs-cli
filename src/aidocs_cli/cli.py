"""CLI commands for aidocs."""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from .installer import check_tools, install_docs_module

app = typer.Typer(
    name="aidocs",
    help="AI-powered documentation generator for web applications.",
    no_args_is_help=True,
)
console = Console()


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
    from . import __version__
    console.print(f"aidocs-cli version {__version__}")


@app.command()
def update() -> None:
    """Update aidocs-cli to the latest version."""
    from . import __version__

    console.print(f"[blue]Current version: {__version__}[/blue]")
    console.print("[blue]Checking for updates...[/blue]")
    console.print()

    # Determine which package manager to use
    uv_path = shutil.which("uv")
    pipx_path = shutil.which("pipx")

    if uv_path:
        # Use uv tool upgrade
        console.print("[dim]Using uv to update...[/dim]")
        cmd = ["uv", "tool", "upgrade", "aidocs-cli"]
    elif pipx_path:
        # Use pipx upgrade
        console.print("[dim]Using pipx to update...[/dim]")
        cmd = ["pipx", "upgrade", "aidocs-cli"]
    else:
        # Fall back to pip
        console.print("[dim]Using pip to update...[/dim]")
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "aidocs-cli"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Get new version by re-importing
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

            # Check if it's just "already up to date"
            if "already" in result.stderr.lower() or "no updates" in result.stderr.lower():
                console.print("[green]Already at the latest version![/green]")
            else:
                raise typer.Exit(1)

    except FileNotFoundError:
        console.print("[red]Error: Could not find package manager.[/red]")
        console.print("Try running manually:")
        console.print("  [cyan]uv tool upgrade aidocs-cli[/cyan]")
        console.print("  or")
        console.print("  [cyan]pip install --upgrade aidocs-cli[/cyan]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error updating: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
