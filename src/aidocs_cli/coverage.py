"""Documentation coverage analysis for codebases."""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Callable


@dataclass
class CoverageItem:
    """Represents a documentable item in the codebase."""
    category: str  # routes, components, models, functions, etc.
    name: str
    file_path: str
    line_number: int
    documented: bool = False
    doc_file: Optional[str] = None


@dataclass
class CoverageCategory:
    """Coverage statistics for a category."""
    name: str
    total: int = 0
    documented: int = 0
    items: list[CoverageItem] = field(default_factory=list)

    @property
    def coverage_percent(self) -> float:
        if self.total == 0:
            return 100.0
        return (self.documented / self.total) * 100

    @property
    def undocumented(self) -> list[CoverageItem]:
        return [item for item in self.items if not item.documented]


@dataclass
class CoverageReport:
    """Complete coverage report."""
    categories: dict[str, CoverageCategory] = field(default_factory=dict)
    analyzed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    codebase_dir: str = ""
    docs_dir: str = ""

    @property
    def total_items(self) -> int:
        return sum(cat.total for cat in self.categories.values())

    @property
    def total_documented(self) -> int:
        return sum(cat.documented for cat in self.categories.values())

    @property
    def overall_coverage(self) -> float:
        if self.total_items == 0:
            return 100.0
        return (self.total_documented / self.total_items) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "analyzed_at": self.analyzed_at,
            "codebase_dir": self.codebase_dir,
            "docs_dir": self.docs_dir,
            "summary": {
                "total_items": self.total_items,
                "documented": self.total_documented,
                "coverage_percent": round(self.overall_coverage, 1),
            },
            "categories": {
                name: {
                    "total": cat.total,
                    "documented": cat.documented,
                    "coverage_percent": round(cat.coverage_percent, 1),
                    "undocumented": [
                        {
                            "name": item.name,
                            "file": item.file_path,
                            "line": item.line_number,
                        }
                        for item in cat.undocumented
                    ]
                }
                for name, cat in self.categories.items()
            }
        }


# === Route Detection Patterns ===

# Next.js App Router patterns
NEXTJS_APP_ROUTE_PATTERNS = [
    # route.ts/js handlers
    (r"export\s+(?:async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)", "method"),
    # page.tsx exports
    (r"export\s+default\s+(?:async\s+)?function\s+(\w+Page|\w+)", "page"),
]

# Next.js Pages Router patterns
NEXTJS_PAGES_ROUTE_PATTERNS = [
    (r"export\s+default\s+(?:async\s+)?function\s+(\w+)", "page"),
    (r"export\s+(?:const|async\s+function)\s+(getServerSideProps|getStaticProps)", "data"),
]

# Express/Node.js patterns
EXPRESS_ROUTE_PATTERNS = [
    (r"(?:app|router)\.(get|post|put|patch|delete|all)\s*\(\s*['\"`]([^'\"`]+)['\"`]", "route"),
    (r"@(Get|Post|Put|Patch|Delete|All)\s*\(\s*['\"`]?([^'\"`\)]*)['\"`]?\s*\)", "decorator"),
]

# Python FastAPI/Flask patterns
PYTHON_ROUTE_PATTERNS = [
    (r"@(?:app|router|api)\.(get|post|put|patch|delete)\s*\(\s*['\"`]([^'\"`]+)['\"`]", "route"),
    (r"@(?:app|router)\.route\s*\(\s*['\"`]([^'\"`]+)['\"`]", "route"),
]

# Laravel patterns
LARAVEL_ROUTE_PATTERNS = [
    (r"Route::(get|post|put|patch|delete|any)\s*\(\s*['\"`]([^'\"`]+)['\"`]", "route"),
]


# === Component Detection Patterns ===

REACT_COMPONENT_PATTERNS = [
    # Function components
    (r"export\s+(?:default\s+)?function\s+([A-Z]\w+)", "function"),
    # Arrow function components
    (r"export\s+(?:default\s+)?(?:const|let)\s+([A-Z]\w+)\s*[=:]\s*(?:\([^)]*\)|[^=])*\s*=>", "arrow"),
    # Class components
    (r"export\s+(?:default\s+)?class\s+([A-Z]\w+)\s+extends\s+(?:React\.)?(?:Component|PureComponent)", "class"),
]

