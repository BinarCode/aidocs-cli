# aidocs-cli

AI-powered documentation generator for web applications. Install docs commands into your Claude Code project.

## Installation

```bash
# Install globally with uv
uv tool install aidocs-cli --from git+https://github.com/binarcode/aidocs-cli.git

# Or install from PyPI (when published)
uv tool install aidocs-cli

# Or use pipx
pipx install aidocs-cli
```

## Quick Start

```bash
# Initialize in current directory
aidocs init .

# Or create a new project
aidocs init my-project

# Check your environment
aidocs check
```

## Commands

### `aidocs init [PROJECT_NAME]`

Initialize the docs module in a project.

```bash
# Current directory
aidocs init .

# New directory
aidocs init my-project

# Force overwrite existing files
aidocs init . --force

# Use with Cursor instead of Claude
aidocs init . --ai cursor
```

**Options:**
- `--ai` - AI assistant to configure for (`claude`, `cursor`, `copilot`). Default: `claude`
- `--force, -f` - Overwrite existing files
- `--no-git` - Skip git initialization

**What it does:**
1. Creates `.claude/commands/docs/` with slash command definitions
2. Creates `docs-workflows/` with workflow implementations
3. Updates `.gitignore` to exclude `.docs-auth`

### `aidocs check`

Check for required tools and dependencies.

```bash
aidocs check
```

**Checks for:**
- Git
- Claude Code CLI
- Python 3.11+
- uv
- npx (for Playwright MCP)

### `aidocs version`

Show version information.

```bash
aidocs version
```

## After Installation

Once installed, use these Claude Code slash commands:

```bash
# Initialize your project settings
/docs:init

# Generate documentation for a page
/docs:generate https://myapp.com/dashboard

# Analyze code without browser
/docs:analyze /campaigns

# Batch generate for multiple pages
/docs:batch --discover
```

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
# Clone the repository
git clone https://github.com/binarcode/aidocs-cli.git
cd aidocs-cli

# Install in development mode
uv pip install -e .

# Run commands
aidocs check
aidocs init test-project
```

## License

MIT
