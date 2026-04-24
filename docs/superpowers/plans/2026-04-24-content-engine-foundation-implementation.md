# Content Engine Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first working slice of the Content Engine by turning the architecture into executable contracts: core data models, config loaders, language rules, and Notion schema definitions.

**Architecture:** Start with a Python contract layer that encodes the system rules before any scraping, prompting, or automation is built. This block creates typed models for collected items and Workflow B artifacts, sample config files for Seed Config and Fact Dossier, and machine-readable Notion schema definitions that future n8n and generation layers can trust.

**Tech Stack:** Python 3.12, Pydantic 2, PyYAML, pytest

---

## Block Breakdown

1. **Block 1 — Foundation contracts, configs, and Notion schemas**
   This plan. Produces a testable core package with typed models and schema definitions.
2. **Block 2 — Research Agent ingestion and discovery**
   Implements source adapters, discovery queue scoring, and monitoring run metadata.
3. **Block 3 — Workflow B generation pipeline**
   Builds source normalization, insight extraction, idea/brief/draft orchestration, and factual guardrails.
4. **Block 4 — Approval gate and LinkedIn bilingual publish layer**
   Implements review-state transitions, RU master + EN publish version handling, and Notion/n8n approval flows.
5. **Block 5 — Workflow A video pipeline**
   Builds hook generation, script queue, filming cards, and publish calendar support.
6. **Block 6 — Measurement and feedback loop**
   Connects content performance, attribution, and signals back into Research Agent priorities.

## File Map For Block 1

- Create: `pyproject.toml`
- Create: `src/content_engine/__init__.py`
- Create: `src/content_engine/models/__init__.py`
- Create: `src/content_engine/config/__init__.py`
- Create: `src/content_engine/notion/__init__.py`
- Create: `src/content_engine/models/source_item.py`
- Create: `src/content_engine/models/workflow_b.py`
- Create: `src/content_engine/config/seed_config.py`
- Create: `src/content_engine/config/fact_dossier.py`
- Create: `src/content_engine/notion/schema_defs.py`
- Create: `examples/seed_config.sample.yaml`
- Create: `examples/fact_dossier.sample.yaml`
- Create: `tests/smoke/test_package_import.py`
- Create: `tests/models/test_source_item.py`
- Create: `tests/models/test_workflow_b_language_policy.py`
- Create: `tests/config/test_seed_config.py`
- Create: `tests/config/test_fact_dossier.py`
- Create: `tests/notion/test_schema_defs.py`

### Task 1: Bootstrap the Python contract package

**Files:**
- Create: `pyproject.toml`
- Create: `src/content_engine/__init__.py`
- Create: `src/content_engine/models/__init__.py`
- Create: `src/content_engine/config/__init__.py`
- Create: `src/content_engine/notion/__init__.py`
- Create: `tests/smoke/test_package_import.py`

- [ ] **Step 1: Write the failing package import test**

```python
# tests/smoke/test_package_import.py
from content_engine import __version__


def test_package_exposes_version() -> None:
    assert __version__ == "0.1.0"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m pytest tests/smoke/test_package_import.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'content_engine'`

- [ ] **Step 3: Write the minimal package bootstrap**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "content-engine"
version = "0.1.0"
description = "Contracts and workflow primitives for the Content Engine project."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
  "pydantic>=2.7,<3",
  "PyYAML>=6.0.1,<7",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2,<9",
]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```python
# src/content_engine/__init__.py
__all__ = ["__version__"]

__version__ = "0.1.0"
```

```python
# src/content_engine/models/__init__.py
__all__: list[str] = []
```

```python
# src/content_engine/config/__init__.py
__all__: list[str] = []
```

```python
# src/content_engine/notion/__init__.py
__all__: list[str] = []
```

- [ ] **Step 4: Install dev dependencies**

Run: `python3 -m pip install -e ".[dev]"`
Expected: editable package install succeeds and `pytest` is available

- [ ] **Step 5: Re-run the import test**

Run: `python3 -m pytest tests/smoke/test_package_import.py -q`
Expected: PASS

- [ ] **Step 6: Commit the bootstrap**

```bash
git add pyproject.toml src/content_engine/__init__.py src/content_engine/models/__init__.py src/content_engine/config/__init__.py src/content_engine/notion/__init__.py tests/smoke/test_package_import.py
git commit -m "chore: bootstrap content engine package"
```

### Task 2: Encode the canonical collected item contract

