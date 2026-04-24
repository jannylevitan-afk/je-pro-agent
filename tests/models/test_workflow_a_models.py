import pytest

from content_engine.models.workflow_a import FilmingCard, VideoHook, VideoPublishItem, VideoScript


def test_video_hook_keeps_angle_type_and_score() -> None:
    hook = VideoHook(
        hook_id="hook_001",
        source_item_id="itm_001",
        platform="instagram",
        content_theme="boutique_hotels",
        angle="Behind the scenes of buyer hesitation",
        hook_text="The cheapest villa usually becomes the most expensive mistake.",
        hook_type="market_warning",
        score=9,
    )

    assert hook.hook_type == "market_warning"
    assert hook.score == 9


def test_video_publish_item_requires_publish_date_when_published() -> None:
    with pytest.raises(ValueError, match="publish_date"):
        VideoPublishItem(
            publish_item_id="pub_001",
            linked_script_id="scr_001",
            platform="instagram",
            caption="Zero bullshit reel.",
            status="published",
        )


def test_filming_card_keeps_human_production_fields() -> None:
    card = FilmingCard(
        card_id="film_001",
        linked_script_id="scr_001",
        filming_priority=1,
        filmed=False,
    )

    assert card.filming_priority == 1

