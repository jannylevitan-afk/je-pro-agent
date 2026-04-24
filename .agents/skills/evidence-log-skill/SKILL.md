---
name: evidence-log-skill
description: Use when a source-derived insight is about to enter Workflow A, Workflow B, or Notion and must be checked for traceable proof.
---

# Evidence Log Skill

## Overview

Nothing reaches Notion without a minimum evidence payload.

## Required Fields

- source URL
- timestamp
- raw excerpt
- confidence score

## Rules

- Raw excerpts come from the collected item, not from rewritten drafts
- If any field is missing, the item is dropped or held for review
- Evidence must point back to one canonical upstream item
- This skill exists to block plausible-sounding nonsense

## Current Project Mapping

- Evidence contract: `src/content_engine/orchestration/search_agent.py`
- Source persistence: `src/content_engine/notion/sync.py`
