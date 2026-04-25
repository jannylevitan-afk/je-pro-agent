---
name: source-discovery-skill
description: Use when the Research Agent needs to expand source pools from niche inputs, seed accounts, founder lists, competitor sets, or platform keywords.
---

# Source Discovery Skill

## Overview

Find candidate sources for Layer 0B Discovery and tag them with:

- `audience_segment`
- `content_theme`
- likely route
- reason for inclusion

## Inputs

- niche
- seed accounts
- keywords
- platform constraints

## Outputs

- Telegram channels
- Instagram pages
- YouTube or TikTok competitors
- LinkedIn founders
- Web reports or market sources when useful

## Rules

- Discovery does not write directly into Workflow A or Workflow B
- Candidate sources go through approval or explicit inclusion first
- Prefer sources with recurring signal, not one-off noise
- Save why the source matters, not just the handle

## Current Project Mapping

- Candidate scoring: `src/content_engine/services/discovery.py`
- Source collectors: `src/content_engine/collectors/native.py`
- Search orchestration: `src/content_engine/orchestration/search_agent.py`
- Canonical seed pool: `examples/seed_config.sample.yaml`
- Discovery query builder: `content_engine.config.seed_config.build_discovery_queries`
- Native monitoring targets: `content_engine.config.seed_config.build_native_source_targets`

## Blog Source Pool Rules

- Treat `content_theme_sources[].sources` as approved inputs for monitoring.
- Treat `content_theme_sources[].discovery_keywords` and `similar_source_targets` as the inputs for finding similar posts, accounts, channels, reports, and videos.
- Keep the source's `content_theme`, primary audience, and route when building discovery candidates.
- New candidates do not enter monitoring until they are approved or explicitly included.
