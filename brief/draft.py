from __future__ import annotations

import logging
import os
import re

import httpx

from brief.models import Story, StoryStatus, load_edition_config, list_stories, update_story
from brief.server import HTTPS_CLIENT_DEFAULTS

logger = logging.getLogger(__name__)

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def first_sentences(text: str, count: int = 2) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return ""
    parts = SENTENCE_SPLIT.split(cleaned)
    return " ".join(parts[:count]).strip()


def extractive_summary(story: Story) -> str:
    base = story.excerpt or story.title
    summary = first_sentences(base, 2)
    if len(summary) < 40 and story.excerpt:
        summary = story.excerpt[:280].rsplit(" ", 1)[0] + "…"
    return summary


def apac_why_line(story: Story) -> str:
    templates = {
        "policy": "Regulatory shifts in APAC can change product obligations faster than US-only coverage suggests.",
        "security": "Security incidents in the region often surface first through local operators and regulators.",
        "fintech": "Payments and banking innovation in APAC frequently leads global adoption patterns.",
        "startups": "Funding and GTM dynamics in APAC differ materially from Silicon Valley playbooks.",
        "ai": "Model access, compute, and deployment constraints vary widely across APAC markets.",
        "engineering": "Engineering teams across APAC are adopting and adapting these tools at scale.",
        "misc": "Worth tracking for builders and operators with APAC customers, teams, or infrastructure.",
    }
    return templates.get(story.category, templates["misc"])


def llm_summary(story: Story) -> tuple[str, str] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    prompt = f"""You are editing a concise APAC tech briefing. Use New Zealand English spelling in any prose.

Title: {story.title}
Source: {story.source_name}
Excerpt: {story.excerpt[:1500]}

Return exactly two lines:
LINE1: A 2-sentence neutral summary (max 280 characters total).
LINE2: One sentence explaining why this matters for APAC tech professionals.

No markdown, no bullet points."""

    try:
        # OpenAI endpoint is fixed; excerpts in the prompt come from trusted ingest
        # output (config/sources.yaml feeds), not arbitrary user input.
        with httpx.Client(timeout=45.0, **HTTPS_CLIENT_DEFAULTS) as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    "temperature": 0.2,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            if len(lines) >= 2:
                return lines[0], lines[1]
            logger.warning(
                "LLM returned an unexpected format for %r — using extractive summary",
                story.title,
            )
    except Exception as exc:
        logger.warning(
            "LLM summary failed for %r (%s) — using extractive summary", story.title, exc
        )
        return None
    return None


def draft_story(story: Story, use_llm: bool = True) -> Story:
    summary = ""
    why = ""
    if use_llm:
        llm = llm_summary(story)
        if llm:
            summary, why = llm

    if not summary:
        summary = extractive_summary(story)
    if not why:
        why = apac_why_line(story)

    story.summary = summary
    story.why_it_matters = why
    story.status = StoryStatus.DRAFTED
    return story


def draft_candidates(limit: int | None = None, use_llm: bool = True) -> int:
    edition = load_edition_config()
    target = limit or edition["edition"]["stories_per_issue"] * 2
    candidates = list_stories(StoryStatus.CANDIDATE, limit=target)
    drafted = 0
    for story in candidates:
        drafted_story = draft_story(story, use_llm=use_llm)
        update_story(
            drafted_story.id,
            summary=drafted_story.summary,
            why_it_matters=drafted_story.why_it_matters,
            status=StoryStatus.DRAFTED,
        )
        drafted += 1
    return drafted
