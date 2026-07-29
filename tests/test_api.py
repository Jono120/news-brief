from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from brief.api_server import create_api_app
from brief.entities import StoryStatus
from brief.models import get_story, upsert_story
from tests.conftest import make_story


@pytest.fixture
def client(sqlite_repo):
    return TestClient(create_api_app())


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_patch_candidate_moves_to_drafted(client):
    story_id = upsert_story(make_story())
    response = client.patch(f"/api/stories/{story_id}", json={"summary": "Edited."})
    assert response.status_code == 200
    assert response.json()["status"] == "drafted"


def test_patch_does_not_unapprove_story(client):
    story_id = upsert_story(make_story(status=StoryStatus.APPROVED))
    response = client.patch(f"/api/stories/{story_id}", json={"summary": "Tightened wording."})
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert get_story(story_id).status == StoryStatus.APPROVED


def test_approve_and_reject_endpoints(client):
    story_id = upsert_story(make_story())
    assert client.post(f"/api/stories/{story_id}/approve").json()["status"] == "approved"
    assert client.post(f"/api/stories/{story_id}/reject").json()["status"] == "rejected"


def test_queue_stats_counts(client):
    upsert_story(make_story(url="https://example.com/a"))
    upsert_story(make_story(url="https://example.com/b", status=StoryStatus.DRAFTED))
    stats = client.get("/api/queue/stats").json()
    assert stats["candidates"] == 1
    assert stats["drafted"] == 1
    assert stats["approved"] == 0


def test_missing_story_returns_404(client):
    assert client.get("/api/stories/9999").status_code == 404
    assert client.patch("/api/stories/9999", json={"summary": "x"}).status_code == 404


def test_patch_rejects_out_of_bounds_read_time(client):
    story_id = upsert_story(make_story())
    assert (
        client.patch(f"/api/stories/{story_id}", json={"read_time_minutes": 0}).status_code == 422
    )
    assert (
        client.patch(f"/api/stories/{story_id}", json={"read_time_minutes": 999}).status_code
        == 422
    )


def test_patch_rejects_unknown_category(client):
    story_id = upsert_story(make_story())
    response = client.patch(f"/api/stories/{story_id}", json={"category": "not-a-category"})
    assert response.status_code == 422
    assert client.patch(f"/api/stories/{story_id}", json={"category": "ai"}).status_code == 200


def test_public_issue_rejects_malformed_date(client):
    assert client.get("/api/public/issues/..%2F..%2Fetc").status_code == 404


def test_bearer_token_required_when_configured(sqlite_repo, monkeypatch):
    monkeypatch.setenv("BRIEF_API_TOKEN", "secret-token")
    secured = TestClient(create_api_app())

    assert secured.get("/api/stories").status_code == 401
    assert secured.get("/api/health").status_code == 200  # health stays open

    ok = secured.get("/api/stories", headers={"Authorization": "Bearer secret-token"})
    assert ok.status_code == 200
    bad = secured.get("/api/stories", headers={"Authorization": "Bearer wrong"})
    assert bad.status_code == 401
