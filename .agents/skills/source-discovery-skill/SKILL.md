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
