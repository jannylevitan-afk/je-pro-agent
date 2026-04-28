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


def test_resolve_research_dependencies_adds_jane_blog_rubric_search_rules(source_item) -> None:
    item = source_item.model_copy(update={"content_theme": "bali_travel"})

    profile = resolve_research_dependencies(item, workflow="workflow_b")

    assert "Jane blog rubric fit" in profile.collect_fields
    assert "narrow topic" in profile.collect_fields
    assert "info occasion" in profile.collect_fields
    assert "serial angle" in profile.collect_fields
    assert "Only keep sources that fit one approved Jane blog rubric." in profile.workflow_intake
    assert "Rubric: #bali life" in profile.writer_context
    assert "1 мысль / 1 эмоция / 1 сюжет" in profile.writer_context


def test_resolve_research_dependencies_requires_best_performing_post_extraction_fields(source_item) -> None:
    profile = resolve_research_dependencies(source_item, workflow="workflow_b")

    required_fields = [
        "best-performing post URL",
        "public engagement metrics: views, likes, comments, saves, shares",
        "engagement score and selection reason",
        "post title or carousel headline",
        "caption / description text",
        "carousel or image OCR text when available",
        "copied source post text for source-note handoff",
    ]

    for field in required_fields:
        assert field in profile.collect_fields
