"""PDF export functionality for markdown documentation."""

import re
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Optional


def extract_headings(markdown_content: str) -> list[dict]:
    """Extract H1 and H2 headings from markdown for TOC."""
    headings = []
    lines = markdown_content.split("\n")

    for line in lines:
        if line.startswith("# "):
            text = line[2:].strip()
            anchor = text.lower().replace(" ", "-").replace(".", "").replace(",", "")
            anchor = re.sub(r"[^a-z0-9-]", "", anchor)
            headings.append({"level": 1, "text": text, "anchor": anchor})
        elif line.startswith("## "):
            text = line[3:].strip()
            anchor = text.lower().replace(" ", "-").replace(".", "").replace(",", "")
            anchor = re.sub(r"[^a-z0-9-]", "", anchor)
            headings.append({"level": 2, "text": text, "anchor": anchor})

    return headings


def generate_toc_html(headings: list[dict]) -> str:
    """Generate HTML table of contents from headings."""
    if not headings:
        return ""

    html = '<div class="toc"><h2>Table of Contents</h2><ul>'

    for h in headings:
        indent = "  " if h["level"] == 2 else ""
        html += f'{indent}<li class="toc-h{h["level"]}"><a href="#{h["anchor"]}">{h["text"]}</a></li>'

    html += "</ul></div>"
    return html


def markdown_to_html(markdown_content: str) -> str:
    """Convert markdown to HTML with proper heading IDs."""
    lines = markdown_content.split("\n")
    html_lines = []
    in_code_block = False
    code_lang = ""
    code_content = []
    in_table = False
    table_rows = []

    for line in lines:
        # Handle code blocks
        if line.startswith("```"):
            if in_code_block:
                # End code block
                code_html = "\n".join(code_content)
                html_lines.append(f'<pre><code class="language-{code_lang}">{code_html}</code></pre>')
                in_code_block = False
                code_content = []
            else:
                # Start code block
                in_code_block = True
                code_lang = line[3:].strip() or "text"
            continue

        if in_code_block:
            # Escape HTML in code
            escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            code_content.append(escaped)
            continue

        # Handle tables
        if "|" in line and not line.strip().startswith("```"):
            if line.strip().replace("-", "").replace("|", "").replace(" ", "") == "":
                # This is the separator row, skip it
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if cells:
                if not in_table:
                    in_table = True
                    table_rows = []
                table_rows.append(cells)
            continue
        elif in_table:
            # End table
            if table_rows:
                html_lines.append('<table>')
                for i, row in enumerate(table_rows):
                    tag = "th" if i == 0 else "td"
                    html_lines.append("<tr>")
                    for cell in row:
                        html_lines.append(f"<{tag}>{cell}</{tag}>")
                    html_lines.append("</tr>")
                html_lines.append('</table>')
            in_table = False
            table_rows = []

        # Handle headings
        if line.startswith("# "):
            text = line[2:].strip()
            anchor = text.lower().replace(" ", "-").replace(".", "").replace(",", "")
            anchor = re.sub(r"[^a-z0-9-]", "", anchor)
            html_lines.append(f'<h1 id="{anchor}">{text}</h1>')
        elif line.startswith("## "):
            text = line[3:].strip()
            anchor = text.lower().replace(" ", "-").replace(".", "").replace(",", "")
            anchor = re.sub(r"[^a-z0-9-]", "", anchor)
            html_lines.append(f'<h2 id="{anchor}">{text}</h2>')
        elif line.startswith("### "):
            text = line[4:].strip()
            html_lines.append(f'<h3>{text}</h3>')
        elif line.startswith("#### "):
            text = line[5:].strip()
            html_lines.append(f'<h4>{text}</h4>')
        elif line.startswith("- "):
            html_lines.append(f'<li>{line[2:]}</li>')
        elif line.startswith("* "):
            html_lines.append(f'<li>{line[2:]}</li>')
        elif line.strip().startswith("!["):
            # Image: ![alt](src)
            match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
            if match:
                alt, src = match.groups()
                html_lines.append(f'<img src="{src}" alt="{alt}">')
        elif line.strip():
            # Regular paragraph - handle inline formatting
            text = line
            # Bold
            text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
            # Italic
            text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
            # Inline code
            text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
            # Links
            text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
            html_lines.append(f'<p>{text}</p>')
        else:
            html_lines.append("")

    # Close any remaining table
    if in_table and table_rows:
        html_lines.append('<table>')
        for i, row in enumerate(table_rows):
            tag = "th" if i == 0 else "td"
            html_lines.append("<tr>")
            for cell in row:
                html_lines.append(f"<{tag}>{cell}</{tag}>")
            html_lines.append("</tr>")
        html_lines.append('</table>')

    return "\n".join(html_lines)


