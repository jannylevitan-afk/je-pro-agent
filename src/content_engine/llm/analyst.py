from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

from content_engine.models.source_item import SourceItem


class AnthropicTextClient(Protocol):
    def generate_text(
        self,
        *,
        system_prompt: str | None,
        user_prompt: str,
        max_tokens: int,
        model: str | None = None,
        temperature: float | None = None,
    ) -> str:
        ...


@dataclass(frozen=True, slots=True)
class InsightExtractionResult:
    useful_lesson: str
    emotional_trigger: str
    narrative_type: str
    reuse_score: int
    topic: str = ""
    angle: str = ""
    audience_fit: str = ""
    customer_job: str = ""
    pain_point: str = ""
    trigger_event: str = ""
    desired_outcome: str = ""
    behavioral_trigger: str = ""
    confidence_score: float = 0.7


_SYSTEM_PROMPT = (
    "You are an Analyst Entity inside a bilingual content engine for Jane Levitan — "
    "founder of Clear Real Estate and Clear Visionary on Bali.\n"
    "\n"
    "Your job is to extract structured insights from raw source material. "
    "You read a transcript or source text, understand the audience segment, "
    "and extract the single most valuable insight that makes a post worth writing.\n"
    "\n"
    "Core audience emotional triggers:\n"
    "- developer_investor: status anxiety, market positioning, ROI logic, downside protection\n"
    "- broker: deal urgency, competitive edge, partner opportunity, closing intelligence\n"
    "- architect_designer: craft pride, design logic, premium materials, project vision\n"
    "- lifestyle_expat: identity pull, life transformation, aspirational living, belonging\n"
    "- dreamer_woman: future-self desire, family plus ambition, emotional resonance\n"
    "\n"
    "Narrative types:\n"
    "- market_observation: analysis of market trends for professional content\n"
    "- journey_of_creation: behind-the-scenes of building a project\n"
    "- behind_the_scenes: real-time BTS fragments, strongest when visual material exists\n"
    "- professional_lesson: expert knowledge, tactical market tips\n"
    "\n"
    "Rules:\n"
    "- Phase 1 is already handled by source normalization; do not rewrite the source.\n"
    "- Phase 2 must extract the topic, angle, emotional trigger, and audience fit.\n"
    "- Working language is Russian: return all narrative text values in Russian, even when the source is English.\n"
    "- Keep enum labels exactly as requested, but write topic, angle, useful_lesson, emotional_trigger, audience_fit, JTBD fields, and outcomes in Russian.\n"
    "- Adapt customer-research logic: identify JTBD/customer_job, pain_point, trigger_event, desired_outcome, and source language.\n"
    "- Adapt ethical marketing psychology only as analysis labels: loss_aversion, status_signal, identity_pull, curiosity_gap, social_proof, or direct_benefit.\n"
    "- The useful_lesson must be 1-2 sentences, specific, and actionable or revelatory.\n"
    "- The emotional_trigger must match the stated audience segment precisely.\n"
    "- Reuse score 1-5: how many different angles this source could generate.\n"
    "- Confidence score 0.0-1.0: how strongly the source supports the extracted insight.\n"
    "- Never invent facts not present in the source transcript.\n"
    "- Return only valid JSON without markdown fences or explanation."
)


class AnthropicPipelineAnalyst:
    def __init__(
        self,
        client: AnthropicTextClient,
        *,
        model: str | None = None,
    ) -> None:
        self._client = client
        self._model = model

    def extract_insight(self, item: SourceItem) -> InsightExtractionResult:
        raw = self._client.generate_text(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=_build_extraction_prompt(item),
            max_tokens=1600,
            model=self._model,
            temperature=0.3,
        )
        return _parse_extraction_result(raw)


