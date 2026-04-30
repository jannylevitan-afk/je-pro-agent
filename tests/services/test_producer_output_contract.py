from content_engine.models.producer import CreatorProfile, ProductOffer, ProducerContext, SeasonSeed
from content_engine.services.producer import run_producer_workflow
from content_engine.services.producer_output_contract import (
    PRODUCER_OUTPUT_SECTION_ORDER,
    build_readable_producer_output,
    format_producer_output_html,
    format_producer_output_markdown,
)


def make_context() -> ProducerContext:
    return ProducerContext(
        creator=CreatorProfile(
            name="Jane Levitan",
            role="CEO / creator",
            niche="Bali real estate, hospitality, events, and founder lifestyle",
            positioning="Jane turns Bali life and premium real estate into a serialized founder-product story.",
            values=["source-backed judgment", "aesthetic precision"],
            tone="честный, спокойный, взрослый, эстетичный",
            personal_boundaries=["no private child details", "no NDA details"],
            allowed_personal_themes=["recovery", "founder life", "Bali real estate"],
            forbidden_themes=["fake urgency", "invented revenue", "private client data"],
            current_life_context="Jane is preparing a season around a phygital ocean villa launch.",
        ),
        audience=["event producers", "investors", "founders"],
        offers=[
            ProductOffer(
                offer_id="villa_first_look",
                name="Phygital Ocean Villa Bali",
                offer_type="first_look",
                target_audience="wedding planners, event producers, brands, investors",
                core_problem="People choose villas by visuals while hidden systems decide quality and risk.",
                promised_transformation="Create an event in a space where architecture, quality, and experience work together.",
                proof_assets=["NDA-safe project teasers", "Bali quality checklist"],
                main_objections=["Is this just a beautiful villa?", "What about mold and delays?"],
                funnel_steps=["attention", "problem_recognition", "trust", "first_look"],
                cta_options=["ВИЛЛА", "БАЛИ", "КОМАНДА"],
            )
        ],
        channels=["instagram", "telegram", "linkedin"],
        constraints=["no auto-publishing", "manual review", "NDA-safe only"],
        season_seed=SeasonSeed(
            seed_id="villa_launch_001",
            season_goal="Build a 28-day serial around recovery, invisible quality, and the villa first look.",
            current_context="Jane is returning from recovery and preparing the public launch path.",
            offer_focus="Phygital Ocean Villa Bali",
            rubrics_to_emphasize=["#bali life", "#недвижка", "#заметки фаундера", "#experience"],
            audience_focus=["event producers", "investors", "founders"],
            channels=["instagram", "telegram", "linkedin"],
            constraints=["no medical clickbait", "no NDA leaks", "no guaranteed ROI"],
            date_range="28 days",
            success_metrics=["DM ВИЛЛА", "DM БАЛИ", "qualified first-look requests"],
        ),
    )


def test_readable_producer_output_keeps_required_section_order() -> None:
    context = make_context()
    runtime_output = run_producer_workflow(context, created_at="2026-04-30T10:00:00+08:00")

    readable = build_readable_producer_output(runtime_output, context=context)

    assert readable.section_order == PRODUCER_OUTPUT_SECTION_ORDER
    assert readable.title == runtime_output.season.title
    assert readable.producer_brief.creator_name == "Jane Levitan"
    assert readable.season_bible.season_id == runtime_output.season.season_id
    assert readable.scene_cards == runtime_output.scenes


def test_readable_producer_output_dispatches_workflow_a_to_video_entity() -> None:
    context = make_context()
    runtime_output = run_producer_workflow(context, created_at="2026-04-30T10:00:00+08:00")

    readable = build_readable_producer_output(runtime_output, context=context)

    tasks = {task.target_agent: task for task in readable.agent_tasks}
    assert tasks["video_asset_agent"].display_name == "Video / AssetAgent"
    assert tasks["video_asset_agent"].workflow == "workflow_a"
    assert "Workflow A" in " ".join(tasks["video_asset_agent"].responsibilities)
    assert "hook" in " ".join(tasks["video_asset_agent"].responsibilities).lower()
    assert "script" in " ".join(tasks["video_asset_agent"].responsibilities).lower()
    assert tasks["copywriter_agent"].workflow == "workflow_b"
    assert "Workflow B" in " ".join(tasks["copywriter_agent"].responsibilities)


def test_readable_producer_output_keeps_calendar_manual_not_autopublish() -> None:
    context = make_context()
    runtime_output = run_producer_workflow(context, created_at="2026-04-30T10:00:00+08:00")

    readable = build_readable_producer_output(runtime_output, context=context)

    calendar_task = next(task for task in readable.agent_tasks if task.target_agent == "manual_publishing_calendar")
    assert calendar_task.display_name == "Manual Publishing / Calendar"
    assert calendar_task.workflow == "manual_ops"
    assert "no auto-publishing" in calendar_task.constraints
    assert all("auto-publish" not in responsibility.lower() for responsibility in calendar_task.responsibilities)


def test_markdown_formatter_matches_human_readable_producer_output() -> None:
    context = make_context()
    runtime_output = run_producer_workflow(context, created_at="2026-04-30T10:00:00+08:00")
    readable = build_readable_producer_output(runtime_output, context=context)

    markdown = format_producer_output_markdown(readable)

    assert markdown.startswith("# ProducerOutput")
    assert "## Producer Brief" in markdown
    assert "## Season Bible" in markdown
    assert "## Scene Cards" in markdown
    assert "## Tasks for Workflow Agents" in markdown
    assert "Video / AssetAgent" in markdown
    assert "Workflow A" in markdown
    assert "Workflow B" in markdown


def test_html_formatter_is_local_readable_and_uses_larger_text() -> None:
    context = make_context()
    runtime_output = run_producer_workflow(context, created_at="2026-04-30T10:00:00+08:00")
    readable = build_readable_producer_output(runtime_output, context=context)

    html = format_producer_output_html(readable)

    assert "<!DOCTYPE html>" in html
    assert "font-size: 17px" in html
    assert "Video / AssetAgent" in html
    assert "Workflow A" in html
    assert "Workflow B" in html
    assert "https://" not in html
    assert "fonts.googleapis" not in html
