---
name: compliance-gate-skill
description: Use when the Research Agent needs to decide whether a platform or source can be collected safely with public-only, minimal-data rules.
---

# Compliance Gate Skill

## Overview

Assess whether a target is safe to collect before any scraping or page extraction.

## Check

- is the source public
- is HTTPS available
- is an official feed or public page enough
- is the plan avoiding unnecessary personal data
- is there platform ToS or auth risk

## Policy

- Telegram public pages, YouTube feeds, and public web reports are low-risk defaults
- Instagram, TikTok, and LinkedIn are public-metadata-only unless explicitly approved otherwise
- Non-HTTPS or clearly unsafe sources are blocked

## Current Project Mapping

- Compliance assessment: `src/content_engine/orchestration/search_agent.py`
- Native collectors: `src/content_engine/collectors/native.py`