def _build_extraction_prompt(item: SourceItem) -> str:
    has_media = bool(item.media_urls)
    engagement_summary = ", ".join(
        f"{k}: {v}" for k, v in item.engagement_signals.items()
    )
    return "\n".join([
        f"Source transcript: {item.transcript_text}",
        f"Audience segment: {item.audience_segment}",
        f"Content theme: {item.content_theme}",
        f"Has media: {has_media}",
        f"Engagement signals: {engagement_summary or 'none'}",
        "",
        "Return topic, angle, useful_lesson, emotional_trigger, audience_fit, customer_job, pain_point, trigger_event, and desired_outcome in Russian.",
        "Extract the insight. Return JSON with these exact keys:",
        '{',
        '  "topic": "specific topic extracted from the source",',
        '  "angle": "main angle for content strategy",',
        '  "useful_lesson": "1-2 sentences, the core insight from this source",',
        '  "emotional_trigger": "the specific emotion this triggers for the stated audience",',
        '  "audience_fit": "why this matters to the stated audience",',
        '  "narrative_type": "market_observation | journey_of_creation | behind_the_scenes | professional_lesson",',
        '  "reuse_score": 3,',
        '  "customer_job": "what the audience is trying to decide, achieve, or avoid",',
        '  "pain_point": "the concrete pain, fear, or friction in the source",',
        '  "trigger_event": "what situation makes this source relevant now",',
        '  "desired_outcome": "what the audience wants after understanding this",',
        '  "behavioral_trigger": "loss_aversion | status_signal | identity_pull | curiosity_gap | social_proof | direct_benefit",',
        '  "confidence_score": 0.8',
        '}',
    ])


def _parse_extraction_result(raw: str) -> InsightExtractionResult:
    normalized = raw.strip()
    if normalized.startswith("```"):
        lines = normalized.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        normalized = "\n".join(lines).strip()

    try:
        decoded = json.loads(normalized)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Analyst LLM did not return valid JSON: {raw!r}"
        ) from error

    if not isinstance(decoded, dict):
        raise ValueError("Analyst LLM response must be a JSON object")

    required = {"useful_lesson", "emotional_trigger", "narrative_type", "reuse_score"}
    missing = required - decoded.keys()
    if missing:
        raise ValueError(f"Analyst LLM response missing fields: {missing}")

    useful_lesson = decoded.get("useful_lesson")
    if not isinstance(useful_lesson, str) or not useful_lesson.strip():
        raise ValueError("Analyst LLM useful_lesson must be a non-empty string")

    emotional_trigger = decoded.get("emotional_trigger")
    if not isinstance(emotional_trigger, str) or not emotional_trigger.strip():
        raise ValueError("Analyst LLM emotional_trigger must be a non-empty string")

    narrative_type = decoded.get("narrative_type")
    if not isinstance(narrative_type, str) or not narrative_type.strip():
        raise ValueError("Analyst LLM narrative_type must be a non-empty string")

    raw_score = decoded.get("reuse_score")
    if not isinstance(raw_score, (int, float)):
        raise ValueError("Analyst LLM reuse_score must be a number")
    score = int(raw_score)
    if not 1 <= score <= 5:
        raise ValueError(f"Analyst LLM reuse_score must be 1-5, got {score}")

    return InsightExtractionResult(
        useful_lesson=useful_lesson.strip(),
        emotional_trigger=emotional_trigger.strip(),
        narrative_type=narrative_type.strip(),
        reuse_score=score,
        topic=_optional_string(decoded.get("topic")),
        angle=_optional_string(decoded.get("angle")),
        audience_fit=_optional_string(decoded.get("audience_fit")),
        customer_job=_optional_string(decoded.get("customer_job")),
        pain_point=_optional_string(decoded.get("pain_point")),
        trigger_event=_optional_string(decoded.get("trigger_event")),
        desired_outcome=_optional_string(decoded.get("desired_outcome")),
        behavioral_trigger=_optional_string(decoded.get("behavioral_trigger")),
        confidence_score=_confidence_score(decoded.get("confidence_score")),
    )


def _optional_string(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _confidence_score(value: object) -> float:
    if isinstance(value, (int, float)):
        return max(0.0, min(1.0, float(value)))
    return 0.7
