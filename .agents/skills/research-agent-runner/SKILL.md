---
name: research-agent-runner
description: Use when running the full Layer 0 research flow from source collection through evidence logging, routing, workflow handoff, and Notion-ready outputs.
---

# Research Agent Runner

## Overview

This is the top-level skill for the Je Pro Content Engine Research Agent.
It owns the full Layer 0 path:

1. collect public sources
2. normalize raw items
3. apply compliance gate
4. enforce evidence log rules
5. route signals into Workflow A, Workflow B, both, or drop
6. hand valid items into the pipeline and write Notion-ready artifacts

## When to Use

- Daily monitoring runs
- Test runs on curated source lists
- New source onboarding after approval
- Any time the system needs fresh inputs for Workflow A and Workflow B

## Required Sequence

- Run `compliance-gate-skill` before collection on high-risk platforms
- Run `source-discovery-skill` when the source pool must be expanded
- Run `video-intake-skill` for video-native inputs
- Run `insight-extraction-skill` for text-heavy inputs
- Run `evidence-log-skill` before any write to Notion
- Run `routing-skill` before workflow handoff

## Current Project Mapping

- Orchestration: `src/content_engine/orchestration/search_agent.py`
- Local dry run: `src/content_engine/runtime/search_dry_run.py`
- Pipeline handoff: `src/content_engine/orchestration/live_pipeline.py`

## Tooling Notes

- Prefer public metadata and feeds first
- Exa MCP is best for discovery
- Firecrawl MCP and Apify MCP are for structured page extraction
- Playwright MCP is a fallback for public pages that need rendering
- Avoid authenticated scraping unless compliance explicitly allows it