def build_html_document(content_html: str, toc_html: str, title: str) -> str:
    """Build a complete HTML document with styling."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.7;
      color: #1a1a1a;
      max-width: 800px;
      margin: 0 auto;
      padding: 40px 20px;
      font-size: 14px;
    }}
    h1 {{
      font-size: 28px;
      border-bottom: 2px solid #e1e1e1;
      padding-bottom: 10px;
      margin-top: 40px;
      page-break-before: always;
    }}
    h1:first-of-type {{ page-break-before: avoid; margin-top: 0; }}
    h2 {{
      font-size: 22px;
      margin-top: 30px;
      color: #2c3e50;
    }}
    h3 {{ font-size: 18px; margin-top: 25px; }}
    h4 {{ font-size: 16px; margin-top: 20px; }}
    .toc {{
      background: #f8f9fa;
      border: 1px solid #e9ecef;
      border-radius: 8px;
      padding: 20px 30px;
      margin-bottom: 40px;
      page-break-after: always;
    }}
    .toc h2 {{
      margin-top: 0;
      font-size: 18px;
      color: #495057;
    }}
    .toc ul {{
      list-style: none;
      padding-left: 0;
      margin: 0;
    }}
    .toc li {{ margin: 8px 0; }}
    .toc .toc-h2 {{ padding-left: 20px; }}
    .toc a {{
      color: #0066cc;
      text-decoration: none;
    }}
    pre {{
      background: #f5f5f5;
      border: 1px solid #e1e1e1;
      border-radius: 6px;
      padding: 16px;
      overflow-x: auto;
      font-size: 13px;
      line-height: 1.5;
      white-space: pre-wrap;
      word-wrap: break-word;
    }}
    code {{
      font-family: 'SF Mono', 'Fira Code', 'Monaco', 'Consolas', monospace;
      font-size: 13px;
    }}
    p code, li code {{
      background: #f0f0f0;
      padding: 2px 6px;
      border-radius: 4px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      font-size: 13px;
    }}
    th, td {{
      border: 1px solid #ddd;
      padding: 10px 12px;
      text-align: left;
    }}
    th {{ background: #f5f5f5; font-weight: 600; }}
    tr:nth-child(even) {{ background: #fafafa; }}
    img {{
      max-width: 100%;
      height: auto;
      border-radius: 4px;
      margin: 15px 0;
    }}
    ul, ol {{ padding-left: 25px; }}
    li {{ margin: 6px 0; }}
    a {{ color: #0066cc; }}
    footer {{
      margin-top: 60px;
      padding-top: 20px;
      border-top: 1px solid #e1e1e1;
      color: #666;
      font-size: 12px;
    }}
  </style>
</head>
<body>
  {toc_html}
  {content_html}
  <footer>Generated by aidocs export-pdf</footer>
</body>
</html>'''


def resolve_image_paths(html: str, base_dir: Path) -> str:
    """Convert relative image paths to absolute file:// URLs."""
    def replace_src(match: re.Match) -> str:
        src = match.group(1)
        if src.startswith(("http://", "https://", "file://", "data:")):
            return match.group(0)

        # Resolve relative path
        img_path = base_dir / src
        if img_path.exists():
            return f'src="file://{img_path.absolute()}"'
        return match.group(0)

    return re.sub(r'src="([^"]+)"', replace_src, html)


