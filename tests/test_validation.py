from __future__ import annotations

import pytest

from brief.ingest import is_safe_story_url
from brief.issues import is_valid_issue_date
from brief.publish import publish_issue


class TestStoryUrlValidation:
    def test_https_and_http_accepted(self):
        assert is_safe_story_url("https://example.com/story")
        assert is_safe_story_url("http://example.com/story")

    def test_dangerous_schemes_rejected(self):
        assert not is_safe_story_url("javascript:alert(1)")
        assert not is_safe_story_url("data:text/html,<script>alert(1)</script>")
        assert not is_safe_story_url("file:///etc/passwd")

    def test_empty_and_relative_rejected(self):
        assert not is_safe_story_url("")
        assert not is_safe_story_url("/relative/path")
        assert not is_safe_story_url("https://")


class TestIssueDateValidation:
    def test_plain_dates_accepted(self):
        assert is_valid_issue_date("2026-07-13")

    def test_path_traversal_rejected(self):
        assert not is_valid_issue_date("../../secret")
        assert not is_valid_issue_date("2026-07-13/../other")
        assert not is_valid_issue_date("2026-07-13x")
        assert not is_valid_issue_date("sample")

    def test_publish_rejects_malformed_date(self, sqlite_repo):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            publish_issue("../evil")