**Files:**
- Create: `src/content_engine/models/source_item.py`
- Create: `tests/models/test_source_item.py`

- [ ] **Step 1: Write the failing source item contract tests**

```python
# tests/models/test_source_item.py
from content_engine.models.source_item import SourceItem


def test_source_item_requires_core_identity_fields() -> None:
    item = SourceItem(
        item_id="itm_001",
        source_type="instagram_post",
        source_name="@test_handle",
        source_url="https://example.com/post/1",
        external_item_id="123",
        collected_at="2026-04-24T08:00:00Z",
        published_at="2026-04-23T08:00:00Z",
        content_hash="hash_123",
        dedupe_key="instagram:123",
        audience_segment="developer_investor",
        content_theme="boutique_hotels",
        raw_payload={"caption": "hello"},
        transcript_text="hello",
        media_urls=["https://example.com/image.jpg"],
        engagement_signals={"likes": 10, "comments": 2, "views": 100},
        routing_decision="workflow_b",
        routing_reason="market observation + textual depth",
        routing_confidence=0.82,
        processing_state="collected",
    )

    assert item.routing_decision == "workflow_b"
    assert item.dedupe_key == "instagram:123"


def test_source_item_rejects_invalid_routing_decision() -> None:
    try:
        SourceItem(
            item_id="itm_001",
            source_type="instagram_post",
            source_name="@test_handle",
            source_url="https://example.com/post/1",
            external_item_id="123",
            collected_at="2026-04-24T08:00:00Z",
            published_at="2026-04-23T08:00:00Z",
            content_hash="hash_123",
            dedupe_key="instagram:123",
            audience_segment="developer_investor",
            content_theme="boutique_hotels",
            raw_payload={"caption": "hello"},
            transcript_text="hello",
            media_urls=["https://example.com/image.jpg"],
            engagement_signals={"likes": 10, "comments": 2, "views": 100},
            routing_decision="wrong_value",
            routing_reason="market observation + textual depth",
            routing_confidence=0.82,
            processing_state="collected",
        )
    except ValueError:
        assert True
    else:
        raise AssertionError("Expected invalid routing decision to fail")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest tests/models/test_source_item.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'content_engine.models.source_item'`

- [ ] **Step 3: Implement the canonical model**

```python
# src/content_engine/models/source_item.py
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


RoutingDecision = Literal["workflow_a", "workflow_b", "both", "drop"]
ProcessingState = Literal["collected", "normalized", "partial", "failed"]


class SourceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str
    source_type: str
    source_name: str
    source_url: str
    external_item_id: str
    collected_at: str
    published_at: str
    content_hash: str
    dedupe_key: str
    audience_segment: str
    content_theme: str
    raw_payload: dict[str, Any]
    transcript_text: str
    media_urls: list[str]
    engagement_signals: dict[str, int]
    routing_decision: RoutingDecision
    routing_reason: str
    routing_confidence: float = Field(ge=0.0, le=1.0)
    processing_state: ProcessingState
```

- [ ] **Step 4: Re-run the source item tests**

Run: `python3 -m pytest tests/models/test_source_item.py -q`
Expected: PASS

- [ ] **Step 5: Commit the collected item contract**

```bash
git add src/content_engine/models/source_item.py tests/models/test_source_item.py
git commit -m "feat: add canonical collected item contract"
```

### Task 3: Encode Workflow B language and bilingual LinkedIn rules

**Files:**
- Create: `src/content_engine/models/workflow_b.py`
- Create: `tests/models/test_workflow_b_language_policy.py`

- [ ] **Step 1: Write the failing Workflow B tests**

```python
# tests/models/test_workflow_b_language_policy.py
from content_engine.models.workflow_b import DraftBundle


def test_linkedin_requires_ru_master_and_en_publish_version() -> None:
    draft = DraftBundle(
        title="AILLA positioning",
        platform="linkedin",
        platform_lane="linkedin_b2b",
        working_language="ru",
        publish_language="en",
        audience_portrait="developer_investor",
        voice_register="register_3",
        funnel_role="authority",
        draft_text_ru="Русский мастер-текст",
        draft_text_en="English publish version",
    )

    assert draft.publish_language == "en"
    assert draft.draft_text_ru
    assert draft.draft_text_en


def test_instagram_defaults_to_russian_publish_language() -> None:
    draft = DraftBundle(
        title="Morning on site",
        platform="instagram",
        platform_lane="instagram_lifestyle",
        working_language="ru",
        publish_language="ru",
        audience_portrait="woman_dreamer",
        voice_register="register_7",
        funnel_role="affinity",
        draft_text_ru="Русский мастер-текст",
        draft_text_en=None,
    )

    assert draft.publish_language == "ru"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest tests/models/test_workflow_b_language_policy.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'content_engine.models.workflow_b'`