def export_pdf_with_playwright(html_path: Path, output_path: Path) -> bool:
    """Use Playwright via npx to generate PDF."""
    # Create a simple Node.js script to generate PDF
    script = f'''
const {{ chromium }} = require('playwright');

(async () => {{
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://{html_path.absolute()}');
  await page.pdf({{
    path: '{output_path.absolute()}',
    format: 'A4',
    printBackground: true,
    margin: {{ top: '1cm', bottom: '1cm', left: '1cm', right: '1cm' }}
  }});
  await browser.close();
}})();
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write(script)
        script_path = f.name

    try:
        result = subprocess.run(
            ["npx", "playwright", "test", "--browser=chromium", "-e", f"node {script_path}"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Try direct node execution instead
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Path.home(),
        )
        return result.returncode == 0
    except Exception:
        return False
    finally:
        Path(script_path).unlink(missing_ok=True)


def export_pdf_with_chrome(html_path: Path, output_path: Path) -> bool:
    """Use Chrome/Chromium headless to generate PDF."""
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "google-chrome",
        "chromium",
        "chromium-browser",
    ]

    chrome_path = None
    for path in chrome_paths:
        if Path(path).exists() or subprocess.run(["which", path], capture_output=True).returncode == 0:
            chrome_path = path
            break

    if not chrome_path:
        return False

    try:
        result = subprocess.run(
            [
                chrome_path,
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                f"--print-to-pdf={output_path.absolute()}",
                f"file://{html_path.absolute()}",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode == 0 and output_path.exists()
    except Exception:
        return False


def export_markdown_to_pdf(
    markdown_path: Path,
    output_path: Optional[Path] = None,
    on_status: Optional[Callable[[str], None]] = None,
) -> dict:
    """
    Export a markdown file to PDF.

    Args:
        markdown_path: Path to the markdown file
        output_path: Optional output path (default: docs/exports/{name}.pdf)
        on_status: Optional callback for status messages

    Returns:
        dict with success, output_path, and stats
    """
    def status(msg: str) -> None:
        if on_status:
            on_status(msg)

    if not markdown_path.exists():
        return {"success": False, "error": f"File not found: {markdown_path}"}

    if not markdown_path.suffix == ".md":
        return {"success": False, "error": "File must be a .md file"}

    status(f"Reading {markdown_path.name}...")

    # Read markdown
    content = markdown_path.read_text(encoding="utf-8")

    # Extract title from first H1
    title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else markdown_path.stem

    # Extract headings for TOC
    status("Extracting table of contents...")
    headings = extract_headings(content)
    toc_html = generate_toc_html(headings)

    # Convert markdown to HTML
    status("Converting to HTML...")
    content_html = markdown_to_html(content)

    # Build full document
    html = build_html_document(content_html, toc_html, title)

    # Resolve image paths
    html = resolve_image_paths(html, markdown_path.parent)

    # Determine output path
    if output_path is None:
        exports_dir = markdown_path.parent.parent / "exports"
        if not exports_dir.exists():
            exports_dir = Path("docs/exports")
        exports_dir.mkdir(parents=True, exist_ok=True)
        output_path = exports_dir / f"{markdown_path.stem}.pdf"
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save HTML temporarily
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        html_path = Path(f.name)

    try:
        status("Rendering PDF...")

        # Try Chrome first (most reliable)
        success = export_pdf_with_chrome(html_path, output_path)

        if not success:
            # Try Playwright
            success = export_pdf_with_playwright(html_path, output_path)

        if not success:
            return {
                "success": False,
                "error": "Could not generate PDF. Please install Chrome/Chromium or Playwright.",
            }

        # Get file size
        size_kb = output_path.stat().st_size / 1024

        return {
            "success": True,
            "output_path": str(output_path),
            "stats": {
                "toc_entries": len(headings),
                "size_kb": round(size_kb, 1),
                "title": title,
            },
        }

    finally:
        html_path.unlink(missing_ok=True)
