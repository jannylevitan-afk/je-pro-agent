# Approval Gate And Bilingual Publish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the deterministic core of Block 4 so Drafts can move through review safely, LinkedIn keeps `ru master` + `en publish version`, and future n8n/Notion automation has stable contracts to execute against.

**Architecture:** This block stays adapter-free. It encodes the approval state machine, rewrite/re-brief/delete decisions, calendar export artifacts, and orchestration events as Python contracts plus pure services. Real Notion buttons, n8n polling, Telegram notifications, and Claude rewrite calls can later plug into these contracts without changing business rules.

**Tech Stack:** Python 3.12, Pydantic 2, pytest

---

## File Map For Block 4

- Create: `src/content_engine/models/approval.py`
- Create: `src/content_engine/services/approval.py`
- Modify: `src/content_engine/notion/schema_defs.py`
- Create: `tests/models/test_approval_models.py`
- Create: `tests/services/test_approval_flow.py`
- Create: `tests/notion/test_block4_schema_extensions.py`

### Task 1: Encode approval and publish contracts

**Files:**
- Create: `src/content_engine/models/approval.py`
- Create: `tests/models/test_approval_models.py`

- [ ] **Step 1: Write failing tests for approval models**
  Cover:
  - `DraftRecord` keeps review metadata, versioning, and bilingual draft fields
  - `ReviewAction` allows `approved`, `needs_rewrite`, `re_brief`, `deleted`
  - `ReviewAction` requires notes for `needs_rewrite`
  - `CalendarItem` keeps `final_text_ru` and optional `final_text_en`
  - LinkedIn publish artifacts require `publish_language = "en"` and `final_text_en`

- [ ] **Step 2: Run the tests to verify they fail**

- [ ] **Step 3: Implement minimal strict models**
  Add:
  - approval enums / literals
  - `DraftRecord`
  - `ReviewAction`
  - `CalendarItem`
  - `OrchestrationEvent`

- [ ] **Step 4: Re-run the model tests**

### Task 2: Build the approval state machine services

**Files:**
- Create: `src/content_engine/services/approval.py`
- Create: `tests/services/test_approval_flow.py`

- [ ] **Step 1: Write failing tests for pure services**
  Cover:
  - `submit_for_review` moves a draft into `awaiting_review` + `pending`
  - `apply_review_action` handles `approved`, `needs_rewrite`, `re_brief`, `deleted`
  - rewrite creates next version with carried-over RU master and reset decision
  - approve creates `CalendarItem` with bilingual LinkedIn output
  - each transition emits stable orchestration events (`draft_reviewed`, `rewrite_requested`, `calendar_item_scheduled`, etc.)

- [ ] **Step 2: Run the tests to verify they fail**

- [ ] **Step 3: Implement minimal service helpers**
  Add:
  - `submit_for_review`
  - `apply_review_action`
  - `build_calendar_item`
  - `build_orchestration_events`

- [ ] **Step 4: Re-run the service tests**

### Task 3: Extend machine-readable Notion schemas for Block 4

**Files:**
- Modify: `src/content_engine/notion/schema_defs.py`
- Create: `tests/notion/test_block4_schema_extensions.py`

- [ ] **Step 1: Write failing schema tests**
  Cover:
  - `DRAFTS_DB_SCHEMA` includes `Platform lane`, `Language mode`, `Parent draft`, `Review requested at`
  - `CONTENT_CALENDAR_SCHEMA` includes `Source draft`, `Approval decided at`
  - `ORCHESTRATION_EVENT_SCHEMA` exists with event, status, payload references

- [ ] **Step 2: Run the tests to verify they fail**

- [ ] **Step 3: Implement schema extensions**

- [ ] **Step 4: Re-run the schema tests**

### Task 4: Verify Block 4 against previous blocks

**Files:**
- Test: `tests/models/test_approval_models.py`
- Test: `tests/services/test_approval_flow.py`
- Test: `tests/notion/test_block4_schema_extensions.py`

- [ ] **Step 1: Run the Block 4 suite**

- [ ] **Step 2: Run the full suite for Blocks 1-4**

- [ ] **Step 3: Create a git checkpoint after fresh passing verification**
  Suggested message:

```bash
git add docs/superpowers/plans/2026-04-24-approval-gate-bilingual-publish-implementation.md src/content_engine/models/approval.py src/content_engine/services/approval.py src/content_engine/notion/schema_defs.py tests/models/test_approval_models.py tests/services/test_approval_flow.py tests/notion/test_block4_schema_extensions.py
git commit -m "feat: add approval gate and bilingual publish core"
```
