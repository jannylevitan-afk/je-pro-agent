from content_engine.knowledge.research_dependencies import resolve_research_dependencies


def test_resolve_research_dependencies_maps_founder_journey_for_workflow_b(source_item) -> None:
    item = source_item.model_copy(
        update={
            "audience_segment": "dreamer_woman",
            "content_theme": "founder_journey",
            "source_type": "instagram_profile",
        }
    )

    profile = resolve_research_dependencies(item, workflow="workflow_b")

    assert profile.route == "workflow_b"
    assert "lifestyle" in profile.content_pillars
    assert "founder struggle" in profile.narrative_types
    assert "family/business tension" in profile.collect_fields
    assert "audience pain and trigger" in profile.workflow_intake
    assert profile.suggested_registers == ["register_7", "register_8", "register_9"]


def test_resolve_research_dependencies_adds_video_fields_for_workflow_a(video_source_item) -> None:
    profile = resolve_research_dependencies(video_source_item, workflow="workflow_a")

    assert profile.workflow == "workflow_a"
    assert "video refs" in profile.collect_fields
    assert "first 3 seconds" in profile.collect_fields
    assert "visual device" in profile.workflow_intake
    assert "source URL" in profile.evidence_required
