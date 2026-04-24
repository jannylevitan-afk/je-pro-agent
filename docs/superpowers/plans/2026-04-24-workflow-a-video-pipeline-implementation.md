# Workflow A Video Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the deterministic core of Workflow A so video-source items can turn into hooks, scripts, filming cards, and publish-ready calendar entries before the human filming/publishing steps.

**Architecture:** This block encodes the pure business logic of the video pipeline without touching publishing APIs. It turns Research Agent input into ranked hook candidates, a chosen script package, filming queue artifacts, and machine-readable Notion schemas for the human production loop.

**Tech Stack:** Python 3.12, Pydantic 2, pytest

---

## File Map For Block 5

- Create: `src/content_engine/models/workflow_a.py`
- Create: `src/content_engine/services/workflow_a.py`
- Modify: `src/content_engine/notion/schema_defs.py`
- Create: `tests/models/test_workflow_a_models.py`
- Create: `tests/services/test_workflow_a_pipeline.py`
- Create: `tests/notion/test_block5_schema_extensions.py`

### Task 1: Encode Workflow A pipeline contracts

**Files:**
- Create: `src/content_engine/models/workflow_a.py`
- Create: `tests/models/test_workflow_a_models.py`

- [ ] **Step 1: Write failing tests for `VideoHook`, `VideoScript`, `FilmingCard`, and `VideoPublishItem`**
- [ ] **Step 2: Run the tests to verify they fail**
- [ ] **Step 3: Implement minimal strict models with platform/status validation**
- [ ] **Step 4: Re-run the model tests**

### Task 2: Build deterministic Workflow A service helpers

**Files:**
- Create: `src/content_engine/services/workflow_a.py`
- Create: `tests/services/test_workflow_a_pipeline.py`

- [ ] **Step 1: Write failing tests for**
  - `develop_video_hooks`
  - `select_best_hook`
  - `build_video_script`
  - `build_filming_card`
  - `build_video_publish_item`
- [ ] **Step 2: Run the tests to verify they fail**
- [ ] **Step 3: Implement minimal helpers**
- [ ] **Step 4: Re-run the service tests**

### Task 3: Extend machine-readable Notion schemas for Workflow A

**Files:**
- Modify: `src/content_engine/notion/schema_defs.py`
- Create: `tests/notion/test_block5_schema_extensions.py`

- [ ] **Step 1: Write failing schema tests**
  Cover:
  - `SCRIPTS_QUEUE_SCHEMA`
  - `FILMING_CARDS_SCHEMA`
  - `VIDEO_PUBLISH_CALENDAR_SCHEMA`
  - `VIDEO_PERFORMANCE_SCHEMA`

- [ ] **Step 2: Run the tests to verify they fail**
- [ ] **Step 3: Implement schema extensions**
- [ ] **Step 4: Re-run the schema tests**

### Task 4: Verify Block 5 against previous blocks

- [ ] **Step 1: Run the Workflow A suite**
- [ ] **Step 2: Run the full suite for Blocks 1-5**
- [ ] **Step 3: Create a git checkpoint after fresh passing verification**
