---
name: docs:flow
description: Document a feature with screenshots and step-by-step instructions. Use --technical for developer-focused output.
---

# Document a Code Flow

Create user-friendly documentation for a feature based on a natural language description. Captures UI screenshots and generates step-by-step guides.

**Usage:**
```
/docs:flow "<description>"                    # User-focused (default)
/docs:flow "<description>" --technical        # Developer-focused
/docs:flow "<description>" --no-screenshots   # Skip screenshots
```

**Examples:**
```
/docs:flow "how to create employees"              # End-user guide with screenshots
/docs:flow "import payments from csv"             # End-user guide with screenshots
/docs:flow "payment webhook handling" --technical # Developer docs with code
/docs:flow "sync users" --no-screenshots          # Quick, no screenshots
```

**Arguments:**
- `"description"` - Natural language description of the flow (in quotes)
- `--technical` - Developer-focused output with code snippets, file paths, diagrams
- `--no-screenshots` - Skip UI screenshot capture

**Output modes:**

| Mode | Output | Audience |
|------|--------|----------|
| Default | Screenshots, plain English, step-by-step | End users |
| `--technical` | Code snippets, file paths, mermaid diagrams | Developers |

**Default output (user-focused):**
- "How to..." title
- Before You Start (prerequisites)
- Step-by-step instructions with screenshots
- What Happens Next
- Troubleshooting

**Technical output (`--technical`):**
- Architecture diagram (mermaid)
- Entry points table
- Code snippets with file:line references
- Database operations
- Events and configuration

**Output location:**
- `docs/flows/{kebab-case-title}.md`
- `docs/flows/images/*.png` (screenshots)

---

**Execute workflow:** `@.claude/workflows/docs/flow/workflow.md`
