"""Tests for the FastAPI docs editor UI application."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from aidocs_cli.ui.app import create_app


@pytest.fixture
def docs_dir(tmp_path: Path) -> Path:
    """Create a temporary docs directory with sample files."""
    (tmp_path / "getting-started.md").write_text(
        '---\ntitle: "Getting Started"\npublished: true\n---\n\n# Getting Started\n\nHello world.\n'
    )

    guides = tmp_path / "guides"
    guides.mkdir()
    (guides / "installation.md").write_text(
        '---\ntitle: "Installation"\npublished: true\n---\n\n# Installation\n'
    )
    (guides / "draft-page.md").write_text("# Draft\n\nNo frontmatter.\n")

    return tmp_path


@pytest.fixture
def client(docs_dir: Path) -> TestClient:
    """Create a test client with mocked GitHub service."""
    app = create_app(
        docs_dir=docs_dir,
        github_token="test-token",
        github_repo="owner/repo",
        base_branch="main",
    )
    return TestClient(app)


class TestIndexPage:
    def test_returns_html(self, client: TestClient):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]

    def test_contains_tree(self, client: TestClient):
        resp = client.get("/")
        assert "getting started" in resp.text
        assert "installation" in resp.text

    def test_shows_draft_badge(self, client: TestClient):
        resp = client.get("/")
        assert "Draft" in resp.text

    def test_contains_editor_structure(self, client: TestClient):
        resp = client.get("/")
        assert "Docs Editor" in resp.text
        assert "edit-form" in resp.text
        assert "create-form" in resp.text


class TestEditApi:
    def test_returns_file_data(self, client: TestClient):
        resp = client.get("/api/edit?path=getting-started.md")
        assert resp.status_code == 200
        data = resp.json()
        assert data["path"] == "getting-started.md"
        assert data["title"] == "Getting Started"
        assert data["published"] is True
        assert "# Getting Started" in data["content"]

    def test_file_without_frontmatter(self, client: TestClient):
        resp = client.get("/api/edit?path=guides/draft-page.md")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == ""
        assert data["published"] is False
        assert "# Draft" in data["content"]

    def test_missing_file_returns_error(self, client: TestClient):
        resp = client.get("/api/edit?path=nonexistent.md")
        assert resp.status_code == 500 or resp.status_code == 404


class TestFoldersApi:
    def test_returns_folders(self, client: TestClient):
        resp = client.get("/api/folders")
        assert resp.status_code == 200
        data = resp.json()
        assert "" in data["folders"]  # root
        assert "guides" in data["folders"]


class TestStoreApi:
    @patch("aidocs_cli.ui.app.GitHubService")
    def test_creates_file_and_redirects(self, mock_gh_cls, docs_dir: Path):
        app = create_app(
            docs_dir=docs_dir,
            github_token="test-token",
            github_repo="owner/repo",
        )

        with patch.object(
            app, "__dict__", app.__dict__
        ):
            client = TestClient(app, follow_redirects=False)

            # Mock the github service that was created inside create_app
            # We need to patch at the module level
            with patch("aidocs_cli.ui.github_service.GitHubService.create_pr_for_new_file", return_value="https://github.com/owner/repo/pull/1"):
                resp = client.post("/api/store", data={
                    "folder": "guides",
                    "filename": "new-page",
                    "content": "# New Page\n",
                    "title": "New Page",
                    "published": "1",
                })
                assert resp.status_code == 303
                assert (docs_dir / "guides" / "new-page.md").exists()
                content = (docs_dir / "guides" / "new-page.md").read_text()
                assert "published: true" in content

    def test_invalid_filename_returns_422(self, client: TestClient):
        resp = client.post("/api/store", data={
            "folder": "",
            "filename": "INVALID NAME",
            "content": "# Test\n",
        }, follow_redirects=False)
        assert resp.status_code == 422


class TestUpdateApi:
    def test_update_creates_pr(self, docs_dir: Path):
        app = create_app(
            docs_dir=docs_dir,
            github_token="test-token",
            github_repo="owner/repo",
        )
        client = TestClient(app, follow_redirects=False)

        with patch("aidocs_cli.ui.github_service.GitHubService.create_pr_for_update", return_value="https://github.com/owner/repo/pull/2"):
            resp = client.post("/api/update", data={
                "path": "getting-started.md",
                "content": "# Updated\n",
                "title": "Updated Title",
                "published": "1",
            })
            assert resp.status_code == 303

    def test_missing_path_returns_422(self, client: TestClient):
        resp = client.post("/api/update", data={
            "path": "",
            "content": "",
        }, follow_redirects=False)
        assert resp.status_code == 422


class TestDeleteApi:
    def test_delete_creates_pr(self, docs_dir: Path):
        app = create_app(
            docs_dir=docs_dir,
            github_token="test-token",
            github_repo="owner/repo",
        )
        client = TestClient(app, follow_redirects=False)

        with patch("aidocs_cli.ui.github_service.GitHubService.create_pr_for_delete", return_value="https://github.com/owner/repo/pull/3"):
            resp = client.post("/api/delete", data={
                "path": "getting-started.md",
            })
            assert resp.status_code == 303

    def test_missing_path_returns_422(self, client: TestClient):
        resp = client.post("/api/delete", data={
            "path": "",
        }, follow_redirects=False)
        assert resp.status_code == 422


class TestUploadImageApi:
    def test_uploads_image(self, client: TestClient):
        resp = client.post("/api/upload-image", data={
            "doc_path": "guides/installation.md",
        }, files={
            "image": ("screenshot.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 100, "image/png"),
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "markdown" in data
        assert "repo_path" in data
        assert "screenshot" in data["markdown"]
