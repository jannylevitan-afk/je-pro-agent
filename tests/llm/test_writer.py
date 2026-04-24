from content_engine.context.workflow_b_rules import WorkflowBDecision
from content_engine.llm.writer import AnthropicPipelineWriter
from content_engine.models.workflow_b import ContentBrief, InsightCard


class StubAnthropicClient:
    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self.calls: list[dict[str, object]] = []

    def generate_text(
        self,
        *,
        system_prompt: str | None,
        user_prompt: str,
        max_tokens: int,
        model: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "max_tokens": max_tokens,
                "model": model,
                "temperature": temperature,
            }
        )
        return self._responses.pop(0)


def test_write_workflow_b_draft_parses_bilingual_json_payload(source_item) -> None:
    client = StubAnthropicClient(
        responses=[
            """```json
            {"draft_text_ru":"Русский драфт.","draft_text_en":"English draft."}
            ```"""
        ]
    )
    writer = AnthropicPipelineWriter(client)
    insight = InsightCard(
        audience="developer_investor",
        platform="linkedin",
        content_theme="boutique_hotels",
        content_pillar="expertise_proof",
        narrative_type="market observation",
        priority=2,
        reuse_score=4,
        emotional_trigger="status anxiety",
        useful_lesson="Boutique hotel ROI beats mass-market in Bali.",
    )
    brief = ContentBrief(
        audience="developer_investor",
        platform="linkedin",
        platform_lane="linkedin_b2b",
        working_language="ru",
        publish_language="en",
        funnel_role="authority",
        purpose="Build authority.",
        angle="Boutique hotel ROI beats mass-market in Bali.",
        hook="The cheapest line item in Bali is often the most expensive strategic mistake.",
        key_points=["Point 1", "Point 2", "Point 3"],
        cta_type="comment",
        tone="register_3",
        length_target="medium",
        engagement_objective="Developer discussion",
        fact_pack=["Verified fact"],
        source_rigor="expert",
        reference_sources=["https://a.example", "https://b.example", "https://c.example"],
    )
    decision = WorkflowBDecision(
        platform="linkedin",
        platform_lane="linkedin_b2b",
        language_mode="ru",
        funnel_role="authority",
        tone="register_3",
        cta_type="comment",
        engagement_objective="Developer discussion",
        source_rigor="expert",
        desired_reaction="Invite qualified discussion.",
        emotional_hook="Expose hidden market logic.",
    )

    draft = writer.write_workflow_b_draft(
        item=source_item,
        insight=insight,
        decision=decision,
        brief=brief,
    )

    assert draft.draft_text_ru == "Русский драфт."
    assert draft.draft_text_en == "English draft."
    assert client.calls[0]["max_tokens"] == 1400


def test_write_video_script_returns_text_from_anthropic(video_source_item) -> None:
    client = StubAnthropicClient(responses=["Hook\nPoint 1\nPoint 2\nCTA"])
    writer = AnthropicPipelineWriter(client)

    script_text = writer.write_video_script(
        item=video_source_item,
        title="Boutique Hotels Signal",
        hook="What looks cheap first is often the most expensive later.",
        body_points=["Point 1", "Point 2"],
        cta="Save this before your next review.",
    )

    assert script_text == "Hook\nPoint 1\nPoint 2\nCTA"
    assert client.calls[0]["max_tokens"] == 700


def test_write_workflow_b_draft_parses_multiline_tagged_payload(source_item) -> None:
    client = StubAnthropicClient(
        responses=[
            """
            <draft_text_ru>Первая строка.
            Вторая строка.</draft_text_ru>
            <draft_text_en>First line.
            Second line.</draft_text_en>
            """
        ]
    )
    writer = AnthropicPipelineWriter(client)
    insight = InsightCard(
        audience="developer_investor",
        platform="linkedin",
        content_theme="boutique_hotels",
        content_pillar="expertise_proof",
        narrative_type="market observation",
        priority=2,
        reuse_score=4,
        emotional_trigger="status anxiety",
        useful_lesson="Boutique hotel ROI beats mass-market in Bali.",
    )
    brief = ContentBrief(
        audience="developer_investor",
        platform="linkedin",
        platform_lane="linkedin_b2b",
        working_language="ru",
        publish_language="en",
        funnel_role="authority",
        purpose="Build authority.",
        angle="Boutique hotel ROI beats mass-market in Bali.",
        hook="The cheapest line item in Bali is often the most expensive strategic mistake.",
        key_points=["Point 1", "Point 2", "Point 3"],
        cta_type="comment",
        tone="register_3",
        length_target="medium",
        engagement_objective="Developer discussion",
        fact_pack=["Verified fact"],
        source_rigor="expert",
        reference_sources=["https://a.example", "https://b.example", "https://c.example"],
    )
    decision = WorkflowBDecision(
        platform="linkedin",
        platform_lane="linkedin_b2b",
        language_mode="ru",
        funnel_role="authority",
        tone="register_3",
        cta_type="comment",
        engagement_objective="Developer discussion",
        source_rigor="expert",
        desired_reaction="Invite qualified discussion.",
        emotional_hook="Expose hidden market logic.",
    )

    draft = writer.write_workflow_b_draft(
        item=source_item,
        insight=insight,
        decision=decision,
        brief=brief,
    )

    assert draft.draft_text_ru == "Первая строка.\n            Вторая строка."
    assert draft.draft_text_en == "First line.\n            Second line."
    assert client.calls[0]["max_tokens"] == 1400


def test_write_workflow_b_draft_normalizes_string_null_to_none(source_item) -> None:
    client = StubAnthropicClient(
        responses=[
            """{"draft_text_ru":"Русский драфт.","draft_text_en":"null"}"""
        ]
    )
    writer = AnthropicPipelineWriter(client)
    insight = InsightCard(
        audience="developer_investor",
        platform="instagram",
        content_theme="boutique_hotels",
        content_pillar="expertise_proof",
        narrative_type="market observation",
        priority=2,
        reuse_score=4,
        emotional_trigger="status anxiety",
        useful_lesson="Boutique hotel ROI beats mass-market in Bali.",
    )
    brief = ContentBrief(
        audience="developer_investor",
        platform="instagram",
        platform_lane="instagram_professional",
        working_language="ru",
        publish_language="ru",
        funnel_role="authority",
        purpose="Build authority.",
        angle="Boutique hotel ROI beats mass-market in Bali.",
        hook="The cheapest line item in Bali is often the most expensive strategic mistake.",
        key_points=["Point 1", "Point 2", "Point 3"],
        cta_type="comment",
        tone="register_3",
        length_target="medium",
        engagement_objective="Developer discussion",
        fact_pack=["Verified fact"],
        source_rigor="expert",
        reference_sources=["https://a.example", "https://b.example", "https://c.example"],
    )
    decision = WorkflowBDecision(
        platform="instagram",
        platform_lane="instagram_professional",
        language_mode="ru",
        funnel_role="authority",
        tone="register_3",
        cta_type="comment",
        engagement_objective="Developer discussion",
        source_rigor="expert",
        desired_reaction="Invite qualified discussion.",
        emotional_hook="Expose hidden market logic.",
    )

    draft = writer.write_workflow_b_draft(
        item=source_item,
        insight=insight,
        decision=decision,
        brief=brief,
    )

    assert draft.draft_text_en is None
