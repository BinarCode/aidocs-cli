"""Tests for docs_service module."""

from pathlib import Path

import pytest

from aidocs_cli.ui.docs_service import (
    build_markdown,
    list_docs,
    list_folders,
    parse_frontmatter,
    get_file_content,
    write_file,
)


@pytest.fixture
def docs_dir(tmp_path: Path) -> Path:
    """Create a temporary docs directory with sample files."""
    # Root file
    (tmp_path / "getting-started.md").write_text(
        '---\ntitle: "Getting Started"\npublished: true\n---\n\n# Getting Started\n\nHello world.\n'
    )

    # Nested folder
    section = tmp_path / "guides"
    section.mkdir()
    (section / "installation.md").write_text(
        '---\ntitle: "Installation"\ndescription: "How to install"\npublished: true\nnoindex: true\n---\n\n# Installation\n'
    )
    (section / "configuration.md").write_text("# Configuration\n\nNo frontmatter here.\n")

    # Deeper nesting
    advanced = section / "advanced"
    advanced.mkdir()
    (advanced / "scaling.md").write_text(
        '---\ntitle: "Scaling"\npublished: false\n---\n\n# Scaling\n'
    )

    # Ignored directories
    hidden = tmp_path / ".hidden"
    hidden.mkdir()
    (hidden / "secret.md").write_text("# Secret\n")

    underscore = tmp_path / "_drafts"
    underscore.mkdir()
    (underscore / "draft.md").write_text("# Draft\n")

    return tmp_path


class TestListDocs:
    def test_lists_all_markdown_files(self, docs_dir: Path):
        docs = list_docs(docs_dir)
        paths = [d["path"] for d in docs]
        assert "getting-started.md" in paths
        assert "guides/installation.md" in paths
        assert "guides/configuration.md" in paths
        assert "guides/advanced/scaling.md" in paths

    def test_excludes_hidden_and_underscore_dirs(self, docs_dir: Path):
        docs = list_docs(docs_dir)
        paths = [d["path"] for d in docs]
        assert not any(".hidden" in p for p in paths)
        assert not any("_drafts" in p for p in paths)

    def test_published_status(self, docs_dir: Path):
        docs = list_docs(docs_dir)
        by_path = {d["path"]: d for d in docs}
        assert by_path["getting-started.md"]["published"] is True
        assert by_path["guides/installation.md"]["published"] is True
        assert by_path["guides/configuration.md"]["published"] is False
        assert by_path["guides/advanced/scaling.md"]["published"] is False

    def test_empty_directory(self, tmp_path: Path):
        docs = list_docs(tmp_path)
        assert docs == []


class TestListFolders:
    def test_lists_all_folders(self, docs_dir: Path):
        folders = list_folders(docs_dir)
        assert "" in folders  # root
        assert "guides" in folders
        assert "guides/advanced" in folders

    def test_excludes_hidden_folders(self, docs_dir: Path):
        folders = list_folders(docs_dir)
        assert not any(".hidden" in f for f in folders)
        assert not any("_drafts" in f for f in folders)


class TestGetFileContent:
    def test_reads_existing_file(self, docs_dir: Path):
        content = get_file_content(docs_dir, "getting-started.md")
        assert "# Getting Started" in content

    def test_raises_on_missing_file(self, docs_dir: Path):
        with pytest.raises(FileNotFoundError):
            get_file_content(docs_dir, "nonexistent.md")


class TestWriteFile:
    def test_writes_new_file(self, docs_dir: Path):
        write_file(docs_dir, "new-page.md", "# New Page\n")
        assert (docs_dir / "new-page.md").read_text() == "# New Page\n"

    def test_creates_directories(self, docs_dir: Path):
        write_file(docs_dir, "new-section/deep/page.md", "# Deep\n")
        assert (docs_dir / "new-section" / "deep" / "page.md").read_text() == "# Deep\n"

    def test_overwrites_existing_file(self, docs_dir: Path):
        write_file(docs_dir, "getting-started.md", "# Updated\n")
        assert (docs_dir / "getting-started.md").read_text() == "# Updated\n"


class TestParseFrontmatter:
    def test_parses_full_frontmatter(self):
        raw = '---\ntitle: "My Title"\ndescription: "My Desc"\npublished: true\nnoindex: false\n---\n\n# Hello\n'
        result = parse_frontmatter(raw)
        assert result["meta"]["title"] == "My Title"
        assert result["meta"]["description"] == "My Desc"
        assert result["meta"]["published"] is True
        assert result["meta"]["noindex"] is False
        assert result["body"] == "# Hello\n"

    def test_no_frontmatter(self):
        raw = "# Just Markdown\n\nSome content.\n"
        result = parse_frontmatter(raw)
        assert result["meta"] == {}
        assert result["body"] == raw

    def test_incomplete_frontmatter(self):
        raw = "---\ntitle: test\nno closing\n"
        result = parse_frontmatter(raw)
        assert result["meta"] == {}
        assert result["body"] == raw

    def test_empty_frontmatter(self):
        raw = "---\n---\n\n# Content\n"
        result = parse_frontmatter(raw)
        assert result["meta"] == {}
        assert result["body"] == "# Content\n"


class TestBuildMarkdown:
    def test_build_with_meta(self):
        meta = {"title": "Hello", "published": True, "noindex": False}
        body = "# Hello\n"
        result = build_markdown(meta, body)
        assert result.startswith("---\n")
        assert 'title: "Hello"' in result
        assert "published: true" in result
        assert "noindex: false" in result
        assert result.endswith("# Hello\n")

    def test_build_without_meta(self):
        result = build_markdown({}, "# Hello\n")
        assert result == "# Hello\n"

    def test_roundtrip(self):
        meta = {"title": "Test", "description": "A test page", "published": True}
        body = "# Test\n\nSome content.\n"
        markdown = build_markdown(meta, body)
        parsed = parse_frontmatter(markdown)
        assert parsed["meta"]["title"] == "Test"
        assert parsed["meta"]["description"] == "A test page"
        assert parsed["meta"]["published"] is True
        assert parsed["body"] == body
