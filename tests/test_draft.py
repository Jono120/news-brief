from __future__ import annotations

from brief.draft import apac_why_line, draft_story, extractive_summary, first_sentences
from brief.entities import StoryStatus
from tests.conftest import make_story


def test_first_sentences_takes_leading_pair():
    text = "One here. Two here! Three here? Four here."
    assert first_sentences(text, 2) == "One here. Two here!"


def test_first_sentences_empty_input():
    assert first_sentences("   ") == ""


def test_extractive_summary_uses_excerpt():
    story = make_story(excerpt="First sentence of the story. Second sentence follows. Third.")
    assert extractive_summary(story) == "First sentence of the story. Second sentence follows."


def test_draft_story_without_llm_sets_fields_and_status():
    story = make_story()
    drafted = draft_story(story, use_llm=False)
    assert drafted.status == StoryStatus.DRAFTED
    assert drafted.summary
    assert drafted.why_it_matters == apac_why_line(story)


def test_apac_why_line_unknown_category_falls_back_to_misc():
    story = make_story(category="does-not-exist")
    assert apac_why_line(story) == apac_why_line(make_story(category="misc"))
