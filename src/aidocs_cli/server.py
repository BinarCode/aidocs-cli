"""MkDocs server utilities for documentation preview."""

from pathlib import Path
from typing import Optional

import yaml


class PythonName:
    """Represents a Python name reference for YAML serialization."""

    def __init__(self, name: str):
        self.name = name


def python_name_representer(dumper: yaml.Dumper, data: PythonName) -> yaml.Node:
    """Custom YAML representer for Python name references."""
    return dumper.represent_scalar("!python/name:" + data.name, "", style="")


def discover_section(section_dir: Path, docs_root: Path) -> list:
    """Discover navigation items within a section directory."""
    items = []

    index_file = section_dir / "index.md"
    if index_file.exists():
        rel_path = index_file.relative_to(docs_root)
        items.append({"Overview": str(rel_path)})

    for md_file in sorted(section_dir.glob("*.md")):
        if md_file.name == "index.md":
            continue
        rel_path = md_file.relative_to(docs_root)
        title = md_file.stem.replace("-", " ").replace("_", " ").title()
        items.append({title: str(rel_path)})

    for subdir in sorted(section_dir.iterdir()):
        if subdir.is_dir() and not subdir.name.startswith((".", "_")) and subdir.name != "images":
            nested_items = discover_section(subdir, docs_root)
            if nested_items:
                subdir_title = subdir.name.replace("-", " ").replace("_", " ").title()
                items.append({subdir_title: nested_items})

    return items


def discover_nav_structure(docs_dir: Path) -> list:
    """Auto-discover navigation structure from docs folder.

    Scans the docs directory and builds a navigation structure:
    - Top-level index.md becomes the home page
    - Each subdirectory becomes a section
    - index.md in subdirectories becomes section home
    - Other .md files become section items
    """
    nav = []

    index_file = docs_dir / "index.md"
    if index_file.exists():
        nav.append({"Home": "index.md"})

    for item in sorted(docs_dir.iterdir()):
        if item.name.startswith((".", "_")) or item.name in ["images", ".chunks"]:
            continue

        if item.is_dir():
            section_nav = discover_section(item, docs_dir)
            if section_nav:
                section_title = item.name.replace("-", " ").replace("_", " ").title()
                nav.append({section_title: section_nav})
        elif item.is_file() and item.suffix == ".md" and item.name != "index.md":
            title = item.stem.replace("-", " ").replace("_", " ").title()
            nav.append({title: item.name})

    return nav


def extract_project_name(docs_dir: Path) -> str:
    """Try to extract project name from config.yml or directory name."""
    config_file = docs_dir / "config.yml"
    if config_file.exists():
        try:
            config = yaml.safe_load(config_file.read_text())
            if config and config.get("project_name"):
                return config["project_name"]
        except Exception:
            pass

    return docs_dir.parent.name.replace("-", " ").replace("_", " ").title()


def generate_mkdocs_config(
    docs_dir: Path,
    site_name: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> dict:
    """Generate MkDocs configuration dictionary."""
    if not site_name:
        site_name = extract_project_name(docs_dir)

    nav = discover_nav_structure(docs_dir)

    config = {
        "site_name": site_name,
        "docs_dir": str(docs_dir.resolve()),
        "theme": {
            "name": "material",
            "palette": [
                {
                    "media": "(prefers-color-scheme: light)",
                    "scheme": "default",
                    "primary": "indigo",
                    "accent": "indigo",
                    "toggle": {
                        "icon": "material/brightness-7",
                        "name": "Switch to dark mode",
                    },
                },
                {
                    "media": "(prefers-color-scheme: dark)",
                    "scheme": "slate",
                    "primary": "indigo",
                    "accent": "indigo",
                    "toggle": {
                        "icon": "material/brightness-4",
                        "name": "Switch to light mode",
                    },
                },
            ],
            "features": [
                "navigation.instant",
                "navigation.tracking",
                "navigation.sections",
                "navigation.expand",
                "navigation.top",
                "search.suggest",
                "search.highlight",
                "content.code.copy",
                "content.tabs.link",
            ],
        },
        "markdown_extensions": [
            "pymdownx.highlight",
            {
                "pymdownx.superfences": {
                    "custom_fences": [
                        {
                            "name": "mermaid",
                            "class": "mermaid",
                            "format": PythonName("pymdownx.superfences.fence_code_format"),
                        }
                    ]
                }
            },
            {"pymdownx.tabbed": {"alternate_style": True}},
            "pymdownx.details",
            "admonition",
            "tables",
            "attr_list",
            "md_in_html",
        ],
        "plugins": [
            "search",
        ],
        "extra": {
            "generator": False,
        },
        "extra_javascript": [
            "https://unpkg.com/mermaid@10/dist/mermaid.min.js",
        ],
    }

    if nav:
        config["nav"] = nav

    if output_dir:
        config["site_dir"] = str(output_dir.resolve())

    return config


def write_mkdocs_config(config: dict, output_path: Path) -> None:
    """Write MkDocs configuration to a YAML file."""
    yaml.add_representer(PythonName, python_name_representer)
    output_path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))


def validate_docs_directory(docs_dir: Path) -> tuple[bool, str]:
    """Validate that docs directory exists and has markdown files."""
    if not docs_dir.exists():
        return False, f"Directory not found: {docs_dir}"

    if not docs_dir.is_dir():
        return False, f"Not a directory: {docs_dir}"

    md_files = list(docs_dir.rglob("*.md"))
    md_files = [f for f in md_files if not any(p.startswith(".") for p in f.relative_to(docs_dir).parts)]

    if not md_files:
        return False, (
            f"No markdown files found in {docs_dir}\n\n"
            "Generate documentation first:\n"
            "  /docs:generate <url>     - Document a single page\n"
            "  /docs:discover && /docs:plan && /docs:execute  - Document entire project"
        )

    return True, ""
