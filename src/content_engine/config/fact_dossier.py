from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class FactRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim: str
    fact_type: str
    verification_status: str
    evidence: str
    freshness_window: str
    allowed_usage: str


class FactDossier(BaseModel):
    model_config = ConfigDict(extra="forbid")

    facts: list[FactRecord] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_facts(self) -> "FactDossier":
        if not self.facts:
            raise ValueError("facts must contain at least one record")
        return self


def load_fact_dossier(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return FactDossier.model_validate(data).model_dump()
