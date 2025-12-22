---
name: docs-export-pdf
description: Export markdown documentation to PDF with table of contents using Playwright MCP
---

# PDF Export Workflow

**Goal:** Convert a markdown documentation file to a styled PDF with auto-generated table of contents.

**Your Role:** You will read the markdown file, build an HTML document with TOC, and use Playwright MCP to render and export it as a PDF.

---

## ARGUMENTS PARSING

Parse the arguments passed to this workflow. Expected format:
```
/docs:export-pdf <markdown-file> [--output <filename.pdf>]
```

Examples:
```
/docs:export-pdf docs/pages/dashboard.md
/docs:export-pdf docs/flows/sync-users.md --output manual.pdf
```

Extract:
- `markdown_file` (required) - Path to the markdown file
- `--output` (optional) - Custom output filename

If no file provided, ask:
```
Please specify the markdown file to export.

Example:
  /docs:export-pdf docs/pages/dashboard.md
```

---

## STEP 1: VALIDATE INPUT

Check that the file exists and is a markdown file.

```
📄 Input file: docs/pages/dashboard.md
```

If file doesn't exist:
```
❌ File not found: docs/pages/dashboard.md

Available docs:
  • docs/pages/dashboard.md
  • docs/pages/settings.md
  • docs/flows/sync-users.md
```

---

## STEP 2: READ MARKDOWN

Read the entire markdown file content.

Display progress:
```
📖 Reading: docs/pages/dashboard.md
   Size: 4.2 KB
   Lines: 156
```

---

## STEP 3: EXTRACT HEADINGS FOR TOC

Parse the markdown to extract all H1 (`#`) and H2 (`##`) headings.

For each heading:
1. Extract the text
2. Generate an anchor ID (lowercase, replace spaces with hyphens)
3. Track the hierarchy (H1 = top level, H2 = nested)

Example extraction:
```
📑 Table of Contents:
   • Dashboard Overview
     • Key Metrics
     • Navigation
   • Components
     • Charts
     • Tables
   • Configuration
```

---

## STEP 4: BUILD HTML DOCUMENT

Convert the markdown content to HTML and wrap it in a styled HTML document.

### 4.1 Generate TOC HTML

Build nested `<ul>` list from extracted headings:

```html
<div class="toc">
  <h2>Table of Contents</h2>
  <ul>
    <li><a href="#dashboard-overview">Dashboard Overview</a>
      <ul>
        <li><a href="#key-metrics">Key Metrics</a></li>
        <li><a href="#navigation">Navigation</a></li>
      </ul>
    </li>
    <li><a href="#components">Components</a>
      <ul>
        <li><a href="#charts">Charts</a></li>
        <li><a href="#tables">Tables</a></li>
      </ul>
    </li>
  </ul>
</div>
```

### 4.2 Convert Markdown to HTML

Convert markdown elements:
- Headings → `<h1>`, `<h2>`, etc. with `id` attributes for TOC links
- Code blocks → `<pre><code>` with syntax highlighting class
- Tables → `<table>` with proper structure
- Images → `<img>` with full paths (resolve relative paths)
- Links → `<a>` tags

### 4.3 Assemble Full HTML

Use this template:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Document Title}</title>
  <style>
    * {
      box-sizing: border-box;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.7;
      color: #1a1a1a;
      max-width: 800px;
      margin: 0 auto;
      padding: 40px 20px;
      font-size: 14px;
    }

    /* Headings */
    h1 {
      font-size: 28px;
      border-bottom: 2px solid #e1e1e1;
      padding-bottom: 10px;
      margin-top: 40px;
      page-break-before: always;
    }
    h1:first-of-type {
      page-break-before: avoid;
      margin-top: 0;
    }
    h2 {
      font-size: 22px;
      margin-top: 30px;
      color: #2c3e50;
    }
    h3 {
      font-size: 18px;
      margin-top: 25px;
    }

    /* Table of Contents */
    .toc {
      background: #f8f9fa;
      border: 1px solid #e9ecef;
      border-radius: 8px;
      padding: 20px 30px;
      margin-bottom: 40px;
    }
    .toc h2 {
      margin-top: 0;
      font-size: 18px;
      color: #495057;
    }
    .toc ul {
      list-style: none;
      padding-left: 0;
      margin: 0;
    }
    .toc ul ul {
      padding-left: 20px;
    }
    .toc li {
      margin: 8px 0;
    }
    .toc a {
      color: #0066cc;
      text-decoration: none;
    }
    .toc a:hover {
      text-decoration: underline;
    }

    /* Code blocks */
    pre {
      background: #f5f5f5;
      border: 1px solid #e1e1e1;
      border-radius: 6px;
      padding: 16px;
      overflow-x: auto;
      font-size: 13px;
      line-height: 1.5;
    }
    code {
      font-family: 'SF Mono', 'Fira Code', 'Monaco', 'Consolas', monospace;
      font-size: 13px;
    }
    p code, li code {
      background: #f0f0f0;
      padding: 2px 6px;
      border-radius: 4px;
    }

    /* Tables */
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      font-size: 13px;
    }
    th, td {
      border: 1px solid #ddd;
      padding: 10px 12px;
      text-align: left;
    }
    th {
      background: #f5f5f5;
      font-weight: 600;
    }
    tr:nth-child(even) {
      background: #fafafa;
    }

    /* Images */
    img {
      max-width: 100%;
      height: auto;
      border-radius: 4px;
      margin: 15px 0;
    }

    /* Lists */
    ul, ol {
      padding-left: 25px;
    }
    li {
      margin: 6px 0;
    }

    /* Blockquotes */
    blockquote {
      border-left: 4px solid #0066cc;
      margin: 20px 0;
      padding: 10px 20px;
      background: #f8f9fa;
      color: #555;
    }

    /* Links */
    a {
      color: #0066cc;
    }

    /* Print styles */
    @media print {
      body {
        padding: 0;
      }
      .toc {
        page-break-after: always;
      }
      pre {
        white-space: pre-wrap;
        word-wrap: break-word;
      }
    }
  </style>
