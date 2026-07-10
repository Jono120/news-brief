from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class StoryStatus(str, Enum):
    CANDIDATE = "candidate"
    DRAFTED = "drafted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


@dataclass
class Story:
    id: int | None
    url: str
    title: str
    source_name: str
    published_at: str
    excerpt: str
    category: str
    apac_score: float
    summary: str = ""
    why_it_matters: str = ""
    read_time_minutes: int = 3
    status: StoryStatus = StoryStatus.CANDIDATE
    issue_date: str | None = None
    created_at: str = field(default_factory=lambda: utc_now())
    updated_at: str = field(default_factory=lambda: utc_now())

    def to_row(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    def to_dict(self) -> dict[str, Any]:
        data = self.to_row()
        if self.id is not None:
            data["id"] = self.id
        return data


@dataclass
class Issue:
    date: str
    edition_slug: str
    title: str
    intro: str
    stories: list[Story]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def story_from_row(row: sqlite3.Row) -> Story:
    return Story(
        id=row["id"],
        url=row["url"],
        title=row["title"],
        source_name=row["source_name"],
        published_at=row["published_at"],
        excerpt=row["excerpt"],
        category=row["category"],
        apac_score=row["apac_score"],
        summary=row["summary"],
        why_it_matters=row["why_it_matters"],
        read_time_minutes=row["read_time_minutes"],
        status=StoryStatus(row["status"]),
        issue_date=row["issue_date"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