VUE_COMPONENT_PATTERNS = [
    (r"export\s+default\s+(?:defineComponent\s*\(\s*)?{", "options"),
    (r"<script[^>]*setup[^>]*>", "setup"),
]

SVELTE_COMPONENT_PATTERNS = [
    (r"<script[^>]*>", "script"),
]


# === Model Detection Patterns ===

# TypeScript/JavaScript
TS_MODEL_PATTERNS = [
    (r"(?:export\s+)?(?:interface|type)\s+([A-Z]\w+)", "type"),
    (r"(?:export\s+)?class\s+([A-Z]\w+)(?:\s+extends|\s+implements|\s*{)", "class"),
]

# Python
PYTHON_MODEL_PATTERNS = [
    (r"class\s+([A-Z]\w+)\s*\([^)]*(?:Model|Base|Schema|BaseModel)[^)]*\)", "model"),
    (r"class\s+([A-Z]\w+)\s*\(.*\):", "class"),
]

# Prisma
PRISMA_MODEL_PATTERNS = [
    (r"model\s+([A-Z]\w+)\s*{", "model"),
]


def detect_framework(codebase_dir: Path) -> dict[str, bool]:
    """Detect which frameworks are used in the codebase."""
    frameworks = {
        "nextjs": False,
        "react": False,
        "vue": False,
        "svelte": False,
        "express": False,
        "fastapi": False,
        "flask": False,
        "laravel": False,
        "prisma": False,
    }

    # Check package.json
    pkg_json = codebase_dir / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

            if "next" in deps:
                frameworks["nextjs"] = True
                frameworks["react"] = True
            elif "react" in deps:
                frameworks["react"] = True
            if "vue" in deps:
                frameworks["vue"] = True
            if "svelte" in deps:
                frameworks["svelte"] = True
            if "express" in deps:
                frameworks["express"] = True
        except Exception:
            pass

    # Check pyproject.toml or requirements.txt
    pyproject = codebase_dir / "pyproject.toml"
    requirements = codebase_dir / "requirements.txt"

    py_deps = ""
    if pyproject.exists():
        py_deps = pyproject.read_text().lower()
    if requirements.exists():
        py_deps += requirements.read_text().lower()

    if "fastapi" in py_deps:
        frameworks["fastapi"] = True
    if "flask" in py_deps:
        frameworks["flask"] = True

    # Check composer.json for Laravel
    composer = codebase_dir / "composer.json"
    if composer.exists():
        try:
            comp = json.loads(composer.read_text())
            if "laravel/framework" in comp.get("require", {}):
                frameworks["laravel"] = True
        except Exception:
            pass

    # Check for Prisma
    if (codebase_dir / "prisma" / "schema.prisma").exists():
        frameworks["prisma"] = True

    return frameworks


