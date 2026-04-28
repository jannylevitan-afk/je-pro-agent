import pytest

from content_engine.llm.analyst import AnthropicPipelineAnalyst, InsightExtractionResult


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
        self.calls.append({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "max_tokens": max_tokens,
            "model": model,
            "temperature": temperature,
        })
        return self._responses.pop(0)


_VALID_JSON = (
    '{"useful_lesson": "Boutique hotel ROI beats mass-market when structure and operations align.", '
    '"emotional_trigger": "status anxiety around deal quality", '
    '"narrative_type": "market_observation", '
    '"reuse_score": 4, '
    '"topic": "boutique hotel strategy", '
    '"angle": "operator discipline turns design into an asset strategy", '
    '"audience_fit": "developer_investor needs downside protection", '
    '"customer_job": "decide whether a hospitality asset is worth trusting", '
    '"pain_point": "beautiful projects hide weak operating logic", '
    '"trigger_event": "reviewing a new Bali hospitality deal", '
    '"desired_outcome": "avoid buying a polished but weak asset", '
    '"behavioral_trigger": "loss_aversion", '
    '"confidence_score": 0.86}'
)


def test_extract_insight_parses_json_response(source_item) -> None:
    client = StubAnthropicClient(responses=[_VALID_JSON])
    analyst = AnthropicPipelineAnalyst(client)

    result = analyst.extract_insight(source_item)

    assert isinstance(result, InsightExtractionResult)
    assert result.useful_lesson == "Boutique hotel ROI beats mass-market when structure and operations align."
    assert result.emotional_trigger == "status anxiety around deal quality"
    assert result.narrative_type == "market_observation"
    assert result.reuse_score == 4
    assert result.topic == "boutique hotel strategy"
    assert result.angle == "operator discipline turns design into an asset strategy"
    assert result.audience_fit == "developer_investor needs downside protection"
    assert result.customer_job == "decide whether a hospitality asset is worth trusting"
    assert result.pain_point == "beautiful projects hide weak operating logic"
    assert result.trigger_event == "reviewing a new Bali hospitality deal"
    assert result.desired_outcome == "avoid buying a polished but weak asset"
    assert result.behavioral_trigger == "loss_aversion"
    assert result.confidence_score == 0.86


def test_extract_insight_strips_markdown_fences(source_item) -> None:
    fenced = f"```json\n{_VALID_JSON}\n```"
    client = StubAnthropicClient(responses=[fenced])
    analyst = AnthropicPipelineAnalyst(client)

    result = analyst.extract_insight(source_item)

    assert result.reuse_score == 4


def test_extract_insight_sends_transcript_in_prompt(source_item) -> None:
    client = StubAnthropicClient(responses=[_VALID_JSON])
    analyst = AnthropicPipelineAnalyst(client)

    analyst.extract_insight(source_item)

    assert source_item.transcript_text in str(client.calls[0]["user_prompt"])
    assert source_item.audience_segment in str(client.calls[0]["user_prompt"])
    assert "topic" in str(client.calls[0]["user_prompt"])
    assert "audience_fit" in str(client.calls[0]["user_prompt"])
    assert "customer_job" in str(client.calls[0]["user_prompt"])
    assert "pain_point" in str(client.calls[0]["user_prompt"])
    assert "behavioral_trigger" in str(client.calls[0]["user_prompt"])


def test_extract_insight_requests_russian_working_language(source_item) -> None:
    client = StubAnthropicClient(responses=[_VALID_JSON])
    analyst = AnthropicPipelineAnalyst(client)

    analyst.extract_insight(source_item)

    assert "Russian" in str(client.calls[0]["system_prompt"])
    assert "all narrative text values in Russian" in str(client.calls[0]["system_prompt"])
    assert "Return topic, angle, useful_lesson, emotional_trigger" in str(client.calls[0]["user_prompt"])


def test_extract_insight_uses_low_temperature(source_item) -> None:
    client = StubAnthropicClient(responses=[_VALID_JSON])
    analyst = AnthropicPipelineAnalyst(client)

    analyst.extract_insight(source_item)

    assert client.calls[0]["temperature"] == 0.3


def test_extract_insight_allows_enough_tokens_for_russian_json(source_item) -> None:
    client = StubAnthropicClient(responses=[_VALID_JSON])
    analyst = AnthropicPipelineAnalyst(client)

    analyst.extract_insight(source_item)

    assert client.calls[0]["max_tokens"] >= 1400


def test_extract_insight_raises_on_invalid_json(source_item) -> None:
    client = StubAnthropicClient(responses=["not json at all"])
    analyst = AnthropicPipelineAnalyst(client)

    with pytest.raises(ValueError, match="valid JSON"):
        analyst.extract_insight(source_item)


def test_extract_insight_raises_on_missing_fields(source_item) -> None:
    client = StubAnthropicClient(responses=['{"useful_lesson": "Only lesson, missing rest"}'])
    analyst = AnthropicPipelineAnalyst(client)

    with pytest.raises(ValueError, match="missing fields"):
        analyst.extract_insight(source_item)


def test_extract_insight_raises_on_out_of_range_reuse_score(source_item) -> None:
    bad = (
        '{"useful_lesson": "Lesson.", "emotional_trigger": "trigger", '
        '"narrative_type": "market_observation", "reuse_score": 9}'
    )
    client = StubAnthropicClient(responses=[bad])
    analyst = AnthropicPipelineAnalyst(client)

    with pytest.raises(ValueError, match="reuse_score"):
        analyst.extract_insight(source_item)


def test_extract_insight_accepts_float_reuse_score(source_item) -> None:
    payload = (
        '{"useful_lesson": "Lesson.", "emotional_trigger": "trigger", '
        '"narrative_type": "market_observation", "reuse_score": 3.0}'
    )
    client = StubAnthropicClient(responses=[payload])
    analyst = AnthropicPipelineAnalyst(client)

    result = analyst.extract_insight(source_item)

    assert result.reuse_score == 3
