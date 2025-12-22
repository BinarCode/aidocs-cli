---
name: docs:flow
description: Document a code flow by analyzing the codebase from a human description. Includes mermaid diagrams, code snippets, and optional UI screenshots.
---

# Document a Code Flow

Analyze your codebase to document how a specific feature or process works based on a natural language description. Optionally captures UI screenshots if Playwright MCP is available.

**Usage:**
```
/docs:flow "<description>" [--no-screenshots]
/docs:flow "sync users from discord"
/docs:flow "import payments from csv"
/docs:flow "how payments are processed"
/docs:flow "webhook handling for stripe" --no-screenshots
```

**Arguments:**
- `"description"` - Natural language description of the flow to document (in quotes)
- `--no-screenshots` - Skip UI screenshot capture (faster, code-only)

**What it does:**
1. Parses your description to extract keywords and detect UI involvement
2. Searches the codebase for relevant files (jobs, services, controllers, etc.)
3. Identifies entry points (commands, jobs, webhooks, routes, UI buttons)
4. Traces the execution flow and builds a call graph
5. Generates a mermaid sequence diagram
6. **Captures UI screenshots** (if Playwright MCP available and route detected)
7. Extracts relevant code snippets with file:line references
8. Creates comprehensive markdown documentation

**Output:**
- `docs/flows/{kebab-case-title}.md` - Complete flow documentation
- `docs/flows/images/*.png` - UI screenshots (if captured)

**Example output for `/docs:flow "import payments from csv"`:**
- Overview of what the flow does
- **Screenshot of the Payroll page with "Import" button**
- **Screenshot of the import modal/form**
- Mermaid sequence diagram showing data flow
- Entry points (UI button, API endpoint, CLI command)
- Step-by-step code walkthrough with snippets
- Validation rules
- Related files table

**Screenshots are captured automatically when:**
- Playwright MCP is installed
- `urls.base` is configured in `docs/config.yml`
- A UI route is detected in the code (controller → route → view)

**No Playwright?** The command still works - just skips screenshots and documents code only.

---

**Execute workflow:** `@.claude/workflows/docs/flow/workflow.md`
