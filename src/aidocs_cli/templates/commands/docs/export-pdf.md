---
name: docs:export-pdf
description: Export markdown documentation to PDF with table of contents using Playwright MCP
---

# Export Documentation to PDF

Convert a markdown file to a styled PDF with auto-generated table of contents.

**Usage:**
```
/docs:export-pdf <markdown-file> [--output <filename.pdf>]
/docs:export-pdf docs/pages/dashboard.md
/docs:export-pdf docs/flows/sync-users.md --output manual.pdf
```

**Arguments:**
- `<markdown-file>` - Path to the markdown file to convert
- `--output` - Optional custom output filename (default: same name as input)

**Output:** `docs/exports/{filename}.pdf`

**What it does:**
1. Reads the markdown file
2. Extracts H1/H2 headings to build a table of contents
3. Converts markdown to styled HTML
4. Uses Playwright MCP to render and export as PDF
5. Saves to `docs/exports/` directory

**Requirements:**
- Playwright MCP must be available

---

**Execute workflow:** `@.claude/workflows/docs/export-pdf/workflow.md`
