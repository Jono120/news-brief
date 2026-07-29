from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader, select_autoescape

from brief.issues import is_valid_issue_date, issue_to_dict, published_issue_dir
from brief.models import (
    OUTPUT_DIR,
    Issue,
    Story,
    StoryStatus,
    dump_json,
    get_story,
    list_stories,
    load_edition_config,
    update_story,
)

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def default_issue_date() -> str:
    edition = load_edition_config()["edition"]
    tz = ZoneInfo(edition.get("timezone", "Pacific/Auckland"))
    return datetime.now(tz).date().isoformat()


def jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def issue_intro(issue_date: str, story_count: int) -> str:
    return (
        f"Your APAC tech briefing for {issue_date}. "
        f"{story_count} stories curated for builders, operators, and founders across the region."
    )


def apac_ratio(stories: list[Story]) -> float:
    if not stories:
        return 0.0
    return round(sum(1 for story in stories if story.apac_score >= 0.35) / len(stories), 2)


def build_issue(issue_date: str, story_ids: list[int]) -> Issue:
    edition = load_edition_config()["edition"]
    stories: list[Story] = []
    for story_id in story_ids:
        story = get_story(story_id)
        if story:
            stories.append(story)
    return Issue(
        date=issue_date,
        edition_slug=edition["slug"],
        title=issue_date,
        intro=issue_intro(issue_date, len(stories)),
        stories=stories,
    )


def render_issue(issue: Issue) -> dict[str, str]:
    env = jinja_env()
    edition = load_edition_config()
    categories = {item["slug"]: item["label"] for item in edition.get("categories", [])}
    context = {
        "issue": issue,
        "categories": categories,
        "apac_ratio": apac_ratio(issue.stories),
        "edition": edition["edition"],
    }
    return {
        "markdown": env.get_template("issue.md.j2").render(**context),
        "html": env.get_template("issue.html.j2").render(**context),
        "email": env.get_template("email.html.j2").render(**context),
        "rss": env.get_template("rss.xml.j2").render(**context),
    }


def publish_issue(issue_date: str | None = None) -> Path:
    edition = load_edition_config()["edition"]
    target_date = issue_date or default_issue_date()
    if not is_valid_issue_date(target_date):
        raise ValueError(f"Issue date must be YYYY-MM-DD, got {target_date!r}")
    approved = [story for story in list_stories(StoryStatus.APPROVED, limit=50) if not story.issue_date]
    approved = approved[: edition["stories_per_issue"]]
    if not approved:
        raise ValueError("No approved stories ready to publish. Approve stories in the review UI first.")

    issue = build_issue(target_date, [story.id for story in approved if story.id is not None])
    rendered = render_issue(issue)

    issue_dir = OUTPUT_DIR / edition["slug"] / target_date
    issue_dir.mkdir(parents=True, exist_ok=True)
    (issue_dir / "issue.md").write_text(rendered["markdown"], encoding="utf-8")
    (issue_dir / "issue.html").write_text(rendered["html"], encoding="utf-8")
    (issue_dir / "email.html").write_text(rendered["email"], encoding="utf-8")
    (issue_dir / "feed.xml").write_text(rendered["rss"], encoding="utf-8")
    dump_json(issue_dir / "issue.json", issue_to_dict(issue, apac_ratio(issue.stories)))

    for story in issue.stories:
        if story.id is not None:
            update_story(story.id, status=StoryStatus.PUBLISHED, issue_date=target_date)

    return issue_dir


def rebuild_issue_json(issue_date: str) -> Path | None:
    """Write issue.json for a previously published issue from the database."""
    edition = load_edition_config()["edition"]
    published = [
        story
        for story in list_stories(StoryStatus.PUBLISHED, limit=200)
        if story.issue_date == issue_date
    ]
    if not published:
        return None

    issue = build_issue(issue_date, [story.id for story in published if story.id is not None])
    issue_dir = published_issue_dir(edition["slug"], issue_date)
    issue_dir.mkdir(parents=True, exist_ok=True)
    dump_json(issue_dir / "issue.json", issue_to_dict(issue, apac_ratio(issue.stories)))
    return issue_dir / "issue.json"
