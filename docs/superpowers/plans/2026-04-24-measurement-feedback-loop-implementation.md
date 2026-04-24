# Measurement And Feedback Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the decision-first analytics layer so content performance can be translated into reusable metrics, performance tiers, and feedback signals that guide future source selection and content packaging.

**Architecture:** This block stays adapter-free and codifies the measurement model from the architecture: engagement/authority/conversion metrics, attribution-ready content performance records, lowercase event naming, and signals that flow back into Research Agent priorities.

**Tech Stack:** Python 3.12, Pydantic 2, pytest

---

## File Map For Block 6

- Create: `src/content_engine/models/analytics.py`
- Create: `src/content_engine/services/analytics.py`
- Modify: `src/content_engine/notion/schema_defs.py`
- Create: `tests/models/test_analytics_models.py`
- Create: `tests/services/test_analytics_feedback.py`
- Create: `tests/notion/test_block6_schema_extensions.py`

### Task 1: Encode analytics and feedback contracts

**Files:**
- Create: `src/content_engine/models/analytics.py`
- Create: `tests/models/test_analytics_models.py`

- [ ] **Step 1: Write failing tests for `ContentPerformanceRecord`, `DecisionMetrics`, `FeedbackSignal`, and `TrackingEvent`**
- [ ] **Step 2: Run the tests to verify they fail**
- [ ] **Step 3: Implement minimal strict models with attribution and event-name validation**
- [ ] **Step 4: Re-run the model tests**

### Task 2: Build decision-metric and feedback helpers

**Files:**
- Create: `src/content_engine/services/analytics.py`
- Create: `tests/services/test_analytics_feedback.py`

- [ ] **Step 1: Write failing tests for**
  - `calculate_decision_metrics`
  - `classify_performance_tier`
  - `build_feedback_signal`
  - `validate_tracking_event_name`
- [ ] **Step 2: Run the tests to verify they fail**
- [ ] **Step 3: Implement minimal helpers**
- [ ] **Step 4: Re-run the service tests**

### Task 3: Extend machine-readable Notion schemas for analytics

**Files:**
- Modify: `src/content_engine/notion/schema_defs.py`
- Create: `tests/notion/test_block6_schema_extensions.py`

- [ ] **Step 1: Write failing schema tests**
  Cover:
  - `CONTENT_PERFORMANCE_SCHEMA`
  - `RESEARCH_FEEDBACK_SIGNAL_SCHEMA`

- [ ] **Step 2: Run the tests to verify they fail**
- [ ] **Step 3: Implement schema extensions**
- [ ] **Step 4: Re-run the schema tests**

### Task 4: Verify Block 6 against previous blocks

- [ ] **Step 1: Run the analytics suite**
- [ ] **Step 2: Run the full suite for Blocks 1-6**
- [ ] **Step 3: Create a git checkpoint after fresh passing verification**
