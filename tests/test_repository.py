from __future__ import annotations

from brief.entities import StoryStatus
from brief.models import count_stories, get_story, list_stories, update_story, upsert_story

from tests.conftest import make_story


def test_upsert_and_get_roundtrip(sqlite_repo):
    story_id = upsert_story(make_story())
    loaded = get_story(story_id)
    assert loaded is not None
    assert loaded.title == "Singapore fintech raises Series B"
    assert loaded.status == StoryStatus.CANDIDATE


def test_upsert_same_url_updates_instead_of_duplicating(sqlite_repo):
    first_id = upsert_story(make_story())
    second_id = upsert_story(make_story(title="Updated title"))
    assert first_id == second_id
    assert count_stories() == 1
    assert get_story(first_id).title == "Updated title"


def test_reingest_does_not_downgrade_published_story(sqlite_repo):
    story_id = upsert_story(make_story())
    update_story(story_id, status=StoryStatus.PUBLISHED, issue_date="2026-07-10")

    # A fresh ingest of the same URL arrives as a candidate again.
    upsert_story(make_story(title="Re-ingested"))

    loaded = get_story(story_id)
    assert loaded.status == StoryStatus.PUBLISHED
    assert loaded.title == "Singapore fintech raises Series B"


def test_count_stories_by_status(sqlite_repo):
    upsert_story(make_story(url="https://example.com/a"))
    upsert_story(make_story(url="https://example.com/b"))
    approved_id = upsert_story(make_story(url="https://example.com/c"))
    update_story(approved_id, status=StoryStatus.APPROVED)

    assert count_stories() == 3
    assert count_stories(StoryStatus.CANDIDATE) == 2
    assert count_stories(StoryStatus.APPROVED) == 1


def test_list_stories_filters_by_status(sqlite_repo):
    upsert_story(make_story(url="https://example.com/a"))
    rejected_id = upsert_story(make_story(url="https://example.com/b"))
    update_story(rejected_id, status=StoryStatus.REJECTED)

    candidates = list_stories(StoryStatus.CANDIDATE)
    assert [s.url for s in candidates] == ["https://example.com/a"]
