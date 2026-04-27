---
name: hook-mining-skill
description: Use when the Research Agent or Workflow A needs to extract reusable hook formulas from strong video or short-form content.
---

# Hook Mining Skill

## Overview

Extract reusable hook structure from short-form content, especially video-native inputs.

## Extract

- first 3 seconds
- pattern
- tension
- promise
- CTA
- visual device
- repeatable formula

## Output Contract

Return a `hook_mining_card` for every strong candidate:

- hook_text
- pattern
- tension
- promise
- CTA
- visual_device
- repeatable_formula
- modality: visual-first | text-first | hybrid
- why_it_works: contrast | curiosity | proof | authority | identity | tension
- hook_quality_gate

The `hook_quality_gate` must score:

- clarity
- specificity
- tension
- relevance
- continuation_pull
- verdict: pass | revise | drop

The minimum pass score is 20/25. If the candidate is below 20/25, revise or drop it before Workflow A handoff.

## Rules

- Hooks should be reusable patterns, not verbatim theft
- Preserve why the hook works: contrast, curiosity, proof, authority, identity, or tension
- Flag whether the hook is visual-first, text-first, or hybrid

## Current Project Mapping

- Hook generation and ranking: `src/content_engine/services/workflow_a.py`
- Workflow A orchestration: `src/content_engine/orchestration/live_pipeline.py`
