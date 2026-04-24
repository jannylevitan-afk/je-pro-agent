# Live Pipeline And Context Rules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the current contract-heavy content engine into a runnable end-to-end slice that applies hard-coded business rules from the architecture, routes collected items into Workflow A and Workflow B, and syncs all resulting artifacts into Notion.

**Architecture:** Keep external integrations thin and deterministic. Business rules from CD1/CD2/CD3 live in dedicated context modules, orchestration lives in a small runner layer, and Notion remains the single output surface through existing payload builders and sync helpers.

**Tech Stack:** Python 3.12, Pydantic 2, pytest, stdlib `urllib`

---

## File Map

- Create: `src/content_engine/context/__init__.py`
- Create: `src/content_engine/context/workflow_b_rules.py`
- Create: `src/content_engine/orchestration/live_pipeline.py`
- Modify: `src/content_engine/notion/payloads.py`
- Modify: `src/content_engine/notion/sync.py`
- Modify: `src/content_engine/notion/__init__.py`
- Create: `tests/context/test_workflow_b_rules.py`
- Create: `tests/notion/test_workflow_b_notion_sync.py`
- Create: `tests/orchestration/test_live_pipeline.py`

## Task 1: Hard-code Workflow B context rules

- [ ] Add a focused rules module for audience defaults, theme-to-register mapping, platform lane expansion, narrative hints, AILLA line support, and source rigor defaults.
- [ ] Cover those rules with tests before implementation.

## Task 2: Close missing Notion entities for Workflow B

- [ ] Add payload builders for `InsightCard` and `IdeaCandidate`.
- [ ] Add sync helpers for creating insights and ideas in Notion.
- [ ] Add targeted tests for payload shape and sync calls.

## Task 3: Build the end-to-end live pipeline runner

- [ ] Add a runner that accepts collected `SourceItem` records plus a Notion client and DB targets.
- [ ] Route each item through `workflow_a`, `workflow_b`, or `both`.
- [ ] For Workflow A, create source/script/filming artifacts in Notion.
- [ ] For Workflow B, create source/insight/idea/brief/draft artifacts in Notion and submit drafts for review.
- [ ] Use the new hard-coded context rules rather than leaving those decisions entirely to call-site arguments.

## Task 4: Verify the runnable slice

- [ ] Add orchestration tests proving one batch can process items into both workflows.
- [ ] Run focused tests for context, notion, and orchestration layers.
- [ ] Run the full suite and keep the tree stable.
