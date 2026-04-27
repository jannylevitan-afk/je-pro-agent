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
    assert "source hook" in profile.collect_fields
    assert "public comments / reactions" in profile.collect_fields
    assert "repeatable formula" in profile.collect_fields
    assert "immutable raw payload snapshot" in profile.collect_fields
    assert "visual device" in profile.workflow_intake
    assert "hook quality gate" in profile.workflow_intake
    assert "source URL" in profile.evidence_required
    assert "canonical upstream item" in profile.evidence_required


def test_resolve_research_dependencies_adds_video_context_boundary_for_workflow_b(video_source_item) -> None:
    item = video_source_item.model_copy(update={"routing_decision": "both"})

    profile = resolve_research_dependencies(item, workflow="workflow_b")

    assert "video-source context boundary" in profile.workflow_intake
    assert "Use video hooks only as source/evidence context, not as Workflow B final hooks or scripts." in profile.writer_context
