from content_engine.models.workflow_b import DraftBundle
from content_engine.services.editing import run_editorial_gate


def make_bundle(
    text_ru: str = "Бутик-отели дают ROI в 3 раза выше, чем массовый сегмент.",
    platform_lane: str = "instagram_professional",
    text_en: str | None = None,
) -> DraftBundle:
    return DraftBundle(
        title="Test draft",
        platform="instagram",
        platform_lane=platform_lane,
        working_language="ru",
        publish_language="ru",
        audience_portrait="developer_investor",
        voice_register="register_2",
        funnel_role="authority",
        draft_text_ru=text_ru,
        draft_text_en=text_en,
    )


def test_clean_draft_passes_editorial_gate() -> None:
    bundle = make_bundle()
    result = run_editorial_gate(
        draft=bundle,
        fact_claims=["boutique ROI exceeds mass-market"],
        verified_facts={"boutique ROI exceeds mass-market"},
    )

    assert result.seven_point_passed is True
    assert result.factual_safety == "clean"
    assert result.failed_checks == []


def test_banned_phrase_fails_gate() -> None:
    bundle = make_bundle(text_ru="В современном мире бутик-отели становятся уникальным решением.")
    result = run_editorial_gate(
        draft=bundle,
        fact_claims=[],
        verified_facts=set(),
    )

    assert result.seven_point_passed is False
    assert any("banned_phrases" in check for check in result.failed_checks)


def test_fully_unverified_claims_block_draft() -> None:
    bundle = make_bundle()
    result = run_editorial_gate(
        draft=bundle,
        fact_claims=["boutique ROI exceeds mass-market", "occupancy hits 90%"],
        verified_facts=set(),
    )

    assert result.factual_safety == "blocked"
    assert result.seven_point_passed is False


def test_partial_verification_needs_human_confirmation() -> None:
    bundle = make_bundle()
    result = run_editorial_gate(
        draft=bundle,
        fact_claims=["boutique ROI exceeds mass-market", "occupancy hits 90%"],
        verified_facts={"boutique ROI exceeds mass-market"},
    )

    assert result.factual_safety == "needs_human_confirmation"
    assert result.seven_point_passed is True
    assert len(result.warnings) == 1


def test_no_claims_produces_clean_safety() -> None:
    bundle = make_bundle()
    result = run_editorial_gate(
        draft=bundle,
        fact_claims=[],
        verified_facts=set(),
    )

    assert result.factual_safety == "clean"
    assert result.seven_point_passed is True


def test_theme_restate_opening_fails_gate() -> None:
    bundle = make_bundle(
        text_ru="Сегодня я хочу рассказать про рынок бутик-отелей на Бали. Здесь всё решает логика сделки."
    )

    result = run_editorial_gate(
        draft=bundle,
        fact_claims=[],
        verified_facts=set(),
    )

    assert result.seven_point_passed is False
    assert any("opening_restates_theme" in check for check in result.failed_checks)


def test_summary_closing_fails_gate() -> None:
    bundle = make_bundle(
        text_ru="Дешёвые сделки часто оказываются самыми дорогими. В итоге можно сказать, что надо просто верить в мечту."
    )

    result = run_editorial_gate(
        draft=bundle,
        fact_claims=[],
        verified_facts=set(),
    )

    assert result.seven_point_passed is False
    assert any("summary_or_motivation_ending" in check for check in result.failed_checks)
