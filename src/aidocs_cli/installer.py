"""Installation logic for docs module."""

import shutil
import subprocess
from importlib import resources
from pathlib import Path
from typing import Dict

from rich.console import Console

console = Console()


def get_templates_path(ai: str = "claude") -> Path:
    """Get the path to bundled templates.
    
    Args:
        ai: AI assistant type (claude, cursor, copilot)
    """
    base_path = Path(resources.files("aidocs_cli"))
    if ai == "copilot":
        return base_path / "copilot-templates"
    return base_path / "templates"


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
    # Copilot uses a different structure and installs globally
    if ai == "copilot":
        install_copilot_skills(force=force)
        return
    
    templates_path = get_templates_path(ai)

    if ai == "claude":
        base_dir = target_dir / ".claude"
    elif ai == "cursor":
        base_dir = target_dir / ".cursor"
    else:
        base_dir = target_dir / ".claude"

    commands_dest = base_dir / "commands" / "docs"
    workflows_dest = base_dir / "workflows" / "docs"

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
        shutil.copytree(workflows_src, workflows_dest, dirs_exist_ok=True)

        for workflow_dir in workflows_dest.iterdir():
            if workflow_dir.is_dir():
                console.print(f"  [green]✓[/green] {workflow_dir.relative_to(target_dir)}/")

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


def install_copilot_skills(force: bool = False) -> None:
    """Install Copilot skills to ~/.copilot directory.
    
    Args:
        force: Overwrite existing files
    """
    import os
    
    home_dir = Path.home()
    copilot_dir = home_dir / ".copilot"
    skills_dest = copilot_dir / "skills"
    
    templates_path = get_templates_path("copilot")
    skills_src = templates_path / "skills"
    
    if not skills_src.exists():
        console.print("[red]✗[/red] Copilot templates not found")
        return
    
    if skills_dest.exists() and not force:
        raise FileExistsError(
            f"Copilot skills directory already exists: {skills_dest}\n"
            "Use --force to overwrite."
        )
    
    console.print(f"[blue]Installing Copilot skills to {copilot_dir}...[/blue]")
    console.print("[dim]Copying skill files...[/dim]")
    
    skills_dest.mkdir(parents=True, exist_ok=True)
    
    # Copy all skill files
    for item in skills_src.iterdir():
        if item.is_file():
            dest_file = skills_dest / item.name
            shutil.copy2(item, dest_file)
            console.print(f"  [green]✓[/green] ~/.copilot/skills/{item.name}")
        elif item.is_dir():
            dest_dir = skills_dest / item.name
            shutil.copytree(item, dest_dir, dirs_exist_ok=True)
            console.print(f"  [green]✓[/green] ~/.copilot/skills/{item.name}/")


def update_gitignore(target_dir: Path) -> None:
    """Add docs/.auth to .gitignore if not present."""
    gitignore_path = target_dir / ".gitignore"
    docs_auth_entry = "docs/.auth"

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
