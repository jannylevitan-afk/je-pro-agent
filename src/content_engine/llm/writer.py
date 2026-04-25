from __future__ import annotations

import json
import re
import textwrap
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
                "Keep claims grounded in the provided source and do not invent market facts. "
                "Source boundary is strict: do not use model memory about people, brands, media appearances, "
                "awards, interviews, numbers, clients, or projects unless the exact claim is present in the source, "
                "body points, or CTA provided in this request."
            ),
            user_prompt="\n".join(
                [
                    f"Title: {title}",
                    f"Audience: {item.audience_segment}",
                    f"Theme: {item.content_theme}",
                    f"Source lesson: {item.transcript_text}",
                    f"Required hook: {hook}",
                    "Start the script with the required hook exactly. Do not replace it with a generic opening.",
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
                "You are the Writer Entity inside a bilingual content engine. "
                "Follow the strict sequence: preflight context, task classification, insight card, "
                "voice/register selection, idea gate, content brief, draft generation, AI editing, and voice QA. "
                "Never write from a raw topic; write only from the insight, selected idea, and brief. "
                "Never invent facts beyond the source transcript, fact pack, and reference sources. "
                "Source boundary is strict: ignore model memory. Do not mention people, institutions, media outlets, "
                "awards, interviews, numbers, clients, projects, AILLA, HANDARA, or Clear brands unless that exact "
                "claim appears in the source transcript, fact pack, or reference sources in this request. "
                "If a claim is not directly supported, replace it with a general observation or remove it. "
                "If Jane Levitan voice is used, preserve the author voice module: facts only from dossier, "
                "no private facts, no client names, no politics, no generic AI openings, and no forbidden phrases. "
                "For LinkedIn, keep the working version in Russian and the publish version in English. "
                "Instagram lifestyle is lived, sharp, feminine, and never sentimental. "
                "Instagram professional is expert, concrete, and visual rather than report-like. "
                "LinkedIn is international B2B only: no lifestyle-for-lifestyle, no motherhood angle, no generic motivation. "
                "AILLA can appear as a cross-cutting narrative only when the provided source supports it, not as forced advertising. "
                "Run a final voice and quality QA before returning. "
                "Return either strict JSON or XML-style tags that are easy to parse. "
                "Keep the draft concise, publication-ready, and within the requested length limits."
            ),
            user_prompt="\n".join(
                [
                    "Writer Entity contract:",
                    "- Insight first, draft second.",
                    "- One post = one main thought.",
                    "- Kill generic ideas; do not include unsupported claims.",
                    "- Editing strengthens the text without replacing the author.",
                    "- Start draft_text_ru with the source-specific Hook line or its natural Russian equivalent.",
                    "- If draft_text_en is required, start it with the same source-specific hook in English.",
                    "- Do not reuse a generic opening from another source.",
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
                    f"Length constraint: {_length_constraint(decision.platform_lane)}",
                    (
                        'Return either JSON with keys "draft_text_ru" and "draft_text_en", '
                        'or exactly two blocks: <draft_text_ru>...</draft_text_ru> and '
                        '<draft_text_en>...</draft_text_en>. '
                        'For non-LinkedIn lanes, set "draft_text_en" to null or leave the tag empty. '
                        'Do not include source lists, explanations, labels, or markdown fences.'
                    ),
                ]
            ),
            max_tokens=_workflow_b_max_tokens(decision.platform_lane),
            model=self._model,
            temperature=0.45,
        )
        payload = _parse_draft_payload(raw)

        draft_text_ru = payload.get("draft_text_ru")
        draft_text_en = payload.get("draft_text_en")
        if not isinstance(draft_text_ru, str) or not draft_text_ru.strip():
            raise ValueError("Anthropic writer must return draft_text_ru")
        if draft_text_en is not None and not isinstance(draft_text_en, str):
            raise ValueError("Anthropic writer draft_text_en must be a string or null")

        return PipelineDraftText(
            draft_text_ru=draft_text_ru.strip(),
            draft_text_en=_normalize_optional_text(draft_text_en),
        )


def _parse_draft_payload(raw: str) -> dict[str, object]:
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
    except json.JSONDecodeError:
        return _parse_tagged_payload(normalized)
    if not isinstance(decoded, dict):
        raise ValueError("Anthropic writer must return a JSON object")
    return decoded


def _parse_tagged_payload(raw: str) -> dict[str, object]:
    draft_text_ru = _extract_tagged_text(raw, "draft_text_ru")
    draft_text_en = _extract_tagged_text(raw, "draft_text_en")
    if draft_text_ru is None and draft_text_en is None:
        raise ValueError("Anthropic writer response is neither valid JSON nor tagged draft payload")
    return {
        "draft_text_ru": draft_text_ru,
        "draft_text_en": draft_text_en,
    }


def _extract_tagged_text(raw: str, tag_name: str) -> str | None:
    match = re.search(
        rf"<{tag_name}>(.*?)</{tag_name}>",
        raw,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if match is None:
        return None
    value = textwrap.dedent(match.group(1)).strip()
    return value or None


def _workflow_b_max_tokens(platform_lane: str) -> int:
    if platform_lane == "linkedin_b2b":
        return 1400
    return 900


def _length_constraint(platform_lane: str) -> str:
    if platform_lane == "linkedin_b2b":
        return "RU master draft 180-260 words. EN publish draft 140-220 words."
    if platform_lane == "instagram_professional":
        return "RU caption 110-170 words."
    if platform_lane == "instagram_lifestyle":
        return "RU caption 80-130 words."
    return "Keep it concise."


def _normalize_optional_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if normalized.lower() in {"", "null", "none", "n/a"}:
        return None
    return normalized
