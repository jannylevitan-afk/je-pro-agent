from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

from content_engine.context.workflow_b_rules import WorkflowBDecision
from content_engine.models.source_item import SourceItem
from content_engine.models.workflow_b import ContentBrief, InsightCard


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
class PipelineDraftText:
    draft_text_ru: str
    draft_text_en: str | None = None


class AnthropicPipelineWriter:
    def __init__(
        self,
        client: AnthropicTextClient,
        *,
        model: str | None = None,
    ) -> None:
        self._client = client
        self._model = model

    def write_video_script(
        self,
        *,
        item: SourceItem,
        title: str,
        hook: str,
        body_points: list[str],
        cta: str,
    ) -> str:
        return self._client.generate_text(
            system_prompt=(
                "You write concise, high-retention short-form video scripts for a premium content engine. "
                "Keep claims grounded in the provided source and do not invent market facts."
            ),
            user_prompt="\n".join(
                [
                    f"Title: {title}",
                    f"Audience: {item.audience_segment}",
                    f"Theme: {item.content_theme}",
                    f"Source lesson: {item.transcript_text}",
                    f"Required hook: {hook}",
                    "Body points:",
                    *[f"- {point}" for point in body_points],
                    f"CTA: {cta}",
                    "Return only the final script text, ready for the Notion Scripts database.",
                ]
            ),
            max_tokens=700,
            model=self._model,
            temperature=0.5,
        ).strip()

    def write_workflow_b_draft(
        self,
        *,
        item: SourceItem,
        insight: InsightCard,
        decision: WorkflowBDecision,
        brief: ContentBrief,
    ) -> PipelineDraftText:
        raw = self._client.generate_text(
            system_prompt=(
                "You are the writer inside a bilingual content engine. "
                "Output valid JSON only. "
                "Never invent facts beyond the source transcript, fact pack, and reference sources. "
                "For LinkedIn, keep the working version in Russian and the publish version in English."
            ),
            user_prompt="\n".join(
                [
                    f"Platform lane: {decision.platform_lane}",
                    f"Audience portrait: {insight.audience}",
                    f"Emotional hook: {decision.emotional_hook}",
                    f"Desired reaction: {decision.desired_reaction}",
                    f"Tone register: {decision.tone}",
                    f"Purpose: {brief.purpose}",
                    f"Hook line: {brief.hook}",
                    f"Angle: {brief.angle}",
                    "Key points:",
                    *[f"- {point}" for point in brief.key_points],
                    "Fact pack:",
                    *[f"- {fact}" for fact in brief.fact_pack],
                    "Reference sources:",
                    *[f"- {source}" for source in brief.reference_sources],
                    f"Source transcript: {item.transcript_text}",
                    (
                        'Return JSON with keys "draft_text_ru" and "draft_text_en". '
                        'For non-LinkedIn lanes, set "draft_text_en" to null.'
                    ),
                ]
            ),
            max_tokens=900,
            model=self._model,
            temperature=0.45,
        )
        payload = _parse_json_object(raw)

        draft_text_ru = payload.get("draft_text_ru")
        draft_text_en = payload.get("draft_text_en")
        if not isinstance(draft_text_ru, str) or not draft_text_ru.strip():
            raise ValueError("Anthropic writer must return draft_text_ru")
        if draft_text_en is not None and not isinstance(draft_text_en, str):
            raise ValueError("Anthropic writer draft_text_en must be a string or null")

        return PipelineDraftText(
            draft_text_ru=draft_text_ru.strip(),
            draft_text_en=draft_text_en.strip() if isinstance(draft_text_en, str) else None,
        )


def _parse_json_object(raw: str) -> dict[str, object]:
    normalized = raw.strip()
    if normalized.startswith("```"):
        lines = normalized.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        normalized = "\n".join(lines).strip()

    decoded = json.loads(normalized)
    if not isinstance(decoded, dict):
        raise ValueError("Anthropic writer must return a JSON object")
    return decoded
