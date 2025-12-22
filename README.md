# aidocs-cli

AI-powered documentation generator for web applications.

## How It Works

aidocs generates comprehensive documentation by combining **three sources of truth**:

1. **Vision Analysis** - Playwright captures screenshots, Claude analyzes what users actually see
2. **Codebase Analysis** - Scans your frontend components, backend routes, validation rules, and models
3. **Interactive Exploration** - Clicks buttons, fills forms, discovers conditional UI and validation messages

This produces documentation that's accurate to both the code AND the actual user experience.

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  📸 Screenshots │  +  │  📄 Code Analysis │  +  │  🖱️ UI Testing   │
│  (what users    │     │  (validation,     │     │  (conditional   │
│   see)          │     │   routes, models) │     │   fields, flows)│
└────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
         │                       │                        │
         └───────────────────────┼────────────────────────┘
                                 ▼
                    ┌────────────────────────┐
                    │  📚 Smart Documentation │
                    │  that stays in sync    │
                    └────────────────────────┘
```

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
# Install the CLI
uv tool install aidocs-cli

# Add to your project
aidocs init .
```

## Usage Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              SETUP (once)                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  $ aidocs init .                    Install commands into project            │
│           │                                                                  │
│           ▼                                                                  │
│  /docs:init                         Configure: name, auth, style, output     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    OPTION A: Document a Code Flow                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  /docs:flow "sync users from discord"    ← Describe the flow in words!       │
│           │                                                                  │
│           ├──→ Searches codebase for relevant files                          │
│           ├──→ Traces execution path and builds call graph                   │
│           ├──→ Generates mermaid sequence diagram                            │
│           ├──→ Captures UI screenshots (if Playwright + route detected)      │
│           └──→ Creates docs/flows/sync-users-from-discord.md                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    OPTION B: Document Entire Project                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  /docs:discover                     Scan codebase, find all modules          │
│           │                                                                  │
│           ▼                                                                  │
│  /docs:plan                         Create ordered documentation plan        │
│           │                         → Outputs docs/plan.yml                 │
│           ▼                                                                  │
│  /docs:execute                      Run through plan, generate all docs      │
│                                     → Resume with --continue if interrupted  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         KEEP DOCS IN SYNC                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  # After implementing a feature:                                             │
│  /docs:update --base main           Detect changes, update affected docs     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Quick Commands

```bash
# Simple: Generate docs for one page
/docs:generate https://myapp.com/dashboard

# Flow: Document a code flow from description
/docs:flow "sync users from discord"
/docs:flow "import payments from csv"

# Batch: Document entire project
/docs:discover && /docs:plan && /docs:execute

# Maintain: Update after code changes
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

### `aidocs update`

Update aidocs-cli to the latest version.

```bash
aidocs update              # Update from PyPI
aidocs update --github     # Update from GitHub (latest)
```

**Options:**
| Option | Description |
|--------|-------------|
| `--github` | Install latest from GitHub instead of PyPI |

Automatically detects and uses the appropriate package manager (uv, pipx, or pip).

### `aidocs chunk`

Chunk markdown files for vector database import.

```bash
aidocs chunk                   # Chunk all files in docs/
aidocs chunk docs/users        # Chunk specific directory
aidocs chunk --force           # Re-chunk all files
aidocs chunk --dry             # Preview only
```

**Options:**
| Option | Description |
|--------|-------------|
| `--force, -f` | Re-chunk all files (ignore cache) |
| `--dry` | Preview without writing files |

**What it does:**
1. Scans directory for `.md` files
2. Splits at `##` headings into chunks
3. Creates `.chunks.json` files alongside each `.md`
4. Maintains `docs/.chunks/manifest.json` for change tracking

**Output structure:**
```
docs/
├── users/
│   ├── lifecycle.md
│   └── lifecycle.chunks.json    # Chunks for this file
├── campaigns/
│   ├── lifecycle.md
│   └── lifecycle.chunks.json
└── .chunks/
    └── manifest.json            # Tracking file
```

**Next step:** Run `/docs:sync` to generate embeddings and SQL

## Slash Commands

After running `aidocs init`, these commands are available in Claude Code:

| Command | Description | Requires Playwright |
|---------|-------------|---------------------|
| `/docs:init` | Configure project settings, credentials, output style | No |
| `/docs:generate <url>` | Generate docs for a single page with screenshots | Yes |
| `/docs:analyze <route>` | Analyze codebase for a route (no browser) | No |
| `/docs:batch` | Generate docs for multiple pages | Yes |
| `/docs:update` | Update docs based on git diff | Optional |
| `/docs:discover` | Scan codebase, discover all modules | No |
| `/docs:plan` | Create ordered documentation plan | No |
| `/docs:execute` | Execute plan, generate all docs | Yes |
| `/docs:explore <module>` | Interactive UI exploration with Playwright | Yes |
| `/docs:flow "<description>"` | Document a code flow from human description | Optional |
| `/docs:sync` | Generate embeddings and SQL for vector DB import | No |

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

### `/docs:discover`

Scan your codebase to discover all modules and their structure:

```bash
/docs:discover                     # Discover all modules
/docs:discover --dry               # Preview without saving
/docs:discover campaigns           # Analyze only one module
```

**What it analyzes:**
- Backend: Models, controllers, routes, validation rules
- Frontend: Pages, components, forms, state management
- Relationships: Foreign keys, ORM relationships, cross-module navigation

**Creates `docs/.knowledge/` with:**
```
docs/.knowledge/
├── _meta/
│   ├── project.json              # Project-level info
│   └── modules-index.json        # List of discovered modules
├── modules/
│   ├── campaigns/
│   │   ├── entity.json           # Fields, types, relationships
│   │   ├── routes.json           # API endpoints
│   │   ├── components.json       # UI components
│   │   └── validation.json       # Validation rules
│   └── users/
│       └── ...
└── relationships/                # Cross-module relationships
```

**Next step:** Run `/docs:plan` to create documentation plan

### `/docs:plan`

Create an ordered documentation plan based on discovered modules:

```bash
/docs:plan                         # Create plan interactively
/docs:plan --auto                  # Auto-generate plan (no prompts)
/docs:plan --show                  # Show existing plan
```

**What it does:**
1. Reads discovered modules from `docs/.knowledge/`
2. Analyzes dependencies and relationships
3. Suggests documentation order (core modules first)
4. Creates `docs/plan.yml` with the plan

**Output: `docs/plan.yml`**
```yaml
modules:
  - name: users
    priority: 1
    reason: "Core module - other modules depend on it"
    document:
      lifecycle: true
      include_errors: true
    status: pending

  - name: campaigns
    priority: 2
    document:
      lifecycle: true
      flows:
        - "duplicate campaign"
    status: pending

cross_module_flows:
  - name: "user registration to first campaign"
    modules: [users, campaigns]
    status: pending
```

**Next step:** Run `/docs:execute` to generate documentation

### `/docs:execute`

Execute the documentation plan and generate all docs:

```bash
/docs:execute                      # Execute full plan
/docs:execute --module campaigns   # Execute only one module
/docs:execute --continue           # Continue from where it stopped
/docs:execute --dry                # Preview what would be generated
```

**What it does:**
1. Reads `docs/plan.yml`
2. For each module in order:
   - Runs explore (if needed)
   - Generates lifecycle documentation
   - Captures screenshots
   - Writes to `docs/{module}/`
3. Updates plan status as it progresses
4. Generates cross-module flows last

**Output structure:**
```
docs/
├── index.md                    # Auto-generated with links
├── users/
│   ├── index.md               # Module overview
│   ├── lifecycle.md           # CRUD documentation
│   ├── user-registration-to-campaign.md  # Cross-module flow (first module)
│   └── images/
└── campaigns/
    ├── index.md
    ├── lifecycle.md
    ├── duplicate-campaign.md  # Custom flow
    └── images/
```

**Resume support:** If execution stops, run `/docs:execute --continue` to resume

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

### `/docs:flow "<description>"`

Document a code flow by analyzing your codebase from a natural language description. Generates mermaid diagrams, code snippets, and optional UI screenshots.

```bash
/docs:flow "sync users from discord"              # Backend integration flow
/docs:flow "import payments from csv"             # Import flow with UI
/docs:flow "how payments are processed"           # Processing flow
/docs:flow "webhook handling for stripe"          # Webhook flow
/docs:flow "user registration" --no-screenshots   # Skip UI screenshots
```