def find_routes(codebase_dir: Path, frameworks: dict[str, bool]) -> list[CoverageItem]:
    """Find all routes/endpoints in the codebase."""
    routes = []

    # Next.js App Router
    if frameworks.get("nextjs"):
        app_dir = codebase_dir / "app"
        if not app_dir.exists():
            app_dir = codebase_dir / "src" / "app"

        if app_dir.exists():
            # Find route.ts/js files
            route_extensions = ["ts", "tsx", "js", "jsx"]
            for ext in route_extensions:
                for route_file in app_dir.rglob(f"route.{ext}"):
                    try:
                        content = route_file.read_text()
                    except Exception:
                        continue

                    rel_path = route_file.relative_to(app_dir)

                    # Extract route path from file location
                    route_path = "/" + str(rel_path.parent).replace("\\", "/")
                    route_path = re.sub(r"\([^)]+\)/", "", route_path)  # Remove route groups
                    route_path = route_path.replace("/route", "")
                    if route_path == "" or route_path == "/.":
                        route_path = "/"

                    for pattern, _ in NEXTJS_APP_ROUTE_PATTERNS:
                        for match in re.finditer(pattern, content):
                            method = match.group(1)
                            line_num = content[:match.start()].count("\n") + 1
                            routes.append(CoverageItem(
                                category="routes",
                                name=f"{method} {route_path}",
                                file_path=str(route_file.relative_to(codebase_dir)),
                                line_number=line_num,
                            ))

            # Find page.tsx files (GET routes implicitly)
            for ext in route_extensions:
                for page_file in app_dir.rglob(f"page.{ext}"):
                    rel_path = page_file.relative_to(app_dir)
                    route_path = "/" + str(rel_path.parent).replace("\\", "/")
                    route_path = re.sub(r"\([^)]+\)/", "", route_path)
                    route_path = route_path.replace("/page", "")
                    if route_path == "" or route_path == "/" or route_path == "/.":
                        route_path = "/"

                    routes.append(CoverageItem(
                        category="routes",
                        name=f"PAGE {route_path}",
                        file_path=str(page_file.relative_to(codebase_dir)),
                        line_number=1,
                    ))

    # Express routes
    if frameworks.get("express"):
        for ext in ["ts", "js"]:
            for file in codebase_dir.rglob(f"*.{ext}"):
                if "node_modules" in str(file):
                    continue
                try:
                    content = file.read_text()
                    for pattern, _ in EXPRESS_ROUTE_PATTERNS:
                        for match in re.finditer(pattern, content):
                            method = match.group(1).upper()
                            path = match.group(2)
                            line_num = content[:match.start()].count("\n") + 1
                            routes.append(CoverageItem(
                                category="routes",
                                name=f"{method} {path}",
                                file_path=str(file.relative_to(codebase_dir)),
                                line_number=line_num,
                            ))
                except Exception:
                    continue

    # Python routes (FastAPI/Flask)
    if frameworks.get("fastapi") or frameworks.get("flask"):
        for file in codebase_dir.rglob("*.py"):
            if "__pycache__" in str(file) or ".venv" in str(file):
                continue
            try:
                content = file.read_text()
                for pattern, _ in PYTHON_ROUTE_PATTERNS:
                    for match in re.finditer(pattern, content):
                        if len(match.groups()) == 2:
                            method = match.group(1).upper()
                            path = match.group(2)
                        else:
                            method = "ANY"
                            path = match.group(1)
                        line_num = content[:match.start()].count("\n") + 1
                        routes.append(CoverageItem(
                            category="routes",
                            name=f"{method} {path}",
                            file_path=str(file.relative_to(codebase_dir)),
                            line_number=line_num,
                        ))
            except Exception:
                continue

    # Laravel routes
    if frameworks.get("laravel"):
        routes_dir = codebase_dir / "routes"
        if routes_dir.exists():
            for file in routes_dir.rglob("*.php"):
                try:
                    content = file.read_text()
                    for pattern, _ in LARAVEL_ROUTE_PATTERNS:
                        for match in re.finditer(pattern, content):
                            method = match.group(1).upper()
                            path = match.group(2)
                            line_num = content[:match.start()].count("\n") + 1
                            routes.append(CoverageItem(
                                category="routes",
                                name=f"{method} {path}",
                                file_path=str(file.relative_to(codebase_dir)),
                                line_number=line_num,
                            ))
                except Exception:
                    continue

    return routes


def find_components(codebase_dir: Path, frameworks: dict[str, bool]) -> list[CoverageItem]:
    """Find all UI components in the codebase."""
    components = []

    # Directories to search for components
    component_dirs = [
        "components", "src/components", "app/components",
        "lib/components", "src/lib/components",
        "ui", "src/ui",
    ]

    search_dirs = []
    for dir_name in component_dirs:
        comp_dir = codebase_dir / dir_name
        if comp_dir.exists():
            search_dirs.append(comp_dir)

    # If no component directories found, search more broadly
    if not search_dirs:
        search_dirs = [codebase_dir]

    # React/Next.js components
    if frameworks.get("react") or frameworks.get("nextjs"):
        for search_dir in search_dirs:
            for ext in ["tsx", "jsx", "ts", "js"]:
                for file in search_dir.rglob(f"*.{ext}"):
                    if "node_modules" in str(file) or ".next" in str(file):
                        continue

                    # Skip test files
                    if ".test." in str(file) or ".spec." in str(file) or "__tests__" in str(file):
                        continue

                    try:
                        content = file.read_text()
                        for pattern, comp_type in REACT_COMPONENT_PATTERNS:
                            for match in re.finditer(pattern, content):
                                name = match.group(1)
                                line_num = content[:match.start()].count("\n") + 1
                                components.append(CoverageItem(
                                    category="components",
                                    name=name,
                                    file_path=str(file.relative_to(codebase_dir)),
                                    line_number=line_num,
                                ))
                    except Exception:
                        continue

    # Vue components
    if frameworks.get("vue"):
        for search_dir in search_dirs:
            for file in search_dir.rglob("*.vue"):
                if "node_modules" in str(file):
                    continue
                components.append(CoverageItem(
                    category="components",
                    name=file.stem,
                    file_path=str(file.relative_to(codebase_dir)),
                    line_number=1,
                ))

    # Svelte components
    if frameworks.get("svelte"):
        for search_dir in search_dirs:
            for file in search_dir.rglob("*.svelte"):
                if "node_modules" in str(file):
                    continue
                components.append(CoverageItem(
                    category="components",
                    name=file.stem,
                    file_path=str(file.relative_to(codebase_dir)),
                    line_number=1,
                ))

    return components


