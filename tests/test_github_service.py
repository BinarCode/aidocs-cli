"""Tests for github_service module."""

from unittest.mock import MagicMock, patch
from pathlib import Path

import pytest

from aidocs_cli.ui.github_service import GitHubService


@pytest.fixture
def github() -> GitHubService:
    return GitHubService(
        token="test-token",
        owner="testowner",
        repo="testrepo",
        base_branch="main",
    )


class TestSlugify:
    def test_basic(self, github: GitHubService):
        assert github._slugify("Hello World") == "hello-world"

    def test_special_chars(self, github: GitHubService):
        assert github._slugify("my-page_v2!") == "my-page-v2"

    def test_leading_trailing(self, github: GitHubService):
        assert github._slugify("  --hello--  ") == "hello"


class TestCreatePrForUpdate:
    def test_calls_github_api_in_correct_order(self, github: GitHubService):
        mock_client = MagicMock()
        github._client = mock_client

        # Mock responses
        get_ref_resp = MagicMock()
        get_ref_resp.json.return_value = {"object": {"sha": "base-sha-123"}}
        get_ref_resp.raise_for_status = MagicMock()

        get_file_resp = MagicMock()
        get_file_resp.json.return_value = {"sha": "file-sha-456"}
        get_file_resp.raise_for_status = MagicMock()

        create_branch_resp = MagicMock()
        create_branch_resp.raise_for_status = MagicMock()

        commit_resp = MagicMock()
        commit_resp.raise_for_status = MagicMock()

        pr_resp = MagicMock()
        pr_resp.json.return_value = {"html_url": "https://github.com/testowner/testrepo/pull/42"}
        pr_resp.raise_for_status = MagicMock()

        mock_client.get.side_effect = [get_file_resp, get_ref_resp]
        mock_client.post.side_effect = [create_branch_resp, pr_resp]
        mock_client.put.return_value = commit_resp

        url = github.create_pr_for_update(
            path="docs/page.md",
            content="# Updated\n",
            commit_message="docs: update page",
        )

        assert url == "https://github.com/testowner/testrepo/pull/42"
        assert mock_client.get.call_count == 2
        assert mock_client.post.call_count == 2
        assert mock_client.put.call_count == 1


class TestCreatePrForNewFile:
    def test_creates_branch_and_commits(self, github: GitHubService):
        mock_client = MagicMock()
        github._client = mock_client

        get_ref_resp = MagicMock()
        get_ref_resp.json.return_value = {"object": {"sha": "base-sha-123"}}
        get_ref_resp.raise_for_status = MagicMock()

        create_branch_resp = MagicMock()
        create_branch_resp.raise_for_status = MagicMock()

        commit_resp = MagicMock()
        commit_resp.raise_for_status = MagicMock()

        pr_resp = MagicMock()
        pr_resp.json.return_value = {"html_url": "https://github.com/testowner/testrepo/pull/99"}
        pr_resp.raise_for_status = MagicMock()

        mock_client.get.return_value = get_ref_resp
        mock_client.post.side_effect = [create_branch_resp, pr_resp]
        mock_client.put.return_value = commit_resp

        url = github.create_pr_for_new_file(
            path="docs/new.md",
            content="# New\n",
            commit_message="docs: add new",
        )

        assert url == "https://github.com/testowner/testrepo/pull/99"


class TestCreatePrForDelete:
    def test_deletes_file_and_creates_pr(self, github: GitHubService):
        mock_client = MagicMock()
        github._client = mock_client

        get_file_resp = MagicMock()
        get_file_resp.json.return_value = {"sha": "file-sha-789"}
        get_file_resp.raise_for_status = MagicMock()

        get_ref_resp = MagicMock()
        get_ref_resp.json.return_value = {"object": {"sha": "base-sha-123"}}
        get_ref_resp.raise_for_status = MagicMock()

        create_branch_resp = MagicMock()
        create_branch_resp.raise_for_status = MagicMock()

        delete_resp = MagicMock()
        delete_resp.raise_for_status = MagicMock()

        pr_resp = MagicMock()
        pr_resp.json.return_value = {"html_url": "https://github.com/testowner/testrepo/pull/55"}
        pr_resp.raise_for_status = MagicMock()

        mock_client.get.side_effect = [get_file_resp, get_ref_resp]
        mock_client.post.side_effect = [create_branch_resp, pr_resp]
        mock_client.delete.return_value = delete_resp

        url = github.create_pr_for_delete(
            path="docs/old.md",
            commit_message="docs: delete old",
        )

        assert url == "https://github.com/testowner/testrepo/pull/55"
        assert mock_client.delete.call_count == 1
