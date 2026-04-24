import pytest
from pydantic import ValidationError

from content_engine.models.repurposing import ContentAtom


def make_atom(**overrides) -> dict:
    base = {
        "atom_id": "atom_ins_001_quotable_claim",
        "source_insight_id": "ins_001",
        "atom_type": "quotable_claim",
        "content": "Boutique hotel ROI beats mass-market by 3x in Bali.",
        "repurpose_target": "workflow_b",
        "standalone": True,
        "evergreen": True,
        "evergreen_window": "6_months",
        "platform_hints": ["linkedin_b2b", "instagram_professional"],
    }
    base.update(overrides)
    return base


def test_content_atom_accepts_valid_evergreen() -> None:
    atom = ContentAtom(**make_atom())

    assert atom.evergreen is True
    assert atom.evergreen_window == "6_months"
    assert atom.standalone is True


def test_content_atom_rejects_evergreen_without_window() -> None:
    with pytest.raises(ValidationError, match="evergreen_window"):
        ContentAtom(**make_atom(evergreen=True, evergreen_window=None))


def test_content_atom_rejects_window_on_non_evergreen() -> None:
    with pytest.raises(ValidationError, match="non-evergreen"):
        ContentAtom(**make_atom(evergreen=False, evergreen_window="3_months"))


def test_content_atom_non_evergreen_has_no_window() -> None:
    atom = ContentAtom(**make_atom(evergreen=False, evergreen_window=None))

    assert atom.evergreen is False
    assert atom.evergreen_window is None


def test_content_atom_rejects_unknown_atom_type() -> None:
    with pytest.raises(ValidationError):
        ContentAtom(**make_atom(atom_type="random_type"))
