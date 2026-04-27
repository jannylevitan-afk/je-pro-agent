from content_engine.context.jane_blog_rubrics import (
    JANE_ANALYST_REVIEW_LOOP_RULES,
    JANE_AUDIENCE_FUNCTION_RULES,
    JANE_BLOG_RUBRICS,
    JANE_STORY_STRUCTURE_RULES,
    resolve_jane_blog_rubric,
)


def test_jane_blog_rubrics_include_all_user_defined_series() -> None:
    expected = {
        "bali_life": "#bali life",
        "lifestyle": "lifestyle",
        "real_estate": "#недвижка",
        "relationships": "#отношения",
        "founder_notes": "#заметки фаундера",
        "experience": "#experience",
    }

    assert {key: rubric.label for key, rubric in JANE_BLOG_RUBRICS.items()} == expected
    assert "новые места" in JANE_BLOG_RUBRICS["bali_life"].source_fit
    assert "личный опыт балийской жизни" in JANE_BLOG_RUBRICS["lifestyle"].source_fit
    assert "земли" in JANE_BLOG_RUBRICS["real_estate"].source_fit
    assert "мужем и бизнес-партнёром" in JANE_BLOG_RUBRICS["relationships"].source_fit
    assert "миллион $" in JANE_BLOG_RUBRICS["founder_notes"].source_fit
    assert "hospitality, business, art" in JANE_BLOG_RUBRICS["experience"].source_fit


def test_resolve_jane_blog_rubric_uses_theme_and_source_specific_overrides() -> None:
    assert resolve_jane_blog_rubric("bali_travel").key == "bali_life"
    assert resolve_jane_blog_rubric("market_reports").key == "real_estate"
    assert resolve_jane_blog_rubric("wellness_architecture").key == "experience"
    assert resolve_jane_blog_rubric("founder_journey").key == "lifestyle"
    assert resolve_jane_blog_rubric("founder_journey", "муж, семья, ребёнок и роль матери").key == "relationships"
    assert resolve_jane_blog_rubric("founder_journey", "как заработать миллион $ и не сойти с ума").key == "founder_notes"


def test_jane_content_function_and_review_loop_rules_are_explicit() -> None:
    joined_function_rules = " ".join(JANE_AUDIENCE_FUNCTION_RULES)
    joined_structure_rules = " ".join(JANE_STORY_STRUCTURE_RULES)
    joined_review_rules = " ".join(JANE_ANALYST_REVIEW_LOOP_RULES)

    assert "мотивация и энергия" in joined_function_rules
    assert "реальность жизни" in joined_function_rules
    assert "рефлексия" in joined_function_rules
    assert "польза в форме опыта" in joined_function_rules
    assert "1 мысль / 1 эмоция / 1 сюжет" in joined_structure_rules
    assert "якорь / интрига -> история / контекст -> умозаключение" in joined_structure_rules
    assert "каждый Instagram post is an info occasion" in joined_structure_rules
    assert "maximum 3 review passes" in joined_review_rules
    assert "return after the third pass" in joined_review_rules
