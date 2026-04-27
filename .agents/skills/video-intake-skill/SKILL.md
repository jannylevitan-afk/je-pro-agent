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
- `raw_payload.first_3_seconds`
- `raw_payload.source_hook`
- `raw_payload.detected_hook` or `raw_payload.opening_line` when a native source hook is detected
- `raw_payload.visual_device`
- `raw_payload.hook_pattern`
- `raw_payload.hook_tension`
- `raw_payload.hook_promise`
- `raw_payload.hook_cta`
- `raw_payload.repeatable_formula`
- `raw_payload.hook_modality` as `visual-first`, `text-first`, or `hybrid`
- `raw_payload.comments_sample` for safe public comments / reactions
- `raw_payload.metadata` for source-native metadata

## Rules

- Do not skip the raw payload snapshot
- Treat the raw payload as an immutable raw payload snapshot for downstream evidence
- Prefer public metadata and transcript layers before deeper scraping
- If the item has video and enough text, it can route to `both`
- Do not invent spoken transcript, comments, metrics, or source hooks when the public source/API does not provide them

## Current Project Mapping

- Native parsing: `src/content_engine/collectors/native.py`
- Structured intake: `src/content_engine/services/workflow_a.py::build_video_intake_record`
- KMD handoff: `src/content_engine/knowledge/kmd.py`
- Workflow A handoff: `src/content_engine/orchestration/live_pipeline.py`
