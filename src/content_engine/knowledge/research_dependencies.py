from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from content_engine.models.source_item import SourceItem


WorkflowName = Literal["workflow_a", "workflow_b"]


@dataclass(frozen=True, slots=True)
class ResearchDependencyProfile:
    workflow: WorkflowName
    route: str
    audience_segment: str
    content_theme: str
    audience_context: str
    content_pillars: list[str]
    narrative_types: list[str]
    suggested_registers: list[str]
    collect_fields: list[str]
    evidence_required: list[str]
    workflow_intake: list[str]
    writer_context: list[str]


_AUDIENCE_CONTEXT: dict[str, str] = {
    "developer_investor": "Developer/investor: cares about yield, downside protection, structure, proof, and market timing.",
    "broker": "Broker: needs clean deal logic, buyer objections, trust signals, and angles that help explain value.",
    "architect_designer": "Architect/designer: looks for design logic, taste, material decisions, project process, and creative authority.",
    "lifestyle_expat": "Lifestyle expat: responds to place, identity, community, atmosphere, and aspirational but concrete life choices.",
    "dreamer_woman": "Dreamer woman: responds to intimate founder journey, family/business tension, aesthetic life design, and future-self desire.",
}


_THEME_PROFILES: dict[str, dict[str, Any]] = {
    "founder_journey": {
        "route": "workflow_b",
        "content_pillars": ["lifestyle", "journey", "human struggle"],
        "narrative_types": ["founder struggle", "journey of creation", "aesthetic reflection"],
        "suggested_registers": ["register_7", "register_8", "register_9"],
        "collect_fields": [
            "personal scene",
            "family/business tension",
            "founder decision",
            "identity shift",
            "emotional payoff",
        ],
    },
    "expert_pain_bali": {
        "route": "workflow_b",
        "content_pillars": ["expertise", "proof"],
        "narrative_types": ["authority", "market observation", "professional lesson"],
        "suggested_registers": ["register_3", "register_4", "register_6"],
        "collect_fields": [
            "market pain",
            "legal risk",
            "deal structure",
            "professional lesson",
            "proof point",
        ],
    },
    "land_and_legal": {
        "route": "workflow_b",
        "content_pillars": ["expertise", "proof"],
        "narrative_types": ["authority", "professional lesson", "market observation"],
        "suggested_registers": ["register_3", "register_4", "register_6"],
        "collect_fields": ["legal nuance", "land status", "buyer risk", "operator warning", "proof point"],
    },
    "market_reports": {
        "route": "workflow_b",
        "content_pillars": ["expertise", "proof"],
        "narrative_types": ["authority", "market observation"],
        "suggested_registers": ["register_3", "register_4"],
        "collect_fields": ["market data", "date", "benchmark", "source citation", "freshness signal"],
    },
    "bali_travel": {
        "route": "both",
        "content_pillars": ["lifestyle", "invitation"],
        "narrative_types": ["aesthetic reflection", "invitation/community"],
        "suggested_registers": ["register_1", "register_2", "register_7"],
        "collect_fields": ["location", "visual hook", "atmosphere", "community signal", "repeatable format"],
    },
    "global_trends": {
        "route": "both",
        "content_pillars": ["expertise", "market signals"],
        "narrative_types": ["market observation", "authority"],
        "suggested_registers": ["register_3", "register_4"],
        "collect_fields": ["trend", "date", "industry signal", "benchmark", "source citation"],
    },
    "wellness_architecture": {
        "route": "workflow_b",
        "content_pillars": ["expertise", "lifestyle"],
        "narrative_types": ["authority", "aesthetic reflection", "journey of creation"],
        "suggested_registers": ["register_2", "register_6"],
        "collect_fields": ["design logic", "spa/wellness feature", "luxury cue", "human feeling", "project lesson"],
    },
    "boutique_hotels": {
        "route": "both",
        "content_pillars": ["expertise", "proof"],
        "narrative_types": ["authority", "market observation"],
        "suggested_registers": ["register_3", "register_6"],
        "collect_fields": ["ADR/yield signal", "positioning", "hospitality case", "visual proof", "operator lesson"],
    },
    "marketing_cases": {
        "route": "workflow_b",
        "content_pillars": ["expertise", "proof"],
        "narrative_types": ["professional lesson", "market observation"],
        "suggested_registers": ["register_3", "register_8"],
        "collect_fields": ["marketing mechanic", "case evidence", "mistake", "framework", "commercial lesson"],
    },
}

_THEME_ALIASES = {
    "personal_life_entrepreneur": "founder_journey",
    "личная_жизнь_предпринимателя": "founder_journey",
    "экспертные_боли_bali": "expert_pain_bali",
    "expert_pain": "expert_pain_bali",
    "bali_real_estate": "expert_pain_bali",
}

_BASE_EVIDENCE = ["source URL", "timestamp", "raw excerpt", "confidence score"]

_WORKFLOW_A_FIELDS = ["video refs", "caption/transcript", "first 3 seconds", "hook pattern", "visual device", "CTA"]
_WORKFLOW_B_FIELDS = ["source note", "topic", "angle", "emotional trigger", "proof", "reusable angle"]

_WORKFLOW_A_INTAKE = ["video reference", "hook pattern", "tension/promise", "visual device", "shooting cue"]
_WORKFLOW_B_INTAKE = ["structured source note", "audience pain and trigger", "narrative type", "fact boundary", "reuse score"]


def resolve_research_dependencies(item: SourceItem, *, workflow: WorkflowName) -> ResearchDependencyProfile:
    theme_key = _normalize_theme(item.content_theme)
    theme_profile = _THEME_PROFILES.get(theme_key, _THEME_PROFILES["boutique_hotels"])
    workflow_fields = _WORKFLOW_A_FIELDS if workflow == "workflow_a" else _WORKFLOW_B_FIELDS
    workflow_intake = _WORKFLOW_A_INTAKE if workflow == "workflow_a" else _WORKFLOW_B_INTAKE

    return ResearchDependencyProfile(
        workflow=workflow,
        route=str(theme_profile["route"]),
        audience_segment=item.audience_segment,
        content_theme=theme_key,
        audience_context=_AUDIENCE_CONTEXT.get(item.audience_segment, _AUDIENCE_CONTEXT["developer_investor"]),
        content_pillars=list(theme_profile["content_pillars"]),
        narrative_types=list(theme_profile["narrative_types"]),
        suggested_registers=list(theme_profile["suggested_registers"]),
        collect_fields=[*list(theme_profile["collect_fields"]), *workflow_fields],
        evidence_required=list(_BASE_EVIDENCE),
        workflow_intake=list(workflow_intake),
        writer_context=[
            "Use the source note as the factual boundary.",
            "Use the audience context before choosing hook, tone, and CTA.",
            "If a claim is not in evidence or verified facts, write it as an observation or omit it.",
        ],
    )


def _normalize_theme(content_theme: str) -> str:
    normalized = content_theme.strip().lower().replace(" ", "_")
    return _THEME_ALIASES.get(normalized, normalized)
