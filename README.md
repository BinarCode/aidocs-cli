# aidocs-cli

AI-powered documentation generator for web applications. Install docs commands into your Claude Code project.

Uses Playwright MCP for browser automation and Claude's vision capabilities for page analysis.

## Installation

```bash
# Install from PyPI
uv tool install aidocs-cli

# Or install from GitHub
uv tool install aidocs-cli --from git+https://github.com/binarcode/aidocs-cli.git

# Or use pipx
pipx install aidocs-cli
```

## Quick Start

```bash
# Initialize in current directory
aidocs init .

# Check your environment
aidocs check
```

Then in Claude Code:

```bash
# Configure your project
/docs:init

# Generate docs for a page
/docs:generate https://myapp.com/dashboard

# Update docs after code changes
/docs:update --base main
```

## CLI Commands

### `aidocs init [PROJECT_NAME]`

Initialize the docs module in a project.

```bash
aidocs init .                  # Current directory
aidocs init my-project         # New directory
aidocs init . --force          # Overwrite existing
aidocs init . --ai cursor      # Use with Cursor
```

**Options:**
| Option | Description |
|--------|-------------|
| `--ai` | AI assistant: `claude`, `cursor`, `copilot` (default: `claude`) |
| `--force, -f` | Overwrite existing files |
| `--no-git` | Skip git initialization |

### `aidocs check`

Check for required tools and dependencies.

```bash
aidocs check
```

### `aidocs version`

Show version information.

## Slash Commands

After running `aidocs init`, these commands are available in Claude Code:

| Command | Description | Requires Playwright |
|---------|-------------|---------------------|
| `/docs:init` | Configure project settings, credentials, output style | No |
| `/docs:generate <url>` | Generate docs for a single page with screenshots | Yes |
| `/docs:analyze <route>` | Analyze codebase for a route (no browser) | No |
| `/docs:batch` | Generate docs for multiple pages | Yes |
| `/docs:update` | Update docs based on git diff | Optional |
| `/docs:discover <module>` | Deep analysis of a module's code structure | No |
| `/docs:explore <module>` | Interactive UI exploration with Playwright | Yes |
| `/docs:flow <entity>` | Document complete entity lifecycle (CRUD) | Yes |

### `/docs:init`

Interactive setup wizard that:
- Detects your tech stack (Laravel, Vue, React, Next.js, etc.)
- Asks for project name, audience, and documentation tone
- Configures authentication method (file, env vars, or manual)
- Sets output directory and screenshot preferences

### `/docs:generate <url>`

Generate documentation for a single page:

```bash
/docs:generate https://myapp.com/campaigns
/docs:generate /campaigns                      # Uses base URL from config
/docs:generate /settings --auth user:pass      # With authentication
```

**Features:**
- Captures full-page screenshots
- Analyzes UI elements visually
- Searches codebase for related code
- Detects forms, buttons, and interactive elements
- Offers to document user flows step-by-step

### `/docs:update`

Update existing documentation based on code changes:

```bash
/docs:update                    # Compare against main
/docs:update --base staging     # Compare against staging branch
/docs:update --dry-run          # Preview changes without applying
/docs:update --screenshots      # Also refresh screenshots
```

**What it does:**
1. Gets git diff between current branch and base
2. Analyzes changed frontend/backend files
3. Maps code changes to affected features
4. Finds and updates related documentation
5. Optionally refreshes screenshots
6. Offers to stage/commit doc changes

**Perfect for:** Running before creating a PR to ensure docs stay in sync with code.

### `/docs:analyze <route>`

Analyze codebase without browser automation:

```bash
/docs:analyze /campaigns
/docs:analyze /api/users
```

### `/docs:batch`

Generate documentation for multiple pages:

```bash
/docs:batch urls.txt                           # From file
/docs:batch --discover --base-url https://myapp.com  # Auto-discover routes
```

### `/docs:discover <module>`

Build a knowledge graph for a specific module:

```bash
/docs:discover --list              # List all detectable modules
/docs:discover campaigns           # Analyze campaigns module
/docs:discover users --deep        # Include relationship analysis
/docs:discover orders --with-flows # Detect user flows
```

