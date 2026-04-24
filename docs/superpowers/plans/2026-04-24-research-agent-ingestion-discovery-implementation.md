# Research Agent Ingestion and Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the local, testable core of Research Agent Block 2: discovery scoring, monitoring run metadata, canonical ingestion helpers, and routing primitives.

**Architecture:** This block does not implement live platform scraping yet. Instead, it creates the deterministic primitives that real connectors will call later: score discovery candidates from seed criteria, track monitoring run health and retry state, generate stable dedupe keys for collected items, and route normalized signal summaries into Workflow A, Workflow B, Both, or Drop.

**Tech Stack:** Python 3.12, Pydantic 2, pytest, hashlib

---

## File Map For Block 2

- Create: `src/content_engine/models/discovery.py`
- Create: `src/content_engine/models/monitoring.py`
- Create: `src/content_engine/services/__init__.py`
- Create: `src/content_engine/services/discovery.py`
- Create: `src/content_engine/services/ingestion.py`
- Create: `src/content_engine/services/routing.py`
- Modify: `src/content_engine/notion/schema_defs.py`
- Create: `tests/models/test_discovery_candidate.py`
- Create: `tests/models/test_monitoring_run.py`
- Create: `tests/services/test_discovery_scoring.py`
- Create: `tests/services/test_ingestion_helpers.py`
- Create: `tests/services/test_routing.py`

### Task 1: Add discovery and monitoring domain models

**Files:**
- Create: `src/content_engine/models/discovery.py`
- Create: `src/content_engine/models/monitoring.py`
- Create: `tests/models/test_discovery_candidate.py`
- Create: `tests/models/test_monitoring_run.py`

- [ ] **Step 1: Write failing model tests**

Write tests for:
- a `DiscoveryCandidate` with `handle`, `platform`, `segment`, `score`, `why_relevant`, `approved`, `added_to_monitoring`
- a `MonitoringRun` with `run_id`, `connector`, `source_name`, `fetched_count`, `failed_count`, `retry_count`, `staleness_hours`, `run_status`
- validation that `run_status` only allows `success`, `partial`, `failed`, `stale`

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest tests/models/test_discovery_candidate.py tests/models/test_monitoring_run.py -q`
Expected: FAIL with missing imports

- [ ] **Step 3: Implement the minimal models**

Add Pydantic models for `DiscoveryCandidate` and `MonitoringRun` with strict fields and typed literals.

- [ ] **Step 4: Re-run the model tests**

Run: `python3 -m pytest tests/models/test_discovery_candidate.py tests/models/test_monitoring_run.py -q`
Expected: PASS

### Task 2: Add deterministic discovery scoring

**Files:**
- Create: `src/content_engine/services/discovery.py`
- Create: `tests/services/test_discovery_scoring.py`

- [ ] **Step 1: Write failing discovery scoring tests**

Cover:
- +3 bio keyword match
- +2 geo match
- +2 content signal match
- +1 follower range match
- -2 for clearly irrelevant content
- queue eligibility when score >= 6

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest tests/services/test_discovery_scoring.py -q`
Expected: FAIL with missing service import

- [ ] **Step 3: Implement the minimal scoring service**

Implement:
- `score_candidate(profile, criteria) -> DiscoveryScoreResult`
- `eligible_for_queue(score_result) -> bool`

- [ ] **Step 4: Re-run the discovery tests**

Run: `python3 -m pytest tests/services/test_discovery_scoring.py -q`
Expected: PASS

### Task 3: Add ingestion helper for stable dedupe key generation

**Files:**
- Create: `src/content_engine/services/ingestion.py`
- Create: `tests/services/test_ingestion_helpers.py`

- [ ] **Step 1: Write failing ingestion helper tests**

