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
            "first_3_seconds": "A villa price flashes on screen, then the permit folder appears.",
            "source_hook": "Cheap villas are never actually cheap.",
            "visual_device": "price tag cut to legal documents",
            "hook_pattern": "cheap surface -> hidden structural cost",
            "hook_tension": "beautiful entry price vs expensive legal reality",
            "hook_promise": "learn what to check before trusting the price",
            "hook_cta": "save before you inspect a villa",
            "repeatable_formula": "Show the attractive surface, then reveal the hidden operating risk.",
            "hook_modality": "hybrid",
            "comments_sample": ["I wish someone told me this before my first viewing."],
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


def test_build_video_intake_record_exposes_hook_mining_context() -> None:
    intake = build_video_intake_record(make_video_source_item())

    assert intake.first_3_seconds == "A villa price flashes on screen, then the permit folder appears."
    assert intake.source_hook == "Cheap villas are never actually cheap."
    assert intake.visual_device == "price tag cut to legal documents"
    assert intake.hook_pattern == "cheap surface -> hidden structural cost"
    assert intake.hook_tension == "beautiful entry price vs expensive legal reality"
    assert intake.hook_promise == "learn what to check before trusting the price"
    assert intake.hook_cta == "save before you inspect a villa"
    assert intake.repeatable_formula == "Show the attractive surface, then reveal the hidden operating risk."
    assert intake.hook_modality == "hybrid"
    assert intake.comments_sample == ["I wish someone told me this before my first viewing."]


def test_develop_video_hooks_returns_five_candidates() -> None:
    hooks = develop_video_hooks(make_video_source_item(), platform="instagram")

    assert len(hooks) == 5
    assert hooks[0].platform == "instagram"


def test_select_best_hook_returns_highest_score() -> None:
    hooks = develop_video_hooks(make_video_source_item(), platform="instagram")

    best_hook = select_best_hook(hooks)

    assert best_hook.score == max(hook.score for hook in hooks)


def test_develop_video_hooks_uses_source_specific_best_hook() -> None:
    founder_item = make_video_source_item().model_copy(
        update={
            "item_id": "itm_vid_founder",
            "source_name": "@founderlife",
            "source_url": "https://instagram.com/reel/founder",
            "external_item_id": "founder",
            "content_hash": "hash_vid_founder",
            "dedupe_key": "instagram:founder",
            "audience_segment": "dreamer_woman",
            "content_theme": "founder_life",
            "raw_payload": {
                "video_title": "Founder life with family",
                "caption_text": "Ambition and family are not two separate lives.",
                "spoken_transcript": (
                    "A founder talks about family rituals, a child, ambition, and the cost of living for the perfect picture."
                ),
                "transcript_source": "caption_or_transcript",
            },
            "transcript_text": (
                "A founder talks about family rituals, a child, ambition, and the cost of living for the perfect picture."
            ),
        }
    )
    market_item = make_video_source_item().model_copy(
        update={
            "item_id": "itm_vid_market",
            "source_name": "@balimarket",
            "source_url": "https://instagram.com/reel/market",
            "external_item_id": "market",
            "content_hash": "hash_vid_market",
            "dedupe_key": "instagram:market",
            "audience_segment": "developer_investor",
            "content_theme": "bali_market",
            "raw_payload": {
                "video_title": "Bali villa legal risk",
                "caption_text": "The price is not the whole risk.",
                "spoken_transcript": (
                    "A market source explains zoning, legal structure, operator weakness, and resale risk in Bali villas."
                ),
                "transcript_source": "caption_or_transcript",
            },
            "transcript_text": (
                "A market source explains zoning, legal structure, operator weakness, and resale risk in Bali villas."
            ),
        }
    )

    founder_hook = select_best_hook(develop_video_hooks(founder_item, platform="instagram")).hook_text
    market_hook = select_best_hook(develop_video_hooks(market_item, platform="instagram")).hook_text

    assert founder_hook != market_hook
    assert founder_hook != "What looks cheap first is often the most expensive later."
    assert market_hook != "What looks cheap first is often the most expensive later."
    assert any(marker in founder_hook.lower() for marker in ("life", "family", "ambition"))
    assert any(marker in market_hook.lower() for marker in ("bali", "structure", "risk", "price"))