def find_models(codebase_dir: Path, frameworks: dict[str, bool]) -> list[CoverageItem]:
    """Find all data models in the codebase."""
    models = []

    # Prisma models
    if frameworks.get("prisma"):
        schema_path = codebase_dir / "prisma" / "schema.prisma"
        if schema_path.exists():
            content = schema_path.read_text()
            for pattern, _ in PRISMA_MODEL_PATTERNS:
                for match in re.finditer(pattern, content):
                    name = match.group(1)
                    line_num = content[:match.start()].count("\n") + 1
                    models.append(CoverageItem(
                        category="models",
                        name=name,
                        file_path="prisma/schema.prisma",
                        line_number=line_num,
                    ))

    # TypeScript types/interfaces
    type_dirs = [
        "types", "src/types", "lib/types",
        "models", "src/models", "lib/models",
        "schemas", "src/schemas",
    ]

    for dir_name in type_dirs:
        type_dir = codebase_dir / dir_name
        if type_dir.exists():
            for file in type_dir.rglob("*.ts"):
                if "node_modules" in str(file):
                    continue
                try:
                    content = file.read_text()
                    for pattern, _ in TS_MODEL_PATTERNS:
                        for match in re.finditer(pattern, content):
                            name = match.group(1)
                            # Skip common utility types
                            if name in ["Props", "State", "Context", "Config"]:
                                continue
                            line_num = content[:match.start()].count("\n") + 1
                            models.append(CoverageItem(
                                category="models",
                                name=name,
                                file_path=str(file.relative_to(codebase_dir)),
                                line_number=line_num,
                            ))
                except Exception:
                    continue

    # Python models
    if frameworks.get("fastapi") or frameworks.get("flask"):
        model_dirs = ["models", "src/models", "app/models", "schemas", "src/schemas"]
        for dir_name in model_dirs:
            model_dir = codebase_dir / dir_name
            if model_dir.exists():
                for file in model_dir.rglob("*.py"):
                    if "__pycache__" in str(file):
                        continue
                    try:
                        content = file.read_text()
                        for pattern, _ in PYTHON_MODEL_PATTERNS:
                            for match in re.finditer(pattern, content):
                                name = match.group(1)
                                line_num = content[:match.start()].count("\n") + 1
                                models.append(CoverageItem(
                                    category="models",
                                    name=name,
                                    file_path=str(file.relative_to(codebase_dir)),
                                    line_number=line_num,
                                ))
                    except Exception:
                        continue

    return models


