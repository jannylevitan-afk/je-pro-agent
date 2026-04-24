from content_engine.models.workflow_b import IdeaCandidate, InsightCard
from content_engine.notion.payloads import build_idea_properties, build_insight_properties
from content_engine.notion.sync import create_idea, create_insight
from tests.notion.conftest import StubNotionClient, first_text


def make_insight() -> InsightCard:
    return InsightCard(
        audience="developer_investor",
        platform="telegram",
        content_theme="boutique_hotels",
        content_pillar="expertise_proof",
        narrative_type="market_observation",
        priority=2,
        reuse_score=4,
        emotional_trigger="status anxiety",
        useful_lesson="Boutique hotel ROI beats mass market when structure and operations align.",
    )


def make_idea() -> IdeaCandidate:
    return IdeaCandidate(
        working_title="Why boutique yield beats cheap inventory",
        target_platform="linkedin",
        platform_lane="linkedin_b2b",
        language_mode="ru",
        funnel_role="authority",
        target_audience="developer_investor",
        content_pillar="expertise_proof",
        emotional_hook="Call out the false economy behind cheap deals.",
        useful_point="Cheap inventory often hides legal and operating drag.",
        desired_reaction="Prompt investor replies",
        suggested_format="thought_leadership_post",
    )


def test_build_insight_properties_maps_schema_fields() -> None:
    insight = make_insight()

    props = build_insight_properties(insight)

    assert first_text(props["Topic"]) == "boutique_hotels"
    assert first_text(props["Angle"]) == "Boutique hotel ROI beats mass market when structure and operations align."
    assert props["Audience portrait"] == {"select": {"name": "developer_investor"}}
    assert props["Narrative type"] == {"select": {"name": "market_observation"}}
    assert props["Reuse score"] == {"number": 4}


def test_build_idea_properties_maps_gate_and_status() -> None:
    idea = make_idea()

    props = build_idea_properties(
        idea,
        gate_passed=True,
        status="ready",
    )

    assert first_text(props["Desired reaction"]) == "Prompt investor replies"
    assert props["Platform lane"] == {"select": {"name": "linkedin_b2b"}}
    assert props["Gate passed"] == {"checkbox": True}
    assert props["Status"] == {"select": {"name": "ready"}}


def test_create_insight_calls_notion_create() -> None:
    client = StubNotionClient(create_results=[{"id": "ins_001"}])

    response = create_insight(client, "db_insights", make_insight())

    assert response["id"] == "ins_001"
    assert client.create_calls[0][0] == "db_insights"


def test_create_idea_calls_notion_create() -> None:
    client = StubNotionClient(create_results=[{"id": "idea_001"}])

    response = create_idea(
        client,
        "db_ideas",
        make_idea(),
        gate_passed=True,
        status="ready",
    )

    assert response["id"] == "idea_001"
    sent_props = client.create_calls[0][1]
    assert sent_props["Status"] == {"select": {"name": "ready"}}
