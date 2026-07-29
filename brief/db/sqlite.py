from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from typing import Any

from brief.entities import Story, StoryStatus, story_from_row, utc_now
from brief.paths import DATA_DIR, DB_PATH


class SqliteRepository:
    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Yield a connection that commits on success and always closes."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        # WAL lets the review API read while the CLI writes; busy_timeout
        # retries instead of raising "database is locked" immediately.
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 5000")
        with closing(conn), conn:
            yield conn

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    published_at TEXT NOT NULL,
                    excerpt TEXT NOT NULL DEFAULT '',
                    category TEXT NOT NULL DEFAULT 'misc',
                    apac_score REAL NOT NULL DEFAULT 0
                        CHECK (apac_score >= 0 AND apac_score <= 1),
                    summary TEXT NOT NULL DEFAULT '',
                    why_it_matters TEXT NOT NULL DEFAULT '',
                    read_time_minutes INTEGER NOT NULL DEFAULT 3
                        CHECK (read_time_minutes >= 1),
                    status TEXT NOT NULL DEFAULT 'candidate'
                        CHECK (status IN ('candidate', 'drafted', 'approved', 'rejected', 'published')),
                    issue_date TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_stories_status ON stories(status);
                CREATE INDEX IF NOT EXISTS idx_stories_apac_score ON stories(apac_score);
                CREATE INDEX IF NOT EXISTS idx_stories_issue_date ON stories(issue_date);
                """
            )

    def upsert_story(self, story: Story) -> int:
        story.updated_at = utc_now()
        with self.connect() as conn:
            existing = conn.execute(
                "SELECT id, status FROM stories WHERE url = ?", (story.url,)
            ).fetchone()
            if existing:
                if (
                    existing["status"] == StoryStatus.PUBLISHED.value
                    and story.status in {StoryStatus.CANDIDATE, StoryStatus.DRAFTED}
                ):
                    return existing["id"]
                conn.execute(
                    """
                    UPDATE stories SET
                        title = ?, source_name = ?, published_at = ?, excerpt = ?,
                        category = ?, apac_score = ?, summary = ?, why_it_matters = ?,
                        read_time_minutes = ?, status = ?, issue_date = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        story.title,
                        story.source_name,
                        story.published_at,
                        story.excerpt,
                        story.category,
                        story.apac_score,
                        story.summary,
                        story.why_it_matters,
                        story.read_time_minutes,
                        story.status.value,
                        story.issue_date,
                        story.updated_at,
                        existing["id"],
                    ),
                )
                return existing["id"]

            cursor = conn.execute(
                """
                INSERT INTO stories (
                    url, title, source_name, published_at, excerpt, category,
                    apac_score, summary, why_it_matters, read_time_minutes,
                    status, issue_date, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    story.url,
                    story.title,
                    story.source_name,
                    story.published_at,
                    story.excerpt,
                    story.category,
                    story.apac_score,
                    story.summary,
                    story.why_it_matters,
                    story.read_time_minutes,
                    story.status.value,
                    story.issue_date,
                    story.created_at,
                    story.updated_at,
                ),
            )
            return cursor.lastrowid

    def list_stories(self, status: StoryStatus | None = None, limit: int = 100) -> list[Story]:
        query = "SELECT * FROM stories"
        params: list[Any] = []
        if status:
            query += " WHERE status = ?"
            params.append(status.value)
        query += " ORDER BY apac_score DESC, published_at DESC LIMIT ?"
        params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [story_from_row(row) for row in rows]

    def count_stories(self, status: StoryStatus | None = None) -> int:
        query = "SELECT COUNT(*) FROM stories"
        params: list[Any] = []
        if status:
            query += " WHERE status = ?"
            params.append(status.value)
        with self.connect() as conn:
            return int(conn.execute(query, params).fetchone()[0])

    def get_story(self, story_id: int) -> Story | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM stories WHERE id = ?", (story_id,)).fetchone()
        return story_from_row(row) if row else None
