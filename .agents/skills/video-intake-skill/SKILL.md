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
- video title
- captions or transcript text
- spoken transcript when the public source/API provides it
- metadata
- comments when available through public context
- visual hints and hook signals
- public metrics relevant to routing, especially views, likes, comments, saves, shares

## Output Contract

- canonical `SourceItem`
- `source_type` aligned to the platform
- immutable raw payload
- dedupe key
- transcript text
- media URLs
- engagement signals
- `raw_payload.video_title`
- `raw_payload.caption_text`
- `raw_payload.spoken_transcript`
- `raw_payload.transcript_source`

## Rules

- Do not skip the raw payload snapshot
- Prefer public metadata and transcript layers before deeper scraping
- If the item has video and enough text, it can route to `both`

## Current Project Mapping

- Native parsing: `src/content_engine/collectors/native.py`
- Structured intake: `src/content_engine/services/workflow_a.py::build_video_intake_record`
- KMD handoff: `src/content_engine/knowledge/kmd.py`
- Workflow A handoff: `src/content_engine/orchestration/live_pipeline.py`
