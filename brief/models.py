from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from brief.db import get_repository
from brief.entities import Issue, Story, StoryStatus, utc_now
from brief.paths import CONFIG_DIR, DATA_DIR, DB_PATH, OUTPUT_DIR, ROOT

__all__ = [
    "CONFIG_DIR",
    "DATA_DIR",
    "DB_PATH",
    "Issue",
    "OUTPUT_DIR",
    "ROOT",
    "Story",
    "StoryStatus",
    "count_stories",
    "dump_json",
    "get_story",
    "init_db",
    "list_stories",
    "load_edition_config",
    "load_sources_config",
    "load_yaml",
    "update_story",
    "upsert_story",
    "utc_now",
]


def init_db() -> None:
    """Create the schema (SQLite) or verify connectivity (Supabase).

    Call once at process startup — repository operations assume it has run.
    """
    get_repository().init()


def upsert_story(story: Story) -> int:
    return get_repository().upsert_story(story)


def list_stories(status: StoryStatus | None = None, limit: int = 100) -> list[Story]:
    return get_repository().list_stories(status=status, limit=limit)


def count_stories(status: StoryStatus | None = None) -> int:
    return get_repository().count_stories(status=status)


def get_story(story_id: int) -> Story | None:
    return get_repository().get_story(story_id)


def update_story(story_id: int, **fields: Any) -> Story | None:
    story = get_story(story_id)
    if not story:
        return None
    for key, value in fields.items():
        if key == "status" and isinstance(value, str):
            value = StoryStatus(value)
        if hasattr(story, key):
            setattr(story, key, value)
    story.updated_at = utc_now()
    upsert_story(story)
    return get_story(story_id)


def load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_edition_config() -> dict[str, Any]:
    return load_yaml(CONFIG_DIR / "edition.yaml")


def load_sources_config() -> list[dict[str, Any]]:
    return load_yaml(CONFIG_DIR / "sources.yaml").get("sources", [])


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
