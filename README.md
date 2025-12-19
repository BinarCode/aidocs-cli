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
