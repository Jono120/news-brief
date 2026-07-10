from __future__ import annotations

from typing import Protocol

from brief.entities import Story, StoryStatus


class StoryRepository(Protocol):
    def init(self) -> None: ...

    def upsert_story(self, story: Story) -> int: ...

    def list_stories(self, status: StoryStatus | None = None, limit: int = 100) -> list[Story]: ...

    def get_story(self, story_id: int) -> Story | None: ...
