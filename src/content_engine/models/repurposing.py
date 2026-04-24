from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


AtomType = Literal[
    "quotable_claim",
    "story_moment",
    "tactical_tip",
    "data_stat_callout",
    "bts_fragment",
]

RepurposeTarget = Literal["workflow_a", "workflow_b", "both"]

EvergreenWindow = Literal["3_months", "6_months"]


class ContentAtom(BaseModel):
    model_config = ConfigDict(extra="forbid")

    atom_id: str
    source_insight_id: str
    atom_type: AtomType
    content: str
    repurpose_target: RepurposeTarget
    standalone: bool
    evergreen: bool
    evergreen_window: EvergreenWindow | None = None
    platform_hints: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_evergreen_window(self) -> "ContentAtom":
        if self.evergreen and self.evergreen_window is None:
            raise ValueError("evergreen atoms require an evergreen_window")
        if not self.evergreen and self.evergreen_window is not None:
            raise ValueError("non-evergreen atoms must not set evergreen_window")
        return self