**What it does:**
1. Parses your description to extract keywords (entities, actions)
2. Searches the codebase for relevant files (jobs, services, controllers)
3. Identifies entry points (commands, jobs, webhooks, routes, UI buttons)
4. Traces the execution flow and builds a call graph
5. Generates a mermaid sequence diagram
6. Captures UI screenshots (if Playwright available and route detected)
7. Extracts code snippets with file:line references
8. Creates comprehensive markdown documentation

**Output:** `docs/flows/{kebab-case-title}.md`

**Example output for `/docs:flow "import payments from csv"`:**

```markdown
# Import Payments from CSV

## Overview
Import payment records from a CSV file into the system.

## UI Location
![Payroll Page](./images/import-payments-trigger.png)
Click the **"Import Payments"** button on the Payroll page.

## Flow Diagram
```mermaid
sequenceDiagram
    participant User
    participant Controller as PayrollController
    participant Job as ImportPaymentsJob
    participant DB as Database

    User->>Controller: POST /payroll/import
    Controller->>Job: dispatch()
    Job->>DB: Payment::create()
```

## Entry Points
| Trigger | Location | Command/Route |
|---------|----------|---------------|
| UI Button | /payroll | "Import Payments" button |
| API | POST /payroll/import | With CSV file |
| CLI | Artisan | `php artisan payments:import` |

## Step-by-Step
### 1. Upload CSV File
Location: `app/Http/Controllers/PayrollController.php:45`
```php
public function import(ImportPaymentsRequest $request)
{
    ImportPaymentsJob::dispatch($request->file('csv'));
}
```
...
```

**Screenshots are captured automatically when:**
- Playwright MCP is installed
- `urls.base` is configured in `docs/config.yml`
- A UI route is detected in the code (controller → route → view)

**No Playwright?** The command still works - generates code analysis, mermaid diagrams, and snippets without screenshots.

### `/docs:sync`

Generate embeddings and SQL for syncing documentation to a PostgreSQL vector database.

```bash
/docs:sync                    # Generate sync SQL (smart)
/docs:sync --dry              # Preview what would be synced
/docs:sync --force            # Re-sync all files
```

**Prerequisites:**
- Run `aidocs chunk` first to create chunk files
- Set `OPENAI_API_KEY` environment variable

**What it does:**
1. Reads chunk files from `docs/.chunks/manifest.json`
2. Compares against last sync to find changes
3. Generates embeddings via OpenAI API (only for new/changed chunks)
4. Creates `docs/.chunks/sync.sql` with INSERT statements

**Smart sync:**
- Unchanged files → Skip (no API calls)
- Changed files → Re-generate embeddings
- New files → Generate embeddings
- Deleted files → Add DELETE statements

**Output:**
```
📊 Sync Summary:
   Unchanged: 12 files (skipped)
   Changed: 2 files (8 chunks)
   New: 1 file (3 chunks)

📄 Generated: docs/.chunks/sync.sql

Run with:
   psql $DATABASE_URL -f docs/.chunks/sync.sql
```

## Knowledge Base

The intelligent commands build a `docs/.knowledge/` folder:

```
docs/.knowledge/
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

### For Single Flow (Quick)

```
/docs:flow "sync users from discord"    → Analyzes code, generates docs with diagrams
/docs:flow "import payments from csv"   → Includes UI screenshots if route detected
```

### For Entire Project (Batch)

```
/docs:discover               → Scans codebase, finds all modules
         ↓
/docs:plan                   → Creates ordered documentation plan
         ↓
/docs:execute                → Generates all docs with screenshots
```

### Example Session

```bash
# Option A: Document a specific flow
/docs:flow "sync users from discord"       # Backend integration
/docs:flow "import payments from csv"      # Import with UI screenshots
/docs:flow "how stripe webhooks work"      # Webhook handling

# Option B: Document entire project
/docs:discover                             # Find all modules
/docs:plan                                 # Create plan (docs/plan.yml)
/docs:execute                              # Generate all documentation

# Resume if interrupted
/docs:execute --continue

# After code changes
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

After running `/docs:init`, a `docs/config.yml` is created:

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
| `file` | Credentials stored in `docs/.auth` (gitignored) |
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