- [ ] **Step 3: Implement the Workflow B models**

```python
# src/content_engine/models/workflow_b.py
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator


Platform = Literal["instagram", "linkedin", "telegram"]
PlatformLane = Literal["instagram_lifestyle", "instagram_professional", "linkedin_b2b"]
Language = Literal["ru", "en"]
FunnelRole = Literal["attention", "affinity", "authority", "conversion"]


class DraftBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    platform: Platform
    platform_lane: PlatformLane
    working_language: Language
    publish_language: Language
    audience_portrait: str
    voice_register: str
    funnel_role: FunnelRole
    draft_text_ru: str
    draft_text_en: str | None = None

    @model_validator(mode="after")
    def validate_language_policy(self) -> "DraftBundle":
        if self.platform_lane == "linkedin_b2b":
            if self.working_language != "ru":
                raise ValueError("LinkedIn working language must stay Russian in Notion")
            if self.publish_language != "en":
                raise ValueError("LinkedIn publish language must be English")
            if not self.draft_text_en:
                raise ValueError("LinkedIn requires an English publish version")
        return self
```

- [ ] **Step 4: Re-run the Workflow B tests**

Run: `python3 -m pytest tests/models/test_workflow_b_language_policy.py -q`
Expected: PASS

- [ ] **Step 5: Commit the language policy models**

```bash
git add src/content_engine/models/workflow_b.py tests/models/test_workflow_b_language_policy.py
git commit -m "feat: add workflow b language policy models"
```

### Task 4: Add Seed Config and Fact Dossier loaders

**Files:**
- Create: `src/content_engine/config/seed_config.py`
- Create: `src/content_engine/config/fact_dossier.py`
- Create: `examples/seed_config.sample.yaml`
- Create: `examples/fact_dossier.sample.yaml`
- Create: `tests/config/test_seed_config.py`
- Create: `tests/config/test_fact_dossier.py`

- [ ] **Step 1: Write the failing config loader tests**

```python
# tests/config/test_seed_config.py
from pathlib import Path

from content_engine.config.seed_config import load_seed_config


def test_seed_config_loads_audience_segments() -> None:
    data = load_seed_config(Path("examples/seed_config.sample.yaml"))
    assert "audience_segments" in data
    assert data["audience_segments"][0]["name"] == "developer_investor"
```

```python
# tests/config/test_fact_dossier.py
from pathlib import Path

from content_engine.config.fact_dossier import load_fact_dossier


def test_fact_dossier_loads_records() -> None:
    data = load_fact_dossier(Path("examples/fact_dossier.sample.yaml"))
    assert data["facts"][0]["verification_status"] == "verified_public"
```

- [ ] **Step 2: Run the config tests to verify they fail**

Run: `python3 -m pytest tests/config/test_seed_config.py tests/config/test_fact_dossier.py -q`
Expected: FAIL with import errors for missing config modules

- [ ] **Step 3: Create the sample YAML files**

```yaml
# examples/seed_config.sample.yaml
audience_segments:
  - name: developer_investor
    route_to: workflow_b
    seed_profiles:
      - platform: instagram
        handle: artur_mkhitaryan_
content_theme_sources:
  - name: boutique_hotels
    route_to: both
```

```yaml
# examples/fact_dossier.sample.yaml
facts:
  - claim: "Clear Real Estate uses the phrase Zero bullshit."
    fact_type: brand
    verification_status: verified_public
    evidence: "public brand materials"
    freshness_window: evergreen
    allowed_usage: public
```

- [ ] **Step 4: Implement the config loaders**

```python
# src/content_engine/config/seed_config.py
from pathlib import Path
from typing import Any

import yaml


def load_seed_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)
```

```python
# src/content_engine/config/fact_dossier.py
from pathlib import Path
from typing import Any

import yaml


def load_fact_dossier(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)
```

- [ ] **Step 5: Re-run the config tests**

Run: `python3 -m pytest tests/config/test_seed_config.py tests/config/test_fact_dossier.py -q`
Expected: PASS

- [ ] **Step 6: Commit the config layer**