def test_develop_video_hooks_preserves_detected_source_hook_as_primary() -> None:
    item = make_video_source_item().model_copy(
        update={
            "raw_payload": {
                "video_title": "Founder mistake",
                "source_hook": "Everyone sees the villa. Almost nobody checks the permit layer.",
                "caption_text": "Everyone sees the villa. Almost nobody checks the permit layer.",
                "spoken_transcript": (
                    "Everyone sees the villa. Almost nobody checks the permit layer. "
                    "The rest of the video explains legal and zoning risk."
                ),
                "transcript_source": "caption_or_transcript",
            },
            "transcript_text": (
                "Everyone sees the villa. Almost nobody checks the permit layer. "
                "The rest of the video explains legal and zoning risk."
            ),
        }
    )

    best_hook = select_best_hook(develop_video_hooks(item, platform="instagram"))

    assert best_hook.hook_text == "Everyone sees the villa. Almost nobody checks the permit layer."
    assert "source verbatim" in best_hook.angle


def test_develop_video_hooks_prioritizes_declared_content_theme_over_bio_keywords() -> None:
    founder_item = make_video_source_item().model_copy(
        update={
            "item_id": "itm_vid_founder_architect",
            "audience_segment": "dreamer_woman",
            "content_theme": "founder_journey",
            "raw_payload": {
                "video_title": "Architect founder life",
                "caption_text": "Architect founder in Bali shares family and ambition tension.",
                "spoken_transcript": (
                    "Architect founder in Bali designs spaces, but the source is about family rituals, "
                    "a child, ambition, and the cost of performing a perfect life."
                ),
                "transcript_source": "caption_or_transcript",
            },
            "transcript_text": (
                "Architect founder in Bali designs spaces, but the source is about family rituals, "
                "a child, ambition, and the cost of performing a perfect life."
            ),
        }
    )
    travel_item = make_video_source_item().model_copy(
        update={
            "item_id": "itm_vid_bali_travel_resort",
            "audience_segment": "lifestyle_expat",
            "content_theme": "bali_travel",
            "raw_payload": {
                "video_title": "Best dinner spots in Ubud",
                "caption_text": "Hotels, resorts, restaurants, and Ubud dinner spots worth saving.",
                "spoken_transcript": (
                    "Bali travel guide about hotels, resorts, restaurants, beach rituals, and honest place experience."
                ),
                "transcript_source": "caption_or_transcript",
            },
            "transcript_text": (
                "Bali travel guide about hotels, resorts, restaurants, beach rituals, and honest place experience."
            ),
        }
    )

    founder_hook = select_best_hook(develop_video_hooks(founder_item, platform="instagram")).hook_text
    travel_hook = select_best_hook(develop_video_hooks(travel_item, platform="instagram")).hook_text

    assert "life" in founder_hook.lower()
    assert "wellness" not in founder_hook.lower()
    assert "bali" in travel_hook.lower()
    assert "boutique hotel" not in travel_hook.lower()


def test_develop_video_hooks_keeps_same_theme_sources_distinct() -> None:
    school_item = make_video_source_item().model_copy(
        update={
            "item_id": "itm_vid_founder_school",
            "audience_segment": "dreamer_woman",
            "content_theme": "founder_journey",
            "raw_payload": {
                "video_title": "Founder school decision",
                "caption_text": "A founder talks about pregnancy, a child, school, and Bali.",
                "spoken_transcript": "A founder talks about pregnancy, a child, school, and Bali.",
                "transcript_source": "caption_or_transcript",
            },
            "transcript_text": "A founder talks about pregnancy, a child, school, and Bali.",
        }
    )
    course_item = make_video_source_item().model_copy(
        update={
            "item_id": "itm_vid_founder_course",
            "audience_segment": "broker",
            "content_theme": "founder_journey",
            "raw_payload": {
                "video_title": "Broker course confidence",
                "caption_text": "Students, realtors, course, clients, confidence, and first deals.",
                "spoken_transcript": "Students, realtors, course, clients, confidence, and first deals.",
                "transcript_source": "caption_or_transcript",
            },
            "transcript_text": "Students, realtors, course, clients, confidence, and first deals.",
        }
    )

    school_hook = select_best_hook(develop_video_hooks(school_item, platform="instagram")).hook_text
    course_hook = select_best_hook(develop_video_hooks(course_item, platform="instagram")).hook_text

    assert school_hook != course_hook
    assert "school" in school_hook.lower() or "child" in school_hook.lower()
    assert "confidence" in course_hook.lower() or "client" in course_hook.lower()


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
