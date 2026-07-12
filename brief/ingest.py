from __future__ import annotations

import html
import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urlparse

import feedparser
import httpx

from brief.models import Story, StoryStatus, load_edition_config, load_sources_config, upsert_story, utc_now
from brief.server import HTTPS_CLIENT_DEFAULTS, require_https_url

logger = logging.getLogger(__name__)

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def clean_text(value: str) -> str:
    text = html.unescape(TAG_RE.sub(" ", value or ""))
    return WS_RE.sub(" ", text).strip()


def is_safe_story_url(url: str) -> bool:
    """Only http(s) links may be stored — feed content is untrusted and a
    javascript: URL would otherwise flow through to published pages."""
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def parse_published(entry: dict[str, Any]) -> str:
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            dt = datetime(*parsed[:6], tzinfo=timezone.utc)
            return dt.isoformat()
    for key in ("published", "updated"):
        raw = entry.get(key)
        if raw:
            try:
                return parsedate_to_datetime(raw).astimezone(timezone.utc).isoformat()
            except (TypeError, ValueError):
                continue
    return utc_now()


def estimate_read_time(text: str) -> int:
    words = len(clean_text(text).split())
    return max(1, round(words / 220))


def compile_keyword_pattern(keywords: list[str]) -> re.Pattern[str] | None:
    """Build one whole-word regex for all keywords (case-insensitive).

    Word boundaries stop short country codes such as "nz" or "sg" matching
    inside unrelated words ("in" inside "innovation", "th" inside "the").
    """
    terms = [keyword.strip().lower() for keyword in keywords if keyword.strip()]
    if not terms:
        return None
    alternation = "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True))
    return re.compile(rf"\b(?:{alternation})\b")


def score_apac_relevance(
    title: str,
    excerpt: str,
    source: dict[str, Any],
    keyword_pattern: re.Pattern[str] | None = None,
) -> float:
    if keyword_pattern is None:
        keywords = load_edition_config().get("scoring", {}).get("apac_keywords", [])
        keyword_pattern = compile_keyword_pattern(keywords)
    haystack = f"{title} {excerpt}".lower()
    hits = len(set(keyword_pattern.findall(haystack))) if keyword_pattern else 0
    keyword_score = min(1.0, hits / 4)
    boost = float(source.get("region_boost", 0.0))
    if source.get("region") == "APAC":
        boost += 0.15
    return round(min(1.0, keyword_score * 0.75 + boost), 3)


CATEGORY_RULES: dict[str, tuple[str, ...]] = {
    "policy": ("regulation", "privacy", "law", "government", "compliance", "gdpr", "act"),
    "security": ("breach", "ransomware", "cve", "vulnerability", "hack", "malware", "phishing"),
    "ai": ("ai", "llm", "machine learning", "openai", "anthropic", "model"),
    "fintech": ("payment", "bank", "fintech", "upi", "crypto", "lending"),
    "startups": ("funding", "series", "seed", "venture", "startup", "raises"),
    "engineering": ("kubernetes", "open source", "github", "developer", "api", "cloud"),
}

CATEGORY_PATTERNS: dict[str, re.Pattern[str]] = {
    category: re.compile(r"\b(?:" + "|".join(re.escape(term) for term in terms) + r")\b")
    for category, terms in CATEGORY_RULES.items()
}


def guess_category(title: str, excerpt: str, default: str) -> str:
    haystack = f"{title} {excerpt}".lower()
    for category, pattern in CATEGORY_PATTERNS.items():
        if pattern.search(haystack):
            return category
    return default


def fetch_feed(url: str) -> feedparser.FeedParserDict:
    require_https_url(url, label="Feed URL")
    headers = {"User-Agent": "BriefAPAC/0.1 (+https://github.com/local/brief-apac)"}
    with httpx.Client(timeout=20.0, headers=headers, **HTTPS_CLIENT_DEFAULTS) as client:
        response = client.get(url)
        response.raise_for_status()
        return feedparser.parse(response.text)


def ingest_sources(max_per_source: int = 15, min_score: float | None = None) -> dict[str, int]:
    edition = load_edition_config()
    threshold = min_score if min_score is not None else edition["edition"]["min_apac_score"]
    keyword_pattern = compile_keyword_pattern(
        edition.get("scoring", {}).get("apac_keywords", [])
    )
    stats = {"fetched": 0, "stored": 0, "skipped_low_score": 0, "errors": 0}

    for source in load_sources_config():
        try:
            feed = fetch_feed(source["url"])
        except Exception as exc:
            logger.warning("Feed %s (%s) failed: %s", source.get("name"), source.get("url"), exc)
            stats["errors"] += 1
            continue

        for entry in feed.entries[:max_per_source]:
            stats["fetched"] += 1
            title = clean_text(entry.get("title", ""))
            link = entry.get("link", "").strip()
            if not title or not is_safe_story_url(link):
                continue

            excerpt = clean_text(
                entry.get("summary")
                or entry.get("description")
                or entry.get("content", [{}])[0].get("value", "")
            )
            score = score_apac_relevance(title, excerpt, source, keyword_pattern)
            if score < threshold:
                stats["skipped_low_score"] += 1
                continue

            story = Story(
                id=None,
                url=link,
                title=title,
                source_name=source["name"],
                published_at=parse_published(entry),
                excerpt=excerpt[:1200],
                category=guess_category(title, excerpt, source.get("default_category", "misc")),
                apac_score=score,
                read_time_minutes=estimate_read_time(excerpt or title),
                status=StoryStatus.CANDIDATE,
            )
            upsert_story(story)
            stats["stored"] += 1

    return stats