Cover:
- uses `platform:external_item_id` when external id exists
- falls back to hash of `source_url + published_at + content_hash` when external id is missing
- produces the same key for identical input

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest tests/services/test_ingestion_helpers.py -q`
Expected: FAIL with missing helper import

- [ ] **Step 3: Implement the dedupe helper**

Implement:
- `build_dedupe_key(platform, external_item_id, source_url, published_at, content_hash) -> str`

- [ ] **Step 4: Re-run the ingestion helper tests**

Run: `python3 -m pytest tests/services/test_ingestion_helpers.py -q`
Expected: PASS

### Task 4: Add routing primitives for normalized signal summaries

**Files:**
- Create: `src/content_engine/services/routing.py`
- Create: `tests/services/test_routing.py`

- [ ] **Step 1: Write failing routing tests**

Cover:
- routes video-first trend signals to `workflow_a`
- routes textual market/founder insights to `workflow_b`
- routes mixed high-value hooks to `both`
- routes low-relevance signals to `drop`

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest tests/services/test_routing.py -q`
Expected: FAIL with missing routing import

- [ ] **Step 3: Implement the minimal routing helper**

Implement:
- `route_signal(signal_summary) -> str`

Use explicit boolean flags / normalized summary fields rather than magic prompt text.

- [ ] **Step 4: Re-run the routing tests**

Run: `python3 -m pytest tests/services/test_routing.py -q`
Expected: PASS

### Task 5: Extend Notion schema definitions for Discovery Queue and monitoring

**Files:**
- Modify: `src/content_engine/notion/schema_defs.py`
- Create: `tests/services/test_block2_schema_extensions.py`

- [ ] **Step 1: Write failing schema extension tests**

Cover:
- `DISCOVERY_QUEUE_SCHEMA` includes `Handle`, `Platform`, `Segment`, `Score`, `Why relevant`, `Approved`, `Added to monitoring`
- `MONITORING_RUN_SCHEMA` includes run metadata and `Run status`

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest tests/services/test_block2_schema_extensions.py -q`
Expected: FAIL because the schema constants do not exist yet

- [ ] **Step 3: Implement the schema extensions**

Add `DISCOVERY_QUEUE_SCHEMA` and `MONITORING_RUN_SCHEMA` to `schema_defs.py`.

- [ ] **Step 4: Re-run the schema extension tests**

Run: `python3 -m pytest tests/services/test_block2_schema_extensions.py -q`
Expected: PASS

### Task 6: Verify the full Block 2 core

**Files:**
- Test: `tests/models/test_discovery_candidate.py`
- Test: `tests/models/test_monitoring_run.py`
- Test: `tests/services/test_discovery_scoring.py`
- Test: `tests/services/test_ingestion_helpers.py`
- Test: `tests/services/test_routing.py`
- Test: `tests/services/test_block2_schema_extensions.py`

- [ ] **Step 1: Run the full Block 2 suite**

Run: `python3 -m pytest tests/models/test_discovery_candidate.py tests/models/test_monitoring_run.py tests/services/test_discovery_scoring.py tests/services/test_ingestion_helpers.py tests/services/test_routing.py tests/services/test_block2_schema_extensions.py -q`
Expected: PASS

- [ ] **Step 2: Run Block 1 + Block 2 together**

Run: `python3 -m pytest tests/smoke/test_package_import.py tests/models/test_source_item.py tests/models/test_workflow_b_language_policy.py tests/config/test_seed_config.py tests/config/test_fact_dossier.py tests/notion/test_schema_defs.py tests/models/test_discovery_candidate.py tests/models/test_monitoring_run.py tests/services/test_discovery_scoring.py tests/services/test_ingestion_helpers.py tests/services/test_routing.py tests/services/test_block2_schema_extensions.py -q`
Expected: PASS

- [ ] **Step 3: Commit the Block 2 core**

```bash
git add src/content_engine/models/ src/content_engine/services/ src/content_engine/notion/schema_defs.py tests/models/ tests/services/ docs/superpowers/plans/2026-04-24-research-agent-ingestion-discovery-implementation.md
git commit -m "feat: implement research agent ingestion and discovery core"
```