</head>
<body>
  {TOC_HTML}

  {CONTENT_HTML}

  <footer style="margin-top: 60px; padding-top: 20px; border-top: 1px solid #e1e1e1; color: #666; font-size: 12px;">
    Generated by /docs:export-pdf
  </footer>
</body>
</html>
```

Display progress:
```
🔨 Building HTML document...
   TOC entries: 8
   Code blocks: 5
   Images: 3
   Tables: 2
```

---

## STEP 5: RESOLVE IMAGE PATHS

For any images in the markdown:
1. Check if path is relative
2. Resolve to absolute file path
3. Convert to base64 data URI for embedding in PDF

```
🖼️ Processing images...
   • ./images/dashboard.png → embedded
   • ./images/chart.png → embedded
```

If image not found:
```
⚠️ Image not found: ./images/missing.png
   Skipping...
```

---

## STEP 6: RENDER PDF WITH PLAYWRIGHT

Use Playwright MCP to render the HTML and export as PDF.

### 6.1 Check Playwright MCP

Verify Playwright MCP is available. If not:
```
❌ Playwright MCP not available

To export PDFs, please install Playwright MCP:
  https://github.com/anthropics/mcp-playwright

Alternative: Save the HTML and convert manually.
```

### 6.2 Create Browser Page

```
🌐 Starting Playwright...
   Creating browser page...
```

### 6.3 Load HTML Content

Set the page content to the generated HTML.

### 6.4 Wait for Resources

Wait for any images or fonts to load:
```
⏳ Waiting for resources to load...
```

### 6.5 Export to PDF

Use Playwright's page.pdf() with these options:

```javascript
{
  format: 'A4',
  printBackground: true,
  margin: {
    top: '1cm',
    bottom: '1cm',
    left: '1cm',
    right: '1cm'
  },
  displayHeaderFooter: false
}
```

Display progress:
```
🖨️ Rendering PDF...
   Format: A4
   Margins: 1cm
```

---

## STEP 7: SAVE PDF FILE

### 7.1 Create Output Directory

Ensure `docs/exports/` directory exists.

### 7.2 Determine Output Path

- If `--output` provided: use that filename
- Otherwise: use input filename with `.pdf` extension

```
📁 Output: docs/exports/dashboard.pdf
```

### 7.3 Save File

Write the PDF data to the output file.

---

## STEP 8: COMPLETION SUMMARY

Display final summary:

```
✅ PDF Export Complete!

📄 Input:  docs/pages/dashboard.md
📁 Output: docs/exports/dashboard.pdf
📊 Size:   245 KB

📑 Contents:
   • Table of Contents (8 entries)
   • 5 code blocks
   • 3 images
   • 2 tables

Open with:
  open docs/exports/dashboard.pdf
```

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| File not found | List available docs, suggest correct path |
| Not a markdown file | Show error, suggest .md file |
| Playwright MCP unavailable | Show install instructions, offer HTML export |
| Image not found | Skip with warning, continue export |
| PDF save failed | Check permissions, suggest alternative path |
| Empty markdown | Show warning, create minimal PDF |

---

## TIPS

- Large documents may take longer to render
- Complex tables might need manual adjustment
- Code blocks are automatically wrapped for print
- Images are embedded as base64 for portability
- The TOC links work within the PDF for navigation
