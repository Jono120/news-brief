from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from brief.issues import (
    category_labels,
    edition_info,
    get_featured_issue,
    get_public_issue,
    list_public_issues,
)
from brief.models import (
    StoryStatus,
    count_stories,
    get_story,
    list_stories,
    load_edition_config,
    update_story,
)

router = APIRouter(prefix="/api")


class StoryUpdate(BaseModel):
    summary: str | None = Field(None, max_length=2000)
    why_it_matters: str | None = Field(None, max_length=1000)
    category: str | None = None
    read_time_minutes: int | None = Field(None, ge=1, le=60)


def _story_dict(story) -> dict[str, Any]:
    return story.to_dict()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/edition")
def edition() -> dict[str, Any]:
    config = load_edition_config()
    return {
        "edition": edition_info(),
        "categories": category_labels(),
        "scoring": config.get("scoring", {}),
    }


@router.get("/queue/stats")
def queue_stats() -> dict[str, Any]:
    edition = edition_info()
    return {
        "candidates": count_stories(StoryStatus.CANDIDATE),
        "drafted": count_stories(StoryStatus.DRAFTED),
        "approved": count_stories(StoryStatus.APPROVED),
        "stories_per_issue": edition["stories_per_issue"],
        "tagline": edition["tagline"],
    }


@router.get("/stories")
def stories_index(status: StoryStatus | None = None, limit: int = 100) -> list[dict[str, Any]]:
    return [_story_dict(s) for s in list_stories(status=status, limit=limit)]


@router.get("/stories/{story_id}")
def story_detail(story_id: int) -> dict[str, Any]:
    story = get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return _story_dict(story)


@router.patch("/stories/{story_id}")
def story_patch(story_id: int, body: StoryUpdate) -> dict[str, Any]:
    story = get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    fields: dict[str, Any] = {}
    if body.summary is not None:
        fields["summary"] = body.summary.strip()
    if body.why_it_matters is not None:
        fields["why_it_matters"] = body.why_it_matters.strip()
    if body.category is not None:
        category = body.category.strip()
        if category not in category_labels():
            raise HTTPException(status_code=422, detail=f"Unknown category: {category}")
        fields["category"] = category
    if body.read_time_minutes is not None:
        fields["read_time_minutes"] = body.read_time_minutes
    # Editing a fresh candidate moves it into the drafted queue; edits to
    # approved/published stories must not knock them out of the issue.
    if story.status == StoryStatus.CANDIDATE:
        fields["status"] = StoryStatus.DRAFTED

    updated = update_story(story_id, **fields)
    if not updated:
        raise HTTPException(status_code=404, detail="Story not found")
    return _story_dict(updated)


@router.post("/stories/{story_id}/approve")
def story_approve(story_id: int) -> dict[str, Any]:
    updated = update_story(story_id, status=StoryStatus.APPROVED)
    if not updated:
        raise HTTPException(status_code=404, detail="Story not found")
    return _story_dict(updated)


@router.post("/stories/{story_id}/reject")
def story_reject(story_id: int) -> dict[str, Any]:
    updated = update_story(story_id, status=StoryStatus.REJECTED)
    if not updated:
        raise HTTPException(status_code=404, detail="Story not found")
    return _story_dict(updated)


@router.get("/public/issues")
def public_issues(include_sample: bool = True) -> list[dict[str, Any]]:
    return [
        {
            "date": item.date,
            "story_count": item.story_count,
            "is_sample": item.is_sample,
            "apac_ratio": item.apac_ratio,
        }
        for item in list_public_issues(include_sample=include_sample)
    ]


@router.get("/public/issues/{issue_date}")
def public_issue_detail(issue_date: str) -> dict[str, Any]:
    issue = get_public_issue(issue_date)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return {
        "date": issue.date,
        "edition_slug": issue.edition_slug,
        "intro": issue.intro,
        "apac_ratio": issue.apac_ratio,
        "is_sample": issue.is_sample,
        "story_count": issue.story_count,
        "stories": [
            {
                "title": s.title,
                "url": s.url,
                "source_name": s.source_name,
                "category": s.category,
                "summary": s.summary,
                "why_it_matters": s.why_it_matters,
                "read_time_minutes": s.read_time_minutes,
                "apac_score": s.apac_score,
            }
            for s in issue.stories
        ],
    }


@router.get("/public/featured")
def public_featured() -> dict[str, Any]:
    issue = get_featured_issue()
    return {
        "date": issue.date,
        "edition_slug": issue.edition_slug,
        "intro": issue.intro,
        "apac_ratio": issue.apac_ratio,
        "is_sample": issue.is_sample,
        "story_count": issue.story_count,
        "stories": [
            {
                "title": s.title,
                "url": s.url,
                "source_name": s.source_name,
                "category": s.category,
                "summary": s.summary,
                "why_it_matters": s.why_it_matters,
                "read_time_minutes": s.read_time_minutes,
                "apac_score": s.apac_score,
            }
            for s in issue.stories
        ],
    }
