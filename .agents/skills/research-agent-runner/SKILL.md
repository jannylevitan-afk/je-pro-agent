---
name: research-agent-runner
description: Use when running the full Layer 0 research flow from source collection through evidence logging, routing, workflow handoff, and Admin Operating Hub outputs.
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
6. hand valid items into the pipeline and write Admin Operating Hub-ready artifacts

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
- Run `evidence-log-skill` before any write to downstream artifacts
- Run `routing-skill` before workflow handoff

## Required Research Payload

Every accepted source item must carry:

- source URL
- timestamp or collection date
- raw excerpt
- confidence score
- canonical upstream item
- immutable raw payload snapshot

For approved monitored public accounts and channels, the Research Agent must scan recent public posts and select the best-performing post before workflow handoff. Best-performing post means the item with the strongest public engagement score from available public metrics: views, likes, comments, saves, shares. Comments, saves, and shares are stronger signals than passive views.

Use this weighted score when the platform exposes the metrics:

```text
engagement_score =
  likes
  + comments * 4
  + shares * 5
  + saves * 5
  + views * 0.02
  + video_views * 0.02
```

For each selected post, collect:

- post URL
- post title, carousel headline, or visible first-line title when available
- caption or description text
- carousel/image OCR text when available from public/API extraction
- public metrics: views, likes, comments, saves, shares
- engagement score and selection reason
- source post payload snapshot

For Workflow A or `both` routes, the Research Agent must also collect:

- video refs and source links
- video title
- caption text and spoken transcript when public/API-provided
- transcript source
- metadata
- first 3 seconds / source hook / opening line
- hook pattern, hook tension, hook promise, CTA, visual device, repeatable formula
- public comments / reactions when available and compliant
- public metrics: views, likes, comments, saves, shares

Workflow A hook research requires a Producer task:

- Do not run hook research without `ProducerHookSearchTask`.
- Validate a 50-video short-form-first set before hook mining: 15 YouTube, 15 TikTok, 20 Instagram.
- Count only qualified videos toward the 50-video set. Qualified means short-form, public metrics present, and minimum gate passed. Discovery-only links, zero/low metrics, missing Instagram metrics, and long/off-format links must be recorded as dropped or blocked and must not count toward 50.
- Use Reels / TikTok / YouTube Shorts / 9:16 vertical videos as the default. Long educational YouTube videos may support context, but no more than 5 long-form sources may appear in the 50-video validation set.
- Treat the short-form duration target as <= 180 seconds unless Producer says otherwise.
- Focus on the Producer brief: season, episode, scene, audience, pain, desire, tension, target themes, forbidden themes, desired hook mechanics, creator archetypes, languages/regions, and date window.
- Search TikTok, Instagram, YouTube/Shorts, and other Producer-approved public video sources using Exa/Firecrawl/Apify/Playwright as appropriate.
- Apply the minimum analysis gate before hook mining or ranking. Do not count views alone as "залетело":
  - `BROAD_VIRAL`: `views >= 100000`, `like_rate >= 2%`, and `comments >= 30`
  - `NICHE_VIRAL`: `views >= 20000`, `views_to_followers_ratio >= 5`, and `like_rate >= 3%`
  - `STRONG_DISCUSSION`: `comments >= 100` and `comment_rate >= 0.1%`
  - `HIGH_VALUE_SIGNAL`: `share_rate >= 0.5%` or `save_rate >= 0.5%`
  - `SMALL_ACCOUNT_BREAKOUT`: `views >= 10000` and `views_to_followers_ratio >= 10`
  - reject unless the small-account override applies: `views < 10000`, `like_rate < 1%`, `comments < 10`, or known `views_to_followers_ratio < 1`
- Return `HookResearchOutcomeBoard` with public video URL, observed source hook/opening, observed first-frame text, public metrics, engagement score, engagement rank, scan batch size, and selection reason for each research-mined hook.
- Do not convert weak/no-proof hooks into Workflow A. Only `APPROVE_FOR_WORKFLOW_A` + `qa_status = PASS` + acceptable risk may be handed to Brief Builder.

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

## MCP Routing

- Use `exa` to expand the source universe before monitoring starts
- Use `firecrawl` when a public page needs clean content extraction or page search
- Use `apify` when extraction is platform-specific and actor tooling is the better fit
- Use `playwright` only after lighter public-source methods are insufficient
