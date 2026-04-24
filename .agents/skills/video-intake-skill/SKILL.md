---
name: video-intake-skill
description: Use when a source item contains video-native material and the Research Agent needs capture-ready inputs for Workflow A.
---

# Video Intake Skill

## Overview

Turn public video signals into a normalized source item that can feed the Video pipeline.

## Capture

- video refs
- source links
- captions or transcript text
- metadata
- comments when available through public context
- visual hints and hook signals

## Output Contract

- canonical `SourceItem`
- `source_type` aligned to the platform
- immutable raw payload
- dedupe key
- transcript text
- media URLs
- engagement signals

## Rules

- Do not skip the raw payload snapshot
- Prefer public metadata and transcript layers before deeper scraping
- If the item has video and enough text, it can route to `both`

## Current Project Mapping

- Native parsing: `src/content_engine/collectors/native.py`
- Workflow A handoff: `src/content_engine/orchestration/live_pipeline.py`
