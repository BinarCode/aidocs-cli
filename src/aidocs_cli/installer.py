"""Installation logic for docs module."""

import shutil
import subprocess
from importlib import resources
from pathlib import Path
from typing import Dict

from rich.console import Console

console = Console()


def get_templates_path() -> Path:
    """Get the path to bundled templates."""
    return Path(resources.files("aidocs_cli")) / "templates"


def install_docs_module(
    target_dir: Path,
    ai: str = "claude",
    force: bool = False,
    no_git: bool = False,
) -> None:
    """Install the docs module into the target directory.

    Args:
        target_dir: Directory to install into
        ai: AI assistant type (claude, cursor, copilot)
        force: Overwrite existing files
        no_git: Skip git initialization
    """
    templates_path = get_templates_path()

    if ai == "claude":
        commands_dest = target_dir / ".claude" / "commands" / "docs"
    elif ai == "cursor":
        commands_dest = target_dir / ".cursor" / "commands" / "docs"
    else:
        commands_dest = target_dir / ".claude" / "commands" / "docs"

    workflows_dest = target_dir / "docs-workflows"

    if commands_dest.exists() and not force:
        raise FileExistsError(
            f"Commands directory already exists: {commands_dest}\n"
            "Use --force to overwrite."
        )

    if workflows_dest.exists() and not force:
        raise FileExistsError(
            f"Workflows directory already exists: {workflows_dest}\n"
            "Use --force to overwrite."
        )

    console.print("[dim]Copying command files...[/dim]")
    commands_src = templates_path / "commands" / "docs"
    if commands_src.exists():
        commands_dest.mkdir(parents=True, exist_ok=True)
        for file in commands_src.glob("*.md"):
            dest_file = commands_dest / file.name
            shutil.copy2(file, dest_file)
            console.print(f"  [green]✓[/green] {dest_file.relative_to(target_dir)}")

    console.print("[dim]Copying workflow files...[/dim]")
    workflows_src = templates_path / "workflows"
    if workflows_src.exists():
        if workflows_dest.exists() and force:
            shutil.rmtree(workflows_dest)
        shutil.copytree(workflows_src, workflows_dest, dirs_exist_ok=True)

        for workflow_dir in workflows_dest.iterdir():
            if workflow_dir.is_dir():
                console.print(f"  [green]✓[/green] docs-workflows/{workflow_dir.name}/")

    update_gitignore(target_dir)

    if not no_git and not (target_dir / ".git").exists():
        console.print("[dim]Initializing git repository...[/dim]")
        try:
            subprocess.run(
                ["git", "init"],
                cwd=target_dir,
                capture_output=True,
                check=True,
            )
            console.print("  [green]✓[/green] Git repository initialized")
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print("  [yellow]![/yellow] Could not initialize git (git not found)")


def update_gitignore(target_dir: Path) -> None:
    """Add .docs-auth to .gitignore if not present."""
    gitignore_path = target_dir / ".gitignore"
    docs_auth_entry = ".docs-auth"

    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if docs_auth_entry not in content:
            console.print("[dim]Updating .gitignore...[/dim]")
            with open(gitignore_path, "a") as f:
                f.write(f"\n# Documentation credentials (do not commit)\n{docs_auth_entry}\n")
            console.print(f"  [green]✓[/green] Added {docs_auth_entry} to .gitignore")
    else:
        console.print("[dim]Creating .gitignore...[/dim]")
        gitignore_path.write_text(
            f"# Documentation credentials (do not commit)\n{docs_auth_entry}\n"
        )
        console.print(f"  [green]✓[/green] Created .gitignore with {docs_auth_entry}")


def check_tools() -> Dict[str, bool]:
    """Check for required tools and return results."""
    results = {}

    results["git"] = check_command("git", "--version", "Git")
    results["claude"] = check_command("claude", "--version", "Claude Code")
    results["python"] = check_python_version()
    results["uv"] = check_command("uv", "--version", "uv")
    results["npx"] = check_command("npx", "--version", "npx (for Playwright MCP)")

    return results


def check_command(cmd: str, arg: str, name: str) -> bool:
    """Check if a command is available."""
    try:
        result = subprocess.run(
            [cmd, arg],
            capture_output=True,
            timeout=5,
        )
        version_output = result.stdout.decode().strip() or result.stderr.decode().strip()
        version_line = version_output.split("\n")[0] if version_output else "found"
        console.print(f"  [green]✓[/green] {name}: {version_line}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        console.print(f"  [red]✗[/red] {name}: not found")
        return False


def check_python_version() -> bool:
    """Check Python version is 3.11+."""
    import sys
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version >= (3, 11):
        console.print(f"  [green]✓[/green] Python: {version_str}")
        return True
    else:
        console.print(f"  [red]✗[/red] Python: {version_str} (requires 3.11+)")
        return False
