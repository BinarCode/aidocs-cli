"""FastAPI web application for the docs editor UI."""

from __future__ import annotations

import html
import os
import re
import subprocess
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .docs_service import (
    build_markdown,
    get_file_content,
    list_docs,
    list_folders,
    parse_frontmatter,
    write_file,
)
from .github_service import GitHubService

TEMPLATE_DIR = Path(__file__).parent / "templates"


RTL_LANGUAGES = {"he", "ar", "fa", "ur", "yi"}


def create_app(
    docs_dir: Path,
    github_token: str,
    github_repo: str,
    base_branch: str = "main",
    media_path: str | None = None,
    docs_prefix: str | None = None,
    base_path: str = "",
    languages: list[str] | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application."""
    owner, repo = github_repo.split("/", 1)
    github = GitHubService(
        token=github_token,
        owner=owner,
        repo=repo,
        base_branch=base_branch,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        github.close()

    app = FastAPI(title="Docs Editor", lifespan=lifespan)
    app.add_middleware(SessionMiddleware, secret_key=os.urandom(32).hex())

    def _repo_path(local_path: str) -> str:
        """Convert a local relative path to a GitHub repo path by prepending docs_prefix."""
        if docs_prefix:
            return f"{docs_prefix.rstrip('/')}/{local_path}"
        return local_path

    def _is_translation(name: str) -> bool:
        """Check if filename has a language suffix like .he.md, .ro.md."""
        if not languages or len(languages) < 2:
            return False
        for lang in languages[1:]:
            if name.endswith(f".{lang}.md"):
                return True
        return False

    def _build_tree_html(docs: list[dict]) -> str:
        tree: dict = {}
        for doc in docs:
            # Skip translation files in sidebar
            if _is_translation(doc["name"]):
                continue
            parts = doc["path"].split("/")
            current = tree
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    current.setdefault("__files", []).append({
                        "name": part,
                        "path": doc["path"],
                        "published": doc.get("published", False),
                    })
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
        return _render_tree(tree)

    def _render_tree(node: dict, depth: int = 0) -> str:
        result = ""
        padding = depth * 16

        folders = {k: v for k, v in node.items() if k != "__files"}
        for name in sorted(folders):
            children = folders[name]
            display_name = name.replace("-", " ")
            result += f'<li class="tree-folder">'
            result += f'<div class="tree-toggle flex items-center gap-1 px-2 py-1 rounded-md hover:bg-gray-100 cursor-pointer select-none" style="padding-left: {padding}px">'
            result += '<svg class="toggle-icon w-3.5 h-3.5 text-gray-400 transition rotate-90 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>'
            result += '<svg class="w-4 h-4 text-amber-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"/></svg>'
            result += f'<span class="text-xs font-medium text-gray-700 truncate">{html.escape(display_name)}</span>'
            result += "</div>"
            result += f'<ul class="list-none">{_render_tree(children, depth + 1)}</ul>'
            result += "</li>"

        files = node.get("__files", [])
        files = sorted(files, key=lambda f: f["name"])
        file_padding = padding + 20

        for file in files:
            name = file["name"]
            escaped_path = html.escape(file["path"])
            published = file.get("published", False)
            display_name = name.replace("-", " ").removesuffix(".md")
            text_color = "text-gray-600" if published else "text-gray-400"
            icon_color = "text-gray-400" if published else "text-gray-300"
            status_icon = (
                '<span class="flex-shrink-0" title="Published"><svg class="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg></span>'
                if published else
                '<span class="flex-shrink-0" title="Draft"><svg class="w-3 h-3 text-orange-400" fill="currentColor" viewBox="0 0 20 20"><circle cx="10" cy="10" r="4"/></svg></span>'
            )

            result += "<li>"
            result += f'<a href="#" class="tree-file flex items-center gap-1.5 px-2 py-1 rounded-md hover:bg-blue-50 hover:text-blue-700 {text_color} transition" style="padding-left: {file_padding}px" data-path="{escaped_path}">'
            result += f'<svg class="w-3.5 h-3.5 {icon_color} flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>'
            result += f'<span class="text-xs truncate">{html.escape(display_name)}</span>'
            result += status_icon
            result += "</a>"
            result += "</li>"

        return result

    def _flash(request: Request, category: str, message: str) -> None:
        if "flash" not in request.session:
            request.session["flash"] = {}
        request.session["flash"][category] = message

    def _get_flash(request: Request) -> dict:
        return request.session.pop("flash", {})

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        flash = _get_flash(request)
        try:
            docs = list_docs(docs_dir)
            tree_html = _build_tree_html(docs)
        except Exception as e:
            tree_html = ""
            flash["error"] = f"Error: {e}"

        template = (TEMPLATE_DIR / "index.html").read_text(encoding="utf-8")
        rendered = template.replace("{{ tree }}", tree_html)
        rendered = rendered.replace("{{ docs_prefix }}", str(docs_dir))
        rendered = rendered.replace("{{ base_path }}", base_path)

        success_html = ""
        if "success" in flash:
            success_html = f"""<div class="mb-4 rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-800 flex items-center gap-2">
                <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
                <span>{flash["success"]}</span></div>"""
        error_html = ""
        if "error" in flash:
            error_html = f"""<div class="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-800 flex items-center gap-2">
                <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>
                <span>{html.escape(flash["error"])}</span></div>"""
        rendered = rendered.replace("{{ flash_messages }}", success_html + error_html)

        return HTMLResponse(rendered)

    @app.get("/api/edit")
    async def api_edit(path: str = Query(...)):
        try:
            content = get_file_content(docs_dir, path)
        except FileNotFoundError:
            return JSONResponse({"error": "File not found"}, status_code=404)
        parsed = parse_frontmatter(content)
        return JSONResponse({
            "path": path,
            "title": parsed["meta"].get("title", ""),
            "description": parsed["meta"].get("description", ""),
            "keywords": parsed["meta"].get("keywords", ""),
            "noindex": parsed["meta"].get("noindex", False),
            "published": parsed["meta"].get("published", False),
            "content": parsed["body"],
        })

    @app.get("/api/folders")
    async def api_folders():
        folders = list_folders(docs_dir)
        return JSONResponse({"folders": folders})

    @app.get("/api/languages")
    async def api_languages():
        langs = languages or []
        rtl = [l for l in langs if l in RTL_LANGUAGES]
        return JSONResponse({"languages": langs, "rtl": rtl})

    @app.get("/api/translations")
    async def api_translations(path: str = Query(...)):
        """Given a default-lang page path, return which translations exist."""
        if not languages or len(languages) < 2:
            return JSONResponse({"translations": {}})

        stem = Path(path).stem  # e.g. "billing"
        parent = str(Path(path).parent)  # e.g. "account-and-billing/manage-your-account-and-billing"

        result = {}
        for lang in languages:
            if lang == languages[0]:
                full = docs_dir / path
                result[lang] = {"exists": full.exists(), "path": path, "rtl": lang in RTL_LANGUAGES}
            else:
                lang_filename = f"{stem}.{lang}.md"
                lang_path = f"{parent}/{lang_filename}" if parent != "." else lang_filename
                full = docs_dir / lang_path
                result[lang] = {"exists": full.exists(), "path": lang_path, "rtl": lang in RTL_LANGUAGES}

        return JSONResponse({"translations": result})

    @app.get("/api/default-pages")
    async def api_default_pages():
        """List default-language pages (no lang suffix) for translation source."""
        if not languages:
            return JSONResponse({"pages": []})
        docs = list_docs(docs_dir)
        non_default_suffixes = [f".{lang}.md" for lang in languages[1:]]
        pages = []
        for doc in docs:
            # Skip non-default language files
            if any(doc["name"].endswith(s) for s in non_default_suffixes):
                continue
            # stem without .md
            stem = doc["name"].removesuffix(".md")
            folder = str(Path(doc["path"]).parent)
            if folder == ".":
                folder = ""
            pages.append({
                "path": doc["path"],
                "stem": stem,
                "folder": folder,
                "title": stem.replace("-", " ").title(),
            })
        return JSONResponse({"pages": pages})

    @app.post("/api/store")
    async def api_store(request: Request):
        form = await request.form()
        folder = (form.get("folder", "") or "").rstrip("/")
        filename = form.get("filename", "")
        content_body = form.get("content", "")

        if not filename or not re.match(r"^[a-z0-9-]+$", filename):
            return JSONResponse({"error": "Invalid filename"}, status_code=422)

        meta = {}
        for key in ("title", "description", "keywords"):
            val = form.get(key, "")
            if val:
                meta[key] = val
        if form.get("noindex") == "1":
            meta["noindex"] = True
        if form.get("published") == "1":
            meta["published"] = True

        file_content = build_markdown(meta, content_body)
        path = f"{folder}/{filename}.md" if folder else f"{filename}.md"

        section = path.split("/")[0] if "/" in path else ""
        commit_msg = f"docs({section}): add {filename}" if section else f"docs: add {filename}"

        try:
            write_file(docs_dir, path, file_content)
            _flash(request, "success", f"Page saved: {path}")
        except Exception as e:
            _flash(request, "error", f"Failed: {e}")

        return RedirectResponse(f"{base_path}/", status_code=303)

    @app.post("/api/update")
    async def api_update(request: Request):
        form = await request.form()
        path = form.get("path", "")
        content_body = form.get("content", "")

        if not path or not content_body:
            return JSONResponse({"error": "Path and content required"}, status_code=422)

        meta = {}
        for key in ("title", "description", "keywords"):
            val = form.get(key, "")
            if val:
                meta[key] = val
        if form.get("noindex") == "1":
            meta["noindex"] = True
        if form.get("published") == "1":
            meta["published"] = True

        # Auto-set direction for RTL languages
        if languages:
            for lang in languages:
                if path.endswith(f".{lang}.md") and lang in RTL_LANGUAGES:
                    meta["direction"] = "rtl"
                    break

        file_content = build_markdown(meta, content_body)

        section = path.split("/")[0] if "/" in path else ""
        basename = Path(path).stem
        commit_msg = f"docs({section}): update {basename}" if section else f"docs: update {basename}"

        try:
            write_file(docs_dir, path, file_content)
            return JSONResponse({"success": True, "message": f"Page saved: {path}"})
        except Exception as e:
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    @app.post("/api/delete")
    async def api_delete(request: Request):
        form = await request.form()
        path = form.get("path", "")

        if not path:
            return JSONResponse({"error": "Path required"}, status_code=422)

        section = path.split("/")[0] if "/" in path else ""
        basename = Path(path).stem
        commit_msg = f"docs({section}): delete {basename}" if section else f"docs: delete {basename}"

        try:
            pr_url = github.create_pr_for_delete(_repo_path(path), commit_msg)
            _flash(request, "success", f'Delete PR created: <a href="{pr_url}" target="_blank" class="underline font-medium">{pr_url}</a>')
        except Exception as e:
            _flash(request, "error", f"Failed to create delete PR: {e}")

        return RedirectResponse(f"{base_path}/", status_code=303)

    @app.get("/api/changes")
    async def api_changes():
        """List files with local changes (git diff)."""
        repo_root = docs_dir
        while repo_root != repo_root.parent:
            if (repo_root / ".git").exists():
                break
            repo_root = repo_root.parent
        else:
            return JSONResponse({"changes": []})

        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD", "--", str(docs_dir)],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            untracked = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard", "--", str(docs_dir)],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            changed = [f for f in result.stdout.strip().splitlines() if f]
            new = [f for f in untracked.stdout.strip().splitlines() if f]
            return JSONResponse({"changes": changed + new})
        except Exception:
            return JSONResponse({"changes": []})

    @app.post("/api/publish")
    async def api_publish(request: Request):
        """Create a single PR with all local changes."""
        repo_root = docs_dir
        while repo_root != repo_root.parent:
            if (repo_root / ".git").exists():
                break
            repo_root = repo_root.parent
        else:
            _flash(request, "error", "Not a git repository")
            return RedirectResponse(f"{base_path}/", status_code=303)

        try:
            # Get changed + untracked files
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD", "--", str(docs_dir)],
                cwd=str(repo_root),
                capture_output=True, text=True, timeout=10,
            )
            untracked = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard", "--", str(docs_dir)],
                cwd=str(repo_root),
                capture_output=True, text=True, timeout=10,
            )
            changed = [f for f in result.stdout.strip().splitlines() if f]
            new = [f for f in untracked.stdout.strip().splitlines() if f]
            all_files = list(set(changed + new))

            if not all_files:
                _flash(request, "error", "No local changes to publish")
                return RedirectResponse(f"{base_path}/", status_code=303)

            # Build file list for batch PR
            files = []
            for file_path in all_files:
                full = repo_root / file_path
                if not full.exists() or not full.suffix == ".md":
                    continue
                content = full.read_text(encoding="utf-8")
                # Try to get existing file SHA from GitHub
                sha = None
                try:
                    sha = github._get_file_sha(file_path)
                except Exception:
                    pass
                files.append({"path": file_path, "content": content, "sha": sha})

            if not files:
                _flash(request, "error", "No doc changes to publish")
                return RedirectResponse(f"{base_path}/", status_code=303)

            count = len(files)
            commit_msg = f"docs: update {count} page{'s' if count > 1 else ''}"
            pr_url = github.create_pr_for_batch(files, commit_msg)
            _flash(request, "success", f'PR created with {count} change{"s" if count > 1 else ""}: <a href="{pr_url}" target="_blank" class="underline font-medium">{pr_url}</a>')
        except Exception as e:
            _flash(request, "error", f"Publish failed: {e}")

        return RedirectResponse(f"{base_path}/", status_code=303)

    @app.post("/api/upload-image")
    async def api_upload_image(
        image: UploadFile,
        doc_path: str = Form(...),
    ):
        parts = doc_path.split("/")
        section = parts[0] if parts else ""
        page_slug = Path(doc_path).stem

        random_id = uuid.uuid4().hex[:10]
        original_name = Path(image.filename or "image").stem
        ext = Path(image.filename or "image.png").suffix
        slug_name = re.sub(r"[^a-z0-9]+", "-", original_name.lower()).strip("-")
        image_name = f"{random_id}-{slug_name}{ext}"

        if media_path:
            upload_dir = Path(media_path) / section / f"media-{page_slug}"
        else:
            upload_dir = docs_dir / section / f"media-{page_slug}"
        upload_dir.mkdir(parents=True, exist_ok=True)

        image_file_path = upload_dir / image_name
        file_content = await image.read()
        image_file_path.write_bytes(file_content)

        repo_path = str(image_file_path)
        if media_path:
            markdown_path = f"/docs-media/{section}/media-{page_slug}/{image_name}"
        else:
            markdown_path = str(image_file_path.relative_to(docs_dir))

        return JSONResponse({
            "markdown": f"![{slug_name}]({markdown_path})",
            "repo_path": repo_path,
        })

    @app.post("/api/sync")
    async def api_sync():
        """Pull latest changes from the base branch."""
        # Find the git repo root by walking up from docs_dir
        repo_root = docs_dir
        while repo_root != repo_root.parent:
            if (repo_root / ".git").exists():
                break
            repo_root = repo_root.parent
        else:
            return JSONResponse({"success": False, "error": "Not a git repository"})

        try:
            # Fetch latest from remote
            result = subprocess.run(
                ["git", "fetch", "origin", base_branch],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                return JSONResponse({"success": False, "error": result.stderr.strip()})

            # Reset local to match remote (discards local edits — safe since all changes go through PRs)
            result = subprocess.run(
                ["git", "reset", "--hard", f"origin/{base_branch}"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                return JSONResponse({"success": False, "error": result.stderr.strip()})

            return JSONResponse({"success": True, "output": result.stdout.strip()})
        except subprocess.TimeoutExpired:
            return JSONResponse({"success": False, "error": "Git operation timed out"})
        except Exception as e:
            return JSONResponse({"success": False, "error": str(e)})

    # Serve media files (images referenced as /docs-media/... in markdown)
    if media_path:
        media_dir = Path(media_path)
        if media_dir.is_dir():
            app.mount("/docs-media", StaticFiles(directory=str(media_dir)), name="docs-media")

    return app
