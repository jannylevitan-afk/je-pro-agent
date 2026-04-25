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
    "founder_journey": [
        WorkflowBDecision(
            platform="instagram",
            platform_lane="instagram_lifestyle",
            language_mode="ru",
            funnel_role="affinity",
            tone="register_7",
            cta_type="comment",
            engagement_objective="Recognition, replies, and warm DMs from women following the founder story",
            source_rigor="standard",
            desired_reaction="Reply with a personal reflection, not a purchase objection.",
            emotional_hook="Make business feel embedded in a real life, not staged around a sales pitch.",
        ),
    ],
    "expert_pain_bali": [
        WorkflowBDecision(
            platform="instagram",
            platform_lane="instagram_professional",
            language_mode="ru",
            funnel_role="authority",
            tone="register_3",
            cta_type="save",
            engagement_objective="Saves and DMs from brokers, developers, and investor-adjacent readers",
            source_rigor="expert",
            desired_reaction="Save this before reviewing a Bali deal.",
            emotional_hook="Turn recurring buyer pain into a useful professional warning.",
        ),
        WorkflowBDecision(
            platform="linkedin",
            platform_lane="linkedin_b2b",
            language_mode="ru",
            funnel_role="authority",
            tone="register_4",
            cta_type="comment",
            engagement_objective="High-signal replies from developers, investors, land owners, and partners",
            source_rigor="expert",
            desired_reaction="Start a qualified B2B conversation about the market signal.",
            emotional_hook="Show the strategic cost of ignoring Bali-specific deal friction.",
        ),
    ],
    "land_and_legal": [
        WorkflowBDecision(
            platform="instagram",
            platform_lane="instagram_professional",
            language_mode="ru",
            funnel_role="authority",
            tone="register_4",
            cta_type="save",
            engagement_objective="Saves from readers who need a pre-deal checklist",
            source_rigor="market-critical",
            desired_reaction="Save and check the legal structure before falling in love with the asset.",
            emotional_hook="Expose how the attractive offer can become the expensive mistake.",
        ),
        WorkflowBDecision(
            platform="linkedin",
            platform_lane="linkedin_b2b",
            language_mode="ru",
            funnel_role="authority",
            tone="register_4",
            cta_type="comment",
            engagement_objective="Developer, investor, and land-owner discussion",
            source_rigor="market-critical",
            desired_reaction="Invite operators to compare what they verify before a deal.",
            emotional_hook="Frame legal nuance as business risk, not paperwork.",
        ),
    ],
    "market_reports": [
        WorkflowBDecision(
            platform="instagram",
            platform_lane="instagram_professional",
            language_mode="ru",
            funnel_role="authority",
            tone="register_3",
            cta_type="save",
            engagement_objective="Saves from brokers and investors tracking market changes",
            source_rigor="market-critical",
            desired_reaction="Save the signal for the next market conversation.",
            emotional_hook="Make the market shift visible before it becomes obvious.",
        ),
        WorkflowBDecision(
            platform="linkedin",
            platform_lane="linkedin_b2b",
            language_mode="ru",
            funnel_role="authority",
            tone="register_4",
            cta_type="comment",
            engagement_objective="International B2B replies and partner conversations",
            source_rigor="market-critical",
            desired_reaction="Invite qualified disagreement or confirmation from operators.",
            emotional_hook="Turn dated market evidence into a strategic point of view.",
        ),
    ],
    "bali_travel": [
        WorkflowBDecision(
            platform="instagram",
            platform_lane="instagram_lifestyle",
            language_mode="ru",
            funnel_role="affinity",
            tone="register_2",
            cta_type="share",
            engagement_objective="Shares, saves, and emotional connection around Bali life",
            source_rigor="standard",
            desired_reaction="Share this with someone who understands the Bali pull.",
            emotional_hook="Make Bali feel like a life decision before it becomes an asset decision.",
        ),
    ],
    "global_trends": [
        WorkflowBDecision(
            platform="instagram",
            platform_lane="instagram_professional",
            language_mode="ru",
            funnel_role="authority",
            tone="register_3",
            cta_type="save",
            engagement_objective="Saves from readers watching travel, hospitality, and wellness shifts",
            source_rigor="expert",
            desired_reaction="Save the trend before applying it to Bali inventory.",
            emotional_hook="Connect global travel behavior to a local development decision.",
        ),
        WorkflowBDecision(
            platform="linkedin",
            platform_lane="linkedin_b2b",
            language_mode="ru",
            funnel_role="authority",
            tone="register_4",
            cta_type="comment",
            engagement_objective="International developer and investor discussion",
            source_rigor="expert",
            desired_reaction="Invite other operators to compare what they see in their market.",
            emotional_hook="Use global trend evidence to sharpen Bali positioning.",
        ),
    ],
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

_THEME_ALIASES = {
    "personal_life_entrepreneur": "founder_journey",
    "личная_жизнь_предпринимателя": "founder_journey",
    "expert_pain": "expert_pain_bali",
    "экспертные_боли_bali": "expert_pain_bali",
    "bali_real_estate": "expert_pain_bali",
    "legal": "land_and_legal",
    "market_report": "market_reports",
    "travel_trends": "global_trends",
}

_AUDIENCE_HOOKS: dict[str, str] = {
    "developer_investor": "Status and downside protection matter more than surface ROI talk.",
    "broker": "Signal what helps partners close cleaner deals.",
    "architect_designer": "Make design logic commercially and emotionally legible.",
    "lifestyle_expat": "Translate business into an aspirational life decision.",
    "dreamer_woman": "Keep the emotional arc intimate and vivid.",
}


def expand_workflow_b_decisions(item: SourceItem) -> list[WorkflowBDecision]:
    theme_key = _normalize_theme(item.content_theme)
    theme_decisions = _THEME_DECISIONS.get(theme_key)
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
    theme_key = _normalize_theme(item.content_theme)
    if theme_key in {"expert_pain_bali", "land_and_legal", "market_reports", "global_trends"}:
        return "market observation"
    if theme_key in {"marketing_cases", "boutique_hotels"}:
        return "market observation"
    if theme_key == "founder_journey":
        return "founder struggle"
    if theme_key == "bali_travel":
        return "invitation/community"
    if theme_key == "wellness_architecture":
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


def _normalize_theme(content_theme: str) -> str:
    normalized = content_theme.strip().lower().replace(" ", "_")
    return _THEME_ALIASES.get(normalized, normalized)
