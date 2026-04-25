from content_engine.models.source_item import SourceItem
from content_engine.services.workflow_a import (
    build_filming_card,
    build_video_intake_record,
    build_video_publish_item,
    build_video_script,
    develop_video_hooks,
    select_best_hook,
)


def make_video_source_item() -> SourceItem:
    return SourceItem(
        item_id="itm_vid_001",
        source_type="instagram_reel",
        source_name="@clearrealestate",
        source_url="https://instagram.com/reel/1",
        external_item_id="1",
        collected_at="2026-04-24T08:00:00Z",
        published_at="2026-04-24T07:45:00Z",
        content_hash="hash_vid_001",
        dedupe_key="instagram:1",
        audience_segment="developer_investor",
        content_theme="boutique_hotels",
        raw_payload={
            "video_title": "What cheap villas hide",
            "caption_text": "Cheap villas are never actually cheap.",
            "spoken_transcript": (
                "Cheap villas are never actually cheap when legal, design, and management costs arrive."
            ),
            "transcript_source": "caption_or_transcript",
        },
        transcript_text="Cheap villas are never actually cheap when legal, design, and management costs arrive.",
        media_urls=["https://cdn.example.com/reel.mp4"],
        engagement_signals={"views": 5200, "saves": 140},
        routing_decision="workflow_a",
        routing_reason="video-native market hook",
        routing_confidence=0.94,
        processing_state="collected",
    )


def test_build_video_intake_record_extracts_title_transcript_refs_and_metrics() -> None:
    intake = build_video_intake_record(make_video_source_item())

    assert intake.title == "What cheap villas hide"
    assert intake.caption_text == "Cheap villas are never actually cheap."
    assert "management costs arrive" in intake.spoken_transcript
    assert intake.transcript_source == "caption_or_transcript"
    assert intake.video_refs == [
        "https://instagram.com/reel/1",
        "https://cdn.example.com/reel.mp4",
    ]
    assert intake.metrics == {"views": 5200, "saves": 140}
    assert intake.content_theme == "boutique_hotels"


def test_develop_video_hooks_returns_five_candidates() -> None:
    hooks = develop_video_hooks(make_video_source_item(), platform="instagram")

    assert len(hooks) == 5
    assert hooks[0].platform == "instagram"


def test_select_best_hook_returns_highest_score() -> None:
    hooks = develop_video_hooks(make_video_source_item(), platform="instagram")

    best_hook = select_best_hook(hooks)

    assert best_hook.score == max(hook.score for hook in hooks)


def test_build_video_script_creates_scripted_queue_item() -> None:
    best_hook = select_best_hook(develop_video_hooks(make_video_source_item(), platform="instagram"))

    script = build_video_script(
        best_hook,
        title="Why cheap villas cost more",
        body_points=[
            "Cheap entry price hides legal friction.",
            "Design shortcuts destroy resale trust.",
        ],
        cta="Comment if you want the zero-bullshit checklist.",
    )

    assert script.status == "scripted"
    assert "Comment if you want the zero-bullshit checklist." in script.script_text


def test_build_filming_card_preserves_priority() -> None:
    best_hook = select_best_hook(develop_video_hooks(make_video_source_item(), platform="instagram"))
    script = build_video_script(
        best_hook,
        title="Why cheap villas cost more",
        body_points=["Point one", "Point two"],
        cta="Save this.",
    )

    card = build_filming_card(script, filming_priority=2)

    assert card.linked_script_id == script.script_id
    assert card.filming_priority == 2


def test_build_video_publish_item_marks_item_ready() -> None:
    best_hook = select_best_hook(develop_video_hooks(make_video_source_item(), platform="instagram"))
    script = build_video_script(
        best_hook,
        title="Why cheap villas cost more",
        body_points=["Point one", "Point two"],
        cta="Save this.",
    )

    publish_item = build_video_publish_item(
        script,
        caption="Zero bullshit reel about villa pricing.",
    )

    assert publish_item.linked_script_id == script.script_id
    assert publish_item.status == "ready"
