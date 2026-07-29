from __future__ import annotations

import base64
import json
import os
from typing import Any

from brief.entities import Story, StoryStatus, utc_now


def _decode_supabase_key_role(key: str) -> str | None:
    """Return the JWT role claim from a Supabase API key, if present."""
    parts = key.split(".")
    if len(parts) < 2:
        return None
    payload = parts[1]
    padding = "=" * (-len(payload) % 4)
    try:
        decoded = base64.urlsafe_b64decode(payload + padding)
        data = json.loads(decoded)
        role = data.get("role")
        return str(role) if role is not None else None
    except (ValueError, json.JSONDecodeError, TypeError):
        return None


def _validate_supabase_key(key: str) -> None:
    role = _decode_supabase_key_role(key)
    if role == "anon":
        raise RuntimeError(
            "SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_KEY) must be the service_role key, "
            "not the public anon key. Anon keys cannot write to the editorial pipeline."
        )


def _row_to_story(row: dict[str, Any]) -> Story:
    return Story(
        id=int(row["id"]),
        url=row["url"],
        title=row["title"],
        source_name=row["source_name"],
        published_at=row["published_at"],
        excerpt=row.get("excerpt") or "",
        category=row.get("category") or "misc",
        apac_score=float(row.get("apac_score") or 0),
        summary=row.get("summary") or "",
        why_it_matters=row.get("why_it_matters") or "",
        read_time_minutes=int(row.get("read_time_minutes") or 3),
        status=StoryStatus(row["status"]),
        issue_date=row.get("issue_date"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _story_payload(story: Story) -> dict[str, Any]:
    return {
        "url": story.url,
        "title": story.title,
        "source_name": story.source_name,
        "published_at": story.published_at,
        "excerpt": story.excerpt,
        "category": story.category,
        "apac_score": story.apac_score,
        "summary": story.summary,
        "why_it_matters": story.why_it_matters,
        "read_time_minutes": story.read_time_minutes,
        "status": story.status.value,
        "issue_date": story.issue_date,
        "created_at": story.created_at,
        "updated_at": story.updated_at,
    }


class SupabaseRepository:
    def __init__(self) -> None:
        url = os.environ.get("SUPABASE_URL", "").strip()
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.environ.get(
            "SUPABASE_KEY", ""
        ).strip()
        if not url or not key:
            raise RuntimeError(
                "Supabase requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY "
                "(or SUPABASE_KEY) when BRIEF_DATABASE=supabase"
            )
        # SUPABASE_KEY is a legacy alias — must be service_role, never the anon JWT.
        _validate_supabase_key(key)
        from supabase import create_client

        self._client = create_client(url, key)
        self._table = "stories"

    def init(self) -> None:
        # Schema is applied via supabase/migrations/ — verify connectivity.
        self._client.table(self._table).select("id").limit(1).execute()

    def upsert_story(self, story: Story) -> int:
        story.updated_at = utc_now()
        existing = (
            self._client.table(self._table)
            .select("id, status")
            .eq("url", story.url)
            .limit(1)
            .execute()
        )
        rows = existing.data or []
        if rows:
            row = rows[0]
            if (
                row["status"] == StoryStatus.PUBLISHED.value
                and story.status in {StoryStatus.CANDIDATE, StoryStatus.DRAFTED}
            ):
                return int(row["id"])
            payload = _story_payload(story)
            self._client.table(self._table).update(payload).eq("id", row["id"]).execute()
            return int(row["id"])

        payload = _story_payload(story)
        inserted = self._client.table(self._table).insert(payload).execute()
        return int(inserted.data[0]["id"])

    def list_stories(self, status: StoryStatus | None = None, limit: int = 100) -> list[Story]:
        query = (
            self._client.table(self._table)
            .select("*")
            .order("apac_score", desc=True)
            .order("published_at", desc=True)
            .limit(limit)
        )
        if status:
            query = query.eq("status", status.value)
        result = query.execute()
        return [_row_to_story(row) for row in (result.data or [])]

    def count_stories(self, status: StoryStatus | None = None) -> int:
        query = self._client.table(self._table).select("id", count="exact", head=True)
        if status:
            query = query.eq("status", status.value)
        result = query.execute()
        return int(result.count or 0)

    def get_story(self, story_id: int) -> Story | None:
        result = (
            self._client.table(self._table).select("*").eq("id", story_id).limit(1).execute()
        )
        rows = result.data or []
        return _row_to_story(rows[0]) if rows else None
