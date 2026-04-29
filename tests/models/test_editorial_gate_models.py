import pytest

from content_engine.models.editorial_gate import EditorialReviewResult


def test_editorial_review_result_caps_review_passes_at_three() -> None:
    with pytest.raises(ValueError):
        EditorialReviewResult(
            review_id="review_001",
            content_id="content_001",
            source_item_id="itm_001",
            passed=False,
            approval_status="needs_revision",
            score=0.62,
            failed_checks=["generic opening"],
            revision_notes=["Rewrite first line."],
            factual_risk_flags=[],
            voice_risk_flags=["too generic"],
            review_pass_number=4,
            created_at="2026-04-29T10:00:00+08:00",
        )


def test_editorial_review_result_requires_human_review_status_when_passed() -> None:
    with pytest.raises(ValueError, match="approved_for_human_review"):
        EditorialReviewResult(
            review_id="review_002",
            content_id="content_002",
            source_item_id="itm_002",
            passed=True,
            approval_status="needs_revision",
            score=0.92,
            failed_checks=[],
            revision_notes=[],
            factual_risk_flags=[],
            voice_risk_flags=[],
            review_pass_number=1,
            created_at="2026-04-29T10:00:00+08:00",
        )
