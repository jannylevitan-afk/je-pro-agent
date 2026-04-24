from __future__ import annotations

from dataclasses import dataclass

from content_engine.models.source_item import SourceItem
from content_engine.models.workflow_b import FunnelRole, Platform, PlatformLane, SourceRigor


@dataclass(frozen=True, slots=True)
class WorkflowBDecision:
    platform: Platform
    platform_lane: PlatformLane
    language_mode: str
    funnel_role: FunnelRole
    tone: str
    cta_type: str
    engagement_objective: str
    source_rigor: SourceRigor
    desired_reaction: str
    emotional_hook: str


_THEME_DECISIONS: dict[str, list[WorkflowBDecision]] = {
    "boutique_hotels": [
        WorkflowBDecision(
            platform="instagram",
            platform_lane="instagram_professional",
            language_mode="ru",
            funnel_role="authority",
            tone="register_3",
            cta_type="save",
            engagement_objective="Saves from broker and developer audience",
            source_rigor="expert",
            desired_reaction="Save this for the next deal review.",
            emotional_hook="Show where premium positioning beats cheap inventory logic.",
        ),
        WorkflowBDecision(
            platform="linkedin",
            platform_lane="linkedin_b2b",
            language_mode="ru",
            funnel_role="authority",
            tone="register_3",
            cta_type="comment",
            engagement_objective="Developer and investor replies",
            source_rigor="expert",
            desired_reaction="Invite qualified market discussion.",
            emotional_hook="Expose the hidden cost logic behind hospitality yield.",
        ),
    ],
    "marketing_cases": [
        WorkflowBDecision(
            platform="instagram",
            platform_lane="instagram_professional",
            language_mode="ru",
            funnel_role="authority",
            tone="register_3",
            cta_type="save",
            engagement_objective="Saves from operators and partners",
            source_rigor="expert",
            desired_reaction="Save the framework for later.",
            emotional_hook="Translate noisy marketing into commercial signal.",
        ),
        WorkflowBDecision(
            platform="linkedin",
            platform_lane="linkedin_b2b",
            language_mode="ru",
            funnel_role="authority",
            tone="register_3",
            cta_type="comment",
            engagement_objective="Partnership and founder conversations",
            source_rigor="market-critical",
            desired_reaction="Spark high-signal B2B discussion.",
            emotional_hook="Call out market red flags before they waste budget.",
        ),
    ],
    "wellness_architecture": [
        WorkflowBDecision(
            platform="instagram",
            platform_lane="instagram_lifestyle",
            language_mode="ru",
            funnel_role="affinity",
            tone="register_2",
            cta_type="share",
            engagement_objective="Emotional resonance and shares",
            source_rigor="standard",
            desired_reaction="Feel the project vision, not just the asset.",
            emotional_hook="Turn the project into a lived emotional scene.",
        ),
        WorkflowBDecision(
            platform="instagram",
            platform_lane="instagram_professional",
            language_mode="ru",
            funnel_role="authority",
            tone="register_6",
            cta_type="save",
            engagement_objective="Saves from architects and developers",
            source_rigor="expert",
            desired_reaction="Save the case logic for the next planning session.",
            emotional_hook="Frame AILLA as product thinking, not decor.",
        ),
        WorkflowBDecision(
            platform="linkedin",
            platform_lane="linkedin_b2b",
            language_mode="ru",
            funnel_role="authority",
            tone="register_6",
            cta_type="comment",
            engagement_objective="Investor and strategic partner replies",
            source_rigor="expert",
            desired_reaction="Invite market positioning discussion.",
            emotional_hook="Position AILLA as an experience-development case.",
        ),
    ],
}

_AUDIENCE_HOOKS: dict[str, str] = {
    "developer_investor": "Status and downside protection matter more than surface ROI talk.",
    "broker": "Signal what helps partners close cleaner deals.",
    "architect_designer": "Make design logic commercially and emotionally legible.",
    "lifestyle_expat": "Translate business into an aspirational life decision.",
    "dreamer_woman": "Keep the emotional arc intimate and vivid.",
}


def expand_workflow_b_decisions(item: SourceItem) -> list[WorkflowBDecision]:
    theme_decisions = _THEME_DECISIONS.get(item.content_theme)
    if theme_decisions is None:
        theme_decisions = _THEME_DECISIONS["boutique_hotels"]

    audience_hook = _AUDIENCE_HOOKS.get(item.audience_segment, _AUDIENCE_HOOKS["developer_investor"])
    adjusted: list[WorkflowBDecision] = []
    for decision in theme_decisions:
        adjusted.append(
            WorkflowBDecision(
                platform=decision.platform,
                platform_lane=decision.platform_lane,
                language_mode=decision.language_mode,
                funnel_role=decision.funnel_role,
                tone=decision.tone,
                cta_type=decision.cta_type,
                engagement_objective=decision.engagement_objective,
                source_rigor=decision.source_rigor,
                desired_reaction=decision.desired_reaction,
                emotional_hook=f"{decision.emotional_hook} {audience_hook}",
            )
        )
    return adjusted


def infer_narrative_type(item: SourceItem) -> str:
    if item.media_urls:
        return "behind the scenes"
    if item.content_theme in {"marketing_cases", "boutique_hotels"}:
        return "market observation"
    if item.content_theme == "wellness_architecture":
        return "journey of creation"
    return "professional lesson"


def infer_useful_lesson(item: SourceItem) -> str:
    text = item.transcript_text.strip()
    if not text:
        return "No source lesson captured."
    first_sentence = text.split(".")[0].strip()
    if not first_sentence:
        return text
    if first_sentence.endswith("."):
        return first_sentence
    return f"{first_sentence}."