def extract_doc_references(docs_dir: Path) -> set[str]:
    """Extract all codebase references from documentation.

    Looks for patterns like:
    - Route mentions: GET /api/users, POST /users
    - Component mentions: PaymentForm, UserDashboard
    - File path mentions: components/Button.tsx
    - Code blocks with file references
    """
    references = set()

    # Common English words to skip (not component names)
    SKIP_WORDS = {
        "The", "This", "That", "These", "Those", "There", "Here",
        "What", "When", "Where", "Which", "Who", "Why", "How",
        "And", "But", "For", "Not", "With", "You", "Your",
        "All", "Any", "Can", "May", "Will", "Should", "Would", "Could",
        "API", "URL", "HTTP", "HTML", "CSS", "JSON", "XML", "SQL",
        "TODO", "FIXME", "NOTE", "WARNING", "ERROR", "INFO", "DEBUG",
        "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS",
        "New", "Old", "See", "Use", "Run", "Set", "Add", "Try",
        "Example", "Examples", "Documentation", "Overview", "Introduction",
        "Setup", "Install", "Usage", "Configuration", "Settings",
        "Returns", "Creates", "Updates", "Deletes", "Displays",
    }

    if not docs_dir.exists():
        return references

    for md_file in docs_dir.rglob("*.md"):
        # Skip hidden dirs and chunks
        parts = md_file.relative_to(docs_dir).parts
        if any(p.startswith(".") for p in parts):
            continue

        try:
            content = md_file.read_text()

            # Find route mentions
            route_patterns = [
                r"(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(/[^\s\)`]+)",
                r"`(GET|POST|PUT|PATCH|DELETE)\s+(/[^`]+)`",
            ]
            for pattern in route_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    method = match.group(1).upper()
                    path = match.group(2).rstrip(")").rstrip("`")
                    references.add(f"{method} {path}")

            # Find page mentions in Next.js style
            page_patterns = [
                r"(?:PAGE|page|route)\s+[`'\"]?(/[^\s`'\"]+)[`'\"]?",
            ]
            for pattern in page_patterns:
                for match in re.finditer(pattern, content):
                    references.add(f"PAGE {match.group(1)}")

            # Find JSX component references: <ComponentName> or <ComponentName />
            jsx_pattern = r"<([A-Z][a-zA-Z0-9]+)(?:\s|/|>)"
            for match in re.finditer(jsx_pattern, content):
                name = match.group(1)
                if name not in SKIP_WORDS:
                    references.add(name)

            # Find backtick component references: `ComponentName`
            backtick_pattern = r"`([A-Z][a-zA-Z0-9]+)`"
            for match in re.finditer(backtick_pattern, content):
                name = match.group(1)
                if name not in SKIP_WORDS:
                    references.add(name)

            # Find PascalCase compound names (2+ capital letters = likely component)
            # e.g., UserProfile, PaymentForm, DataTable
            pascal_pattern = r"\b([A-Z][a-z]+[A-Z][a-zA-Z0-9]*)\b"
            for match in re.finditer(pascal_pattern, content):
                name = match.group(1)
                if name not in SKIP_WORDS:
                    references.add(name)

            # Find explicit component mentions: "the UserProfile component"
            explicit_pattern = r"(?:the\s+)?([A-Z][a-zA-Z0-9]+)\s+(?:component|widget|form|button|modal|dialog)"
            for match in re.finditer(explicit_pattern, content, re.IGNORECASE):
                name = match.group(1)
                if name not in SKIP_WORDS:
                    references.add(name)

            # Find section headers that name components: "## Dashboard" or "### UserProfile"
            header_pattern = r"^#{1,6}\s+([A-Z][a-zA-Z0-9]+)(?:\s+Component)?(?:\s|$)"
            for match in re.finditer(header_pattern, content, re.MULTILINE):
                name = match.group(1)
                if name not in SKIP_WORDS:
                    references.add(name)

            # Find model/type mentions
            model_patterns = [
                r"(?:model|type|interface|schema|entity)\s+[`'\"]?([A-Z][a-zA-Z0-9]+)[`'\"]?",
            ]
            for pattern in model_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    name = match.group(1)
                    if name not in SKIP_WORDS:
                        references.add(name)

            # Find file path mentions
            file_pattern = r"(?:^|\s|`)[a-zA-Z0-9_\-/]+\.(tsx?|jsx?|vue|svelte|py|php)(?:\s|`|$)"
            for match in re.finditer(file_pattern, content):
                # Extract just the filename for matching
                file_path = match.group(0).strip().strip("`")
                references.add(file_path)

        except Exception:
            continue

    return references


