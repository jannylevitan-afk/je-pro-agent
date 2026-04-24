from content_engine.models.repurposing import ContentAtom
from content_engine.models.workflow_b import InsightCard
from content_engine.services.repurposing import (
    build_content_atom,
    derive_atom_types,
    filter_publishable_atoms,
)


def make_insight(narrative_type: str = "market_observation", reuse_score: int = 4) -> InsightCard:
    return InsightCard(
        audience="developer_investor",
        platform="instagram",
        content_theme="boutique_hotels",
        content_pillar="expertise_proof",
        narrative_type=narrative_type,
        priority=2,
        reuse_score=reuse_score,
        emotional_trigger="status anxiety",
        useful_lesson="Boutique hotel ROI beats mass-market by 3x in Bali.",
    )


def test_derive_atom_types_includes_quotable_for_high_reuse_score() -> None:
    insight = make_insight(reuse_score=3)
    types = derive_atom_types(insight)

    assert "quotable_claim" in types


def test_derive_atom_types_excludes_quotable_for_low_reuse_score() -> None:
    insight = make_insight(reuse_score=2)
    types = derive_atom_types(insight)

    assert "quotable_claim" not in types


def test_derive_atom_types_adds_story_and_bts_for_bts_narrative() -> None:
    insight = make_insight(narrative_type="behind the scenes", reuse_score=4)
    types = derive_atom_types(insight)

    assert "story_moment" in types
    assert "bts_fragment" in types


def test_derive_atom_types_adds_tactical_tip_for_professional_lesson() -> None:
    insight = make_insight(narrative_type="professional lesson", reuse_score=4)
    types = derive_atom_types(insight)

    assert "tactical_tip" in types
    assert "bts_fragment" not in types


def test_derive_atom_types_includes_data_callout_when_reuse_score_ge_4() -> None:
    insight = make_insight(reuse_score=4)
    types = derive_atom_types(insight)

    assert "data_stat_callout" in types


def test_derive_atom_types_returns_no_duplicates() -> None:
    insight = make_insight(narrative_type="behind the scenes", reuse_score=5)
    types = derive_atom_types(insight)

    assert len(types) == len(set(types))


def test_build_content_atom_maps_repurpose_target_from_type() -> None:
    insight = make_insight()
    atom = build_content_atom(
        insight=insight,
        insight_id="ins_001",
        atom_type="bts_fragment",
        content="We found a structural flaw during the site visit — before any contract was signed.",
        standalone=True,
        evergreen=False,
    )

    assert atom.repurpose_target == "workflow_a"
    assert "instagram_lifestyle" in atom.platform_hints
    assert atom.atom_id == "atom_ins_001_bts_fragment"


def test_build_content_atom_tactical_tip_routes_to_both() -> None:
    insight = make_insight()
    atom = build_content_atom(
        insight=insight,
        insight_id="ins_002",
        atom_type="tactical_tip",
        content="Check legal risk, design quality, and management track record before signing.",
        standalone=True,
        evergreen=True,
        evergreen_window="3_months",
    )

    assert atom.repurpose_target == "both"
    assert atom.evergreen_window == "3_months"


def test_filter_publishable_atoms_drops_non_standalone() -> None:
    insight = make_insight()
    standalone = build_content_atom(
        insight=insight,
        insight_id="ins_001",
        atom_type="quotable_claim",
        content="Boutique hotel ROI beats mass-market by 3x.",
        standalone=True,
        evergreen=True,
        evergreen_window="6_months",
    )
    dependent = build_content_atom(
        insight=insight,
        insight_id="ins_001",
        atom_type="story_moment",
        content="As I walked through the site...",
        standalone=False,
        evergreen=False,
    )

    result = filter_publishable_atoms([standalone, dependent])

    assert len(result) == 1
    assert result[0].atom_type == "quotable_claim"
