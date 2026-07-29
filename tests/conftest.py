from __future__ import annotations

import pytest

from brief.db.factory import reset_repository
from brief.entities import Story, StoryStatus


@pytest.fixture
def sqlite_repo(tmp_path, monkeypatch):
    """Point the SQLite backend at a throwaway database for the test."""
    import brief.db.sqlite as sqlite_module

    monkeypatch.setenv("BRIEF_DATABASE", "sqlite")
    monkeypatch.setattr(sqlite_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(sqlite_module, "DB_PATH", tmp_path / "test.db")
    reset_repository()

    from brief.models import init_db

    init_db()
    yield
    reset_repository()


def make_story(**overrides) -> Story:
    defaults = {
        "id": None,
        "url": "https://example.com/story",
        "title": "Singapore fintech raises Series B",
        "source_name": "Test Source",
        "published_at": "2026-07-10T00:00:00+00:00",
        "excerpt": "A Singapore-based payments startup raised new funding.",
        "category": "fintech",
        "apac_score": 0.8,
        "status": StoryStatus.CANDIDATE,
    }
    defaults.update(overrides)
    return Story(**defaults)
