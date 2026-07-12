from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from brief.entities import Issue
from brief.models import load_edition_config
from brief.paths import OUTPUT_DIR, ROOT

logger = logging.getLogger(__name__)

PLACEHOLDER_PATH = ROOT / "content" / "placeholder" / "issue.json"

ISSUE_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_valid_issue_date(value: str) -> bool:
    """Issue dates are path components — reject anything that is not
    a plain YYYY-MM-DD string before it reaches the filesystem."""
    return bool(ISSUE_DATE_RE.fullmatch(value))


@dataclass
class PublicStory:
    title: str
    url: str
    source_name: str
    category: str
    summary: str
    why_it_matters: str
    read_time_minutes: int
    apac_score: float


@dataclass
class PublicIssue:
    date: str
    edition_slug: str
    intro: str
    apac_ratio: float
    is_sample: bool
    stories: list[PublicStory]

    @property
    def story_count(self) -> int:
        return len(self.stories)

    @property
    def label(self) -> str:
        if self.is_sample:
            return "Sample issue"
        return self.date


@dataclass
class IssueSummary:
    date: str
    story_count: int
    is_sample: bool
    apac_ratio: float


def category_labels() -> dict[str, str]:
    edition = load_edition_config()
    return {item["slug"]: item["label"] for item in edition.get("categories", [])}


def edition_info() -> dict[str, Any]:
    return load_edition_config()["edition"]


def _story_from_dict(data: dict[str, Any]) -> PublicStory:
    return PublicStory(
        title=data["title"],
        url=data["url"],
        source_name=data["source_name"],
        category=data.get("category", "misc"),
        summary=data.get("summary", ""),
        why_it_matters=data.get("why_it_matters", ""),
        read_time_minutes=int(data.get("read_time_minutes", 3)),
        apac_score=float(data.get("apac_score", 0.0)),
    )


def issue_from_dict(data: dict[str, Any]) -> PublicIssue:
    return PublicIssue(
        date=data["date"],
        edition_slug=data.get("edition_slug", edition_info()["slug"]),
        intro=data.get("intro", ""),
        apac_ratio=float(data.get("apac_ratio", 0.0)),
        is_sample=bool(data.get("is_sample", False)),
        stories=[_story_from_dict(item) for item in data.get("stories", [])],
    )


def issue_to_dict(issue: Issue, apac_ratio: float, is_sample: bool = False) -> dict[str, Any]:
    return {
        "date": issue.date,
        "edition_slug": issue.edition_slug,
        "title": issue.title,
        "intro": issue.intro,
        "apac_ratio": apac_ratio,
        "is_sample": is_sample,
        "stories": [
            {
                "title": story.title,
                "url": story.url,
                "source_name": story.source_name,
                "category": story.category,
                "summary": story.summary,
                "why_it_matters": story.why_it_matters,
                "read_time_minutes": story.read_time_minutes,
                "apac_score": story.apac_score,
            }
            for story in issue.stories
        ],
    }


def load_json_issue(path: Path) -> PublicIssue | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return issue_from_dict(data)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        logger.warning("Skipping malformed issue file %s: %s", path, exc)
        return None


def published_issue_dir(edition_slug: str, issue_date: str) -> Path:
    return OUTPUT_DIR / edition_slug / issue_date


def list_published_dates(edition_slug: str | None = None) -> list[str]:
    slug = edition_slug or edition_info()["slug"]
    edition_dir = OUTPUT_DIR / slug
    if not edition_dir.exists():
        return []
    dates = []
    for child in edition_dir.iterdir():
        if child.is_dir() and is_valid_issue_date(child.name) and (child / "issue.json").exists():
            dates.append(child.name)
    return sorted(dates, reverse=True)


def load_published_issue(issue_date: str, edition_slug: str | None = None) -> PublicIssue | None:
    if not is_valid_issue_date(issue_date):
        return None
    slug = edition_slug or edition_info()["slug"]
    return load_json_issue(published_issue_dir(slug, issue_date) / "issue.json")


def load_placeholder_issue() -> PublicIssue:
    issue = load_json_issue(PLACEHOLDER_PATH)
    if issue is None:
        raise FileNotFoundError(f"Placeholder issue missing at {PLACEHOLDER_PATH}")
    return issue


def list_public_issues(include_sample: bool = True) -> list[IssueSummary]:
    slug = edition_info()["slug"]
    summaries: list[IssueSummary] = []
    for issue_date in list_published_dates(slug):
        issue = load_published_issue(issue_date, slug)
        if issue:
            summaries.append(
                IssueSummary(
                    date=issue.date,
                    story_count=issue.story_count,
                    is_sample=False,
                    apac_ratio=issue.apac_ratio,
                )
            )
    if include_sample:
        sample = load_placeholder_issue()
        summaries.append(
            IssueSummary(
                date=sample.date,
                story_count=sample.story_count,
                is_sample=True,
                apac_ratio=sample.apac_ratio,
            )
        )
    return summaries


def get_public_issue(issue_date: str) -> PublicIssue | None:
    if issue_date == "sample":
        return load_placeholder_issue()
    published = load_published_issue(issue_date)
    if published:
        return published
    if issue_date == load_placeholder_issue().date:
        return load_placeholder_issue()
    return None


def get_featured_issue() -> PublicIssue:
    dates = list_published_dates()
    if dates:
        issue = load_published_issue(dates[0])
        if issue:
            return issue
    return load_placeholder_issue()