def match_documentation(
    items: list[CoverageItem],
    doc_references: set[str],
) -> list[CoverageItem]:
    """Match codebase items against documentation references."""
    for item in items:
        # Normalize item name for matching
        item_name = item.name

        # Check direct match
        if item_name in doc_references:
            item.documented = True
            continue

        # Check partial match for routes (ignore dynamic segments)
        if item.category == "routes":
            # Normalize route for comparison
            normalized = re.sub(r"\[[^\]]+\]", "*", item_name)  # [id] -> *
            normalized = re.sub(r":\w+", "*", normalized)  # :id -> *

            for ref in doc_references:
                ref_normalized = re.sub(r"\[[^\]]+\]", "*", ref)
                ref_normalized = re.sub(r":\w+", "*", ref_normalized)
                ref_normalized = re.sub(r"\{[^}]+\}", "*", ref_normalized)  # {id} -> *

                if normalized == ref_normalized:
                    item.documented = True
                    break

        # Check component name match (case-insensitive partial)
        if item.category == "components":
            name_lower = item.name.lower()
            for ref in doc_references:
                if ref.lower() == name_lower or name_lower in ref.lower():
                    item.documented = True
                    break

        # Check model name match
        if item.category == "models":
            for ref in doc_references:
                if item.name.lower() == ref.lower():
                    item.documented = True
                    break

    return items


def analyze_coverage(
    codebase_dir: Path,
    docs_dir: Path,
    on_status: Optional[Callable[[str], None]] = None,
) -> CoverageReport:
    """Analyze documentation coverage for a codebase.

    Args:
        codebase_dir: Path to the codebase root
        docs_dir: Path to the documentation directory
        on_status: Optional callback for status messages

    Returns:
        CoverageReport with detailed coverage analysis
    """
    report = CoverageReport(
        codebase_dir=str(codebase_dir),
        docs_dir=str(docs_dir),
    )

    def status(msg: str) -> None:
        if on_status:
            on_status(msg)

    # Detect frameworks
    status("Detecting frameworks...")
    frameworks = detect_framework(codebase_dir)
    detected = [name for name, found in frameworks.items() if found]
    if detected:
        status(f"Detected: {', '.join(detected)}")
    else:
        status("No specific frameworks detected, using generic analysis")

    # Extract documentation references
    status("Scanning documentation...")
    doc_references = extract_doc_references(docs_dir)
    status(f"Found {len(doc_references)} documentation references")

    # Find routes
    status("Scanning for routes/endpoints...")
    routes = find_routes(codebase_dir, frameworks)
    routes = match_documentation(routes, doc_references)

    if routes:
        routes_cat = CoverageCategory(name="Routes", items=routes)
        routes_cat.total = len(routes)
        routes_cat.documented = sum(1 for r in routes if r.documented)
        report.categories["routes"] = routes_cat
        status(f"Found {len(routes)} routes")

    # Find components
    status("Scanning for components...")
    components = find_components(codebase_dir, frameworks)
    components = match_documentation(components, doc_references)

    if components:
        comp_cat = CoverageCategory(name="Components", items=components)
        comp_cat.total = len(components)
        comp_cat.documented = sum(1 for c in components if c.documented)
        report.categories["components"] = comp_cat
        status(f"Found {len(components)} components")

    # Find models
    status("Scanning for models/types...")
    models = find_models(codebase_dir, frameworks)
    models = match_documentation(models, doc_references)

    if models:
        models_cat = CoverageCategory(name="Models", items=models)
        models_cat.total = len(models)
        models_cat.documented = sum(1 for m in models if m.documented)
        report.categories["models"] = models_cat
        status(f"Found {len(models)} models/types")

    return report


def save_coverage_report(report: CoverageReport, docs_dir: Path) -> Path:
    """Save coverage report to .chunks/coverage.json."""
    chunks_dir = docs_dir / ".chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    report_path = chunks_dir / "coverage.json"
    report_path.write_text(
        json.dumps(report.to_dict(), indent=2),
        encoding="utf-8",
    )

    return report_path


def load_coverage_report(docs_dir: Path) -> Optional[CoverageReport]:
    """Load previous coverage report if it exists."""
    report_path = docs_dir / ".chunks" / "coverage.json"

    if not report_path.exists():
        return None

    try:
        data = json.loads(report_path.read_text())
        # Convert dict back to CoverageReport
        # (simplified - just returns dict for now)
        return data
    except Exception:
        return None
