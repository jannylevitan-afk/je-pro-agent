---
name: insight-extraction-skill
description: Use when raw text or text-heavy signals need to become structured insight cards for Workflow B.
---

# Insight Extraction Skill

## Overview

Turn raw text into a structured insight card for the Content Farm.

## Extract

- topic
- audience
- emotional trigger
- proof
- reusable angle
- narrative type
- useful lesson

## Rules

- Keep the original source note intact
- The insight must stay grounded in the source text
- If proof is weak, the signal should be downgraded or discarded
- Link the insight back to the original item and source URL

## Current Project Mapping

- Source normalization: `src/content_engine/services/workflow_b.py`
- Context rules: `src/content_engine/context/workflow_b_rules.py`
- Pipeline handoff: `src/content_engine/orchestration/live_pipeline.py`