```bash
git add src/content_engine/config/ examples/ tests/config/
git commit -m "feat: add seed config and fact dossier loaders"
```

### Task 5: Define the machine-readable Notion schemas

**Files:**
- Create: `src/content_engine/notion/schema_defs.py`
- Create: `tests/notion/test_schema_defs.py`

- [ ] **Step 1: Write the failing Notion schema tests**

```python
# tests/notion/test_schema_defs.py
from content_engine.notion.schema_defs import CONTENT_CALENDAR_SCHEMA, DRAFTS_DB_SCHEMA


def test_drafts_schema_contains_bilingual_linkedin_fields() -> None:
    assert "Draft text RU" in DRAFTS_DB_SCHEMA
    assert "Draft text EN" in DRAFTS_DB_SCHEMA
    assert "Working language" in DRAFTS_DB_SCHEMA
    assert "Publish language" in DRAFTS_DB_SCHEMA


def test_content_calendar_contains_publish_fields() -> None:
    assert "Final text RU" in CONTENT_CALENDAR_SCHEMA
    assert "Final text EN" in CONTENT_CALENDAR_SCHEMA
```

- [ ] **Step 2: Run the Notion schema tests to verify they fail**

Run: `python3 -m pytest tests/notion/test_schema_defs.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'content_engine.notion.schema_defs'`

- [ ] **Step 3: Implement the schema definitions**

```python
# src/content_engine/notion/schema_defs.py
DRAFTS_DB_SCHEMA = {
    "Title": "title",
    "Draft text RU": "rich_text",
    "Draft text EN": "rich_text",
    "Platform": "select",
    "Audience portrait": "select",
    "Voice register": "select",
    "Version": "number",
    "Working language": "select",
    "Publish language": "select",
    "Workflow stage": "select",
    "Review decision": "select",
    "Review Notes": "rich_text",
    "AI edited": "checkbox",
    "7-point test passed": "checkbox",
    "Factual safety": "select",
    "Linked brief": "relation",
    "Linked calendar": "relation",
    "Archived": "checkbox",
}

CONTENT_CALENDAR_SCHEMA = {
    "Platform": "select",
    "Platform lane": "select",
    "Language mode": "select",
    "Working language": "select",
    "Publish language": "select",
    "Audience portrait": "select",
    "Voice register used": "select",
    "Pillar": "select",
    "Funnel role": "select",
    "Hook": "rich_text",
    "Final text RU": "rich_text",
    "Final text EN": "rich_text",
    "Publish date target": "date",
    "Approval status": "select",
    "Repurpose status": "select",
}
```

- [ ] **Step 4: Re-run the Notion schema tests**

Run: `python3 -m pytest tests/notion/test_schema_defs.py -q`
Expected: PASS

- [ ] **Step 5: Commit the Notion schema definitions**

```bash
git add src/content_engine/notion/schema_defs.py tests/notion/test_schema_defs.py
git commit -m "feat: add notion schema definitions"
```

### Task 6: Verify the whole foundation block

**Files:**
- Test: `tests/smoke/test_package_import.py`
- Test: `tests/models/test_source_item.py`
- Test: `tests/models/test_workflow_b_language_policy.py`
- Test: `tests/config/test_seed_config.py`
- Test: `tests/config/test_fact_dossier.py`
- Test: `tests/notion/test_schema_defs.py`

- [ ] **Step 1: Run the full Block 1 test suite**

Run: `python3 -m pytest tests/smoke/test_package_import.py tests/models/test_source_item.py tests/models/test_workflow_b_language_policy.py tests/config/test_seed_config.py tests/config/test_fact_dossier.py tests/notion/test_schema_defs.py -q`
Expected: PASS

- [ ] **Step 2: Inspect the working tree**

Run: `git status --short`
Expected: either clean output or only the files intentionally created in this block before the final commit

- [ ] **Step 3: Create the block completion commit**

```bash
git add pyproject.toml src/ examples/ tests/
git commit -m "feat: implement content engine foundation contracts"
```

## Self-Review Notes

- This plan intentionally covers only **Block 1** because the architecture spans multiple independent subsystems.
- Block 1 gives later work a stable foundation: data contracts, config loaders, bilingual LinkedIn rules, and Notion schema definitions.
- No placeholder tasks remain; every task names exact files, commands, and expected outputs.
- The first follow-up implementation plan after this block should be **Research Agent ingestion and discovery**, because that is the next dependency for both Workflow A and Workflow B.
