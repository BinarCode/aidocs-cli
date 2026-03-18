"""GitHub API service for creating branches, commits, and pull requests."""

from __future__ import annotations

import base64
import re
from datetime import datetime, timezone
from pathlib import Path

import httpx


class GitHubService:
    def __init__(self, token: str, owner: str, repo: str, base_branch: str = "main"):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_branch = base_branch
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url="https://api.github.com",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                timeout=30.0,
            )
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def _slugify(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9]+", "-", text)
        return text.strip("-")

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    def _get_base_sha(self) -> str:
        resp = self.client.get(
            f"/repos/{self.owner}/{self.repo}/git/ref/heads/{self.base_branch}"
        )
        resp.raise_for_status()
        return resp.json()["object"]["sha"]

    def _create_branch(self, branch_name: str) -> None:
        base_sha = self._get_base_sha()
        resp = self.client.post(
            f"/repos/{self.owner}/{self.repo}/git/refs",
            json={"ref": f"refs/heads/{branch_name}", "sha": base_sha},
        )
        resp.raise_for_status()

    def _get_file_sha(self, path: str) -> str:
        resp = self.client.get(
            f"/repos/{self.owner}/{self.repo}/contents/{path}",
            params={"ref": self.base_branch},
        )
        resp.raise_for_status()
        return resp.json()["sha"]

    def _commit_file(
        self,
        branch: str,
        path: str,
        content: str,
        message: str,
        sha: str | None = None,
    ) -> None:
        payload: dict = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha
        resp = self.client.put(
            f"/repos/{self.owner}/{self.repo}/contents/{path}",
            json=payload,
        )
        resp.raise_for_status()

    def _commit_images(self, branch: str, image_paths: list[str], docs_dir: Path) -> None:
        for repo_path in image_paths:
            full_path = docs_dir / repo_path
            if not full_path.exists():
                continue
            image_content = full_path.read_bytes()
            resp = self.client.put(
                f"/repos/{self.owner}/{self.repo}/contents/{repo_path}",
                json={
                    "message": f"docs: add image {Path(repo_path).name}",
                    "content": base64.b64encode(image_content).decode(),
                    "branch": branch,
                },
            )
            resp.raise_for_status()

    def _open_pull_request(self, branch: str, title: str) -> str:
        resp = self.client.post(
            f"/repos/{self.owner}/{self.repo}/pulls",
            json={
                "title": title,
                "head": branch,
                "base": self.base_branch,
                "body": "Docs update via aidocs editor.",
            },
        )
        resp.raise_for_status()
        return resp.json()["html_url"]

    def create_pr_for_update(
        self,
        path: str,
        content: str,
        commit_message: str,
        image_paths: list[str] | None = None,
        docs_dir: Path | None = None,
    ) -> str:
        slug = self._slugify(Path(path).stem)
        branch = f"docs/{slug}-{self._timestamp()}"
        sha = self._get_file_sha(path)

        self._create_branch(branch)
        if image_paths and docs_dir:
            self._commit_images(branch, image_paths, docs_dir)
        self._commit_file(branch, path, content, commit_message, sha=sha)
        return self._open_pull_request(branch, commit_message)

    def create_pr_for_new_file(
        self,
        path: str,
        content: str,
        commit_message: str,
        image_paths: list[str] | None = None,
        docs_dir: Path | None = None,
    ) -> str:
        slug = self._slugify(Path(path).stem)
        branch = f"docs/{slug}-{self._timestamp()}"

        self._create_branch(branch)
        if image_paths and docs_dir:
            self._commit_images(branch, image_paths, docs_dir)
        self._commit_file(branch, path, content, commit_message)
        return self._open_pull_request(branch, commit_message)

    def create_pr_for_delete(self, path: str, commit_message: str) -> str:
        slug = self._slugify(Path(path).stem)
        branch = f"docs/delete-{slug}-{self._timestamp()}"
        sha = self._get_file_sha(path)

        self._create_branch(branch)
        resp = self.client.delete(
            f"/repos/{self.owner}/{self.repo}/contents/{path}",
            json={
                "message": commit_message,
                "sha": sha,
                "branch": branch,
            },
        )
        resp.raise_for_status()
        return self._open_pull_request(branch, commit_message)
