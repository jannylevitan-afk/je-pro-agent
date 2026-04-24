from content_engine.models.repurposing import AtomType, ContentAtom, EvergreenWindow, RepurposeTarget
from content_engine.models.workflow_b import InsightCard


_BTS_NARRATIVES = {"behind the scenes", "journey of creation", "founder struggle"}
_TACTICAL_NARRATIVES = {"professional lesson", "market observation", "authority"}

_ATOM_PLATFORM_HINTS: dict[AtomType, list[str]] = {
    "quotable_claim": ["linkedin_b2b", "instagram_professional"],
    "story_moment": ["instagram_lifestyle", "instagram_professional", "telegram"],
    "tactical_tip": ["linkedin_b2b", "instagram_professional"],
    "data_stat_callout": ["linkedin_b2b", "instagram_professional"],
    "bts_fragment": ["instagram_lifestyle", "workflow_a"],
}

_ATOM_REPURPOSE_TARGET: dict[AtomType, RepurposeTarget] = {
    "quotable_claim": "workflow_b",
    "story_moment": "workflow_b",
    "tactical_tip": "both",
    "data_stat_callout": "both",
    "bts_fragment": "workflow_a",
}


def derive_atom_types(insight: InsightCard) -> list[AtomType]:
    atom_types: list[AtomType] = []

    if insight.reuse_score >= 3:
        atom_types.append("quotable_claim")

    if insight.narrative_type in _BTS_NARRATIVES:
        atom_types.append("story_moment")
        atom_types.append("bts_fragment")
    elif insight.narrative_type in _TACTICAL_NARRATIVES:
        atom_types.append("tactical_tip")

    if insight.reuse_score >= 4:
        atom_types.append("data_stat_callout")

    # deduplicate while preserving order
    seen: set[AtomType] = set()
    unique: list[AtomType] = []
    for t in atom_types:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique


def build_content_atom(
    insight: InsightCard,
    insight_id: str,
    atom_type: AtomType,
    content: str,
    standalone: bool,
    evergreen: bool,
    evergreen_window: EvergreenWindow | None = None,
) -> ContentAtom:
    atom_index = _ATOM_PLATFORM_HINTS[atom_type]
    return ContentAtom(
        atom_id=f"atom_{insight_id}_{atom_type}",
        source_insight_id=insight_id,
        atom_type=atom_type,
        content=content,
        repurpose_target=_ATOM_REPURPOSE_TARGET[atom_type],
        standalone=standalone,
        evergreen=evergreen,
        evergreen_window=evergreen_window,
        platform_hints=list(atom_index),
    )


def filter_publishable_atoms(atoms: list[ContentAtom]) -> list[ContentAtom]:
    """Keep only atoms that can stand alone without source context."""
    return [a for a in atoms if a.standalone]