**Creates `.docs-knowledge/modules/{module}/` with:**
- `entity.json` - Fields, types, relationships
- `routes.json` - API endpoints and validation
- `components.json` - UI components and props
- `validation.json` - Validation rules from code
- `ui-states/` - Conditional UI behaviors
- `flows/` - Detected user flows

### `/docs:explore <module>`

Interactively explore a module's UI with Playwright:

```bash
/docs:explore campaigns                    # Explore all campaign pages
/docs:explore users --page /users/create   # Specific page
/docs:explore orders --depth deep          # Thorough exploration
```

**What it discovers:**
- Conditional fields (checkbox reveals more inputs)
- Validation messages (tries invalid data)
- UI state changes (what happens when you click)
- Cross-page effects (create here → appears there)

### `/docs:flow <entity>`

Document a complete entity lifecycle:

```bash
/docs:flow campaign                        # Smart flow detection
/docs:flow campaign --lifecycle            # Full CRUD documentation
/docs:flow "user registration"             # Custom flow description
/docs:flow order --include-errors          # Include error states
```

**Produces step-by-step guides with:**
- Screenshots at each step
- Data flow tracking
- Validation documentation
- Error state handling
- Related pages

## Knowledge Base

The intelligent commands build a `.docs-knowledge/` folder:

```
.docs-knowledge/
├── _meta/                    # Project info
├── modules/
│   ├── campaigns/
│   │   ├── entity.json       # Entity definition
│   │   ├── routes.json       # API routes
│   │   ├── validation.json   # Validation rules
│   │   ├── flows/            # User flows
│   │   └── ui-states/        # Conditional UI
│   └── users/
│       └── ...
├── relationships/            # Cross-module relationships
└── cross-module-flows/       # Flows spanning modules
```

This knowledge powers smarter documentation generation.

## Intelligent Workflow

The recommended flow for comprehensive documentation:

```
/docs:discover campaigns     → Analyzes code, builds knowledge graph
         ↓
/docs:explore campaigns      → Playwright explores UI, finds behaviors
         ↓
/docs:flow campaign          → Documents complete lifecycle with screenshots
```

### Example Session

```bash
# 1. List all detectable modules
/docs:discover --list

# 2. Analyze the campaigns module deeply
/docs:discover campaigns --deep --with-flows

# 3. Explore UI to discover conditional fields & validation
/docs:explore campaigns

# 4. Generate full lifecycle documentation
/docs:flow campaign --lifecycle --include-errors

# 5. Update docs after code changes
/docs:update --base main
```

### What Makes It Smart

| Capability | How It Works |
|------------|--------------|
| **Conditional UI** | Clicks checkboxes/toggles, observes what fields appear |
| **Validation Discovery** | Submits empty/invalid forms, captures error messages |
| **Cross-Page Tracking** | Creates data, verifies it appears in lists/dashboards |
| **Entity Lifecycle** | Documents full create → view → edit → delete flow |
| **Modular Analysis** | One module at a time, scales to large projects |
| **Code + UI Correlation** | Matches frontend components to backend validation |

## Configuration

After running `/docs:init`, a `docs-config.yaml` is created:

```yaml
project:
  name: "My App"
  type: saas

style:
  tone: friendly  # friendly | professional | technical | minimal

urls:
  base: "https://myapp.com"

auth:
  method: file    # file | env | manual

output:
  directory: ./docs
```

### Authentication Methods

| Method | Description |
|--------|-------------|
| `file` | Credentials stored in `.docs-auth` (gitignored) |
| `env` | Read from `DOCS_AUTH_USER` and `DOCS_AUTH_PASS` |
| `manual` | Pass `--auth user:pass` each time |

## Output

Generated documentation includes:
- **Overview** - What the page is for
- **Features** - What users can do
- **Key Actions** - Buttons and actions explained
- **Screenshots** - Full-page captures
- **How-to Guides** - Step-by-step flows (optional)
- **Related Pages** - Navigation links

## Requirements

- Python 3.11+
- Claude Code (or Cursor/Copilot)
- Playwright MCP (for browser-based commands)

### Installing Playwright MCP

Add to your `~/.claude.json` or project `.mcp.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic/mcp-playwright"]
    }
  }
}
```

## Development

```bash
git clone https://github.com/binarcode/aidocs-cli.git
cd aidocs-cli
uv venv && uv pip install -e .
aidocs check
```

## License

MIT
