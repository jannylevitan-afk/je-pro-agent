# Workflow B Generation Primitives Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the deterministic core of Workflow B so the future LLM layer has stable inputs and outputs: source normalization, insight cards, idea gating, and content brief contracts.

**Architecture:** This block intentionally stops before live LLM prompting. It encodes the shapes and validation rules for Workflow B artifacts and implements the non-LLM business logic that the architecture already defines: metadata preservation, source-theme acceleration, platform lane rules, source-rigor rules, and idea gating.

**Tech Stack:** Python 3.12, Pydantic 2, pytest

---

## File Map For Block 3

- Modify: `src/content_engine/models/workflow_b.py`
- Create: `src/content_engine/services/workflow_b.py`
- Create: `tests/models/test_workflow_b_pipeline_models.py`
- Create: `tests/services/test_workflow_b_pipeline.py`

### Task 1: Add Workflow B pipeline models

**Files:**
- Modify: `src/content_engine/models/workflow_b.py`
- Create: `tests/models/test_workflow_b_pipeline_models.py`

- [ ] **Step 1: Write failing tests for `SourceNote`, `InsightCard`, `IdeaCandidate`, and `ContentBrief`**
- [ ] **Step 2: Run the tests to verify they fail**
- [ ] **Step 3: Implement the minimal pipeline models with strict fields**
- [ ] **Step 4: Re-run the tests**

### Task 2: Add deterministic Workflow B service helpers

**Files:**
- Create: `src/content_engine/services/workflow_b.py`
- Create: `tests/services/test_workflow_b_pipeline.py`

- [ ] **Step 1: Write failing tests for**
  - `normalize_source_item`
  - `build_insight_card`
  - `gate_idea_candidate`
  - `build_content_brief`
- [ ] **Step 2: Run the tests to verify they fail**
- [ ] **Step 3: Implement the minimal helpers**
- [ ] **Step 4: Re-run the tests**

### Task 3: Verify Block 3 with previous blocks

**Files:**
- Test: `tests/models/test_workflow_b_pipeline_models.py`
- Test: `tests/services/test_workflow_b_pipeline.py`

- [ ] **Step 1: Run the Block 3 suite**
- [ ] **Step 2: Run the full Block 1 + 2 + 3 suite**
