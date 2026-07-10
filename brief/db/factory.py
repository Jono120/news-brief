from __future__ import annotations

import os

from brief.db.base import StoryRepository
from brief.db.sqlite import SqliteRepository
from brief.db.supabase_backend import SupabaseRepository

_repo: StoryRepository | None = None


def get_repository() -> StoryRepository:
    global _repo
    if _repo is not None:
        return _repo

    backend = os.environ.get("BRIEF_DATABASE", "sqlite").strip().lower()
    if backend == "supabase":
        _repo = SupabaseRepository()
    else:
        _repo = SqliteRepository()
    return _repo


def reset_repository() -> None:
    global _repo
    _repo = None
