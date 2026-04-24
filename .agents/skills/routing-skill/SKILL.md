---
name: routing-skill
description: Use when a collected signal needs a deterministic decision about whether it should feed Workflow A, Workflow B, both, or be dropped.
---

# Routing Skill

## Overview

Decide where each collected signal goes:

- video refs -> Workflow A
- market, founder, expert, or text insight -> Workflow B
- strong video plus strong text -> both
- weak or unsupported signal -> drop

## Rules

- Routing must be explicit
- Store both the route and the reason
- Confidence should be attached before any downstream write
- Weak signals are cheaper to drop early than to “creatively improve” later

## Current Project Mapping

- Deterministic router: `src/content_engine/services/routing.py`
- Search Agent evidence and handoff: `src/content_engine/orchestration/search_agent.py`
