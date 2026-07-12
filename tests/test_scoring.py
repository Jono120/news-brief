from __future__ import annotations

from brief.ingest import (
    clean_text,
    compile_keyword_pattern,
    estimate_read_time,
    guess_category,
    score_apac_relevance,
)

KEYWORDS = ["singapore", "new zealand", "nz", "au", "japan", "tokyo", "apac"]
PATTERN = compile_keyword_pattern(KEYWORDS)

GLOBAL_SOURCE = {"region": "GLOBAL", "region_boost": 0.0}
APAC_SOURCE = {"region": "APAC", "region_boost": 0.25}


class TestScoreApacRelevance:
    def test_generic_english_text_scores_zero_for_global_source(self):
        # Words like "in", "my", "the" must not count as country-code hits.
        score = score_apac_relevance(
            "The company said my invoice arrived in minutes",
            "Nothing regional in this innovative announcement.",
            GLOBAL_SOURCE,
            PATTERN,
        )
        assert score == 0.0

    def test_short_codes_only_match_whole_words(self):
        assert (
            score_apac_relevance("Snz Corp launches Xau widget", "", GLOBAL_SOURCE, PATTERN)
            == 0.0
        )
        assert score_apac_relevance("NZ startup expands", "", GLOBAL_SOURCE, PATTERN) > 0.0

    def test_regional_keywords_raise_score(self):
        score = score_apac_relevance(
            "Singapore and Japan sign digital trade pact",
            "Tokyo firms to benefit across APAC.",
            GLOBAL_SOURCE,
            PATTERN,
        )
        assert score == 0.75  # 4 distinct hits saturate the keyword component

    def test_repeated_keyword_counts_once(self):
        score = score_apac_relevance(
            "Singapore, Singapore, Singapore, Singapore",
            "",
            GLOBAL_SOURCE,
            PATTERN,
        )
        assert score == round(0.25 * 0.75, 3)

    def test_apac_source_boost_applies(self):
        score = score_apac_relevance("Nothing regional here", "", APAC_SOURCE, PATTERN)
        assert score == 0.4  # 0.25 region_boost + 0.15 APAC bonus

    def test_score_is_capped_at_one(self):
        source = {"region": "APAC", "region_boost": 0.9}
        score = score_apac_relevance(
            "Singapore Japan Tokyo APAC", "", source, PATTERN
        )
        assert score == 1.0

    def test_falls_back_to_edition_config_when_no_pattern_given(self):
        # Real config: generic English prose must not pass the 0.35 threshold
        # on keyword hits alone for a non-APAC source.
        score = score_apac_relevance(
            "The team said it was thrilled by my demo in the morning",
            "An update that is not about the region at all.",
            GLOBAL_SOURCE,
        )
        assert score < 0.35


class TestGuessCategory:
    def test_word_boundaries_prevent_substring_matches(self):
        # "api" must not match inside "rapid", "ai" not inside "said".
        assert guess_category("Rapid growth, the CEO said", "", "misc") == "misc"

    def test_policy_keywords(self):
        assert guess_category("New privacy act passed by government", "", "misc") == "policy"

    def test_ai_keywords(self):
        assert guess_category("OpenAI ships a new model", "", "misc") == "ai"

    def test_default_when_no_rule_matches(self):
        assert guess_category("Weather update", "Sunny weekend ahead", "startups") == "startups"


def test_compile_keyword_pattern_empty_returns_none():
    assert compile_keyword_pattern([]) is None
    assert compile_keyword_pattern(["  "]) is None


def test_clean_text_strips_tags_and_entities():
    assert clean_text("<p>Hello&nbsp;<b>world</b></p>") == "Hello world"


def test_estimate_read_time_minimum_one_minute():
    assert estimate_read_time("short") == 1
