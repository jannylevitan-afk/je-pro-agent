# Admin Panel GPT Handoff — Content Engine

## Purpose

This handoff explains the current Content Engine architecture and the new product direction: **remove Notion as the operating/output layer** and replace it with a dedicated admin panel.

The next GPT/designer should use this file to create a professional admin-panel product spec or UI/UX design file where the user can:

- see the final output of both workflows in one place;
- review, approve, rewrite, delete, or re-brief content;
- inspect the source evidence behind every output;
- track daily research runs, pipeline status, and failures;
- view analytics and feedback loops;
- manage sources, audiences, prompts, and workflow settings;
- keep the system simple, clear, and production-minded.

## Major Product Decision

**Notion is no longer the destination.**

Previously, the architecture described Notion as the Content Operating Hub. That layer should now be treated as deprecated legacy wording. The new destination is:

```text
Admin Operating Hub
```

The admin panel becomes the main place where all system results are stored, viewed, edited, reviewed, and analyzed.

Important:

- Do not design a Notion-like clone with unnecessary complexity.
- Do not assume content is exported to Notion.
- The admin panel is the source of truth for workflow output.
- Publishing remains manual at first; the system prepares assets and scheduling suggestions.
- The backend can still use internal service names like `drafts`, `briefs`, `sources`, etc., but user-facing UI should be clean.

## Current Architecture Summary

The system is an AI content engine for collecting public market/content signals and turning them into two independent content workflows.

```text
Research Agent
  -> collects sources
  -> normalizes raw data
  -> logs evidence
  -> routes each signal

Route A: video refs / hooks / scripts
  -> Workflow A — Video Pipeline

Route B: text insight / market signal / founder angle
  -> Analyst Entity
  -> Writer Entity
  -> Workflow B — Content Farm

Both workflows
  -> Admin Operating Hub
  -> review, calendar, analytics, feedback
```

## Core Principle

Research Agent is the only part of the system that searches and collects.

Workflows do not search. They receive prepared input from Research Agent.

```text
Research Agent = collects and routes
Workflow A = prepares video production assets
Workflow B = prepares written content assets
Admin Panel = displays, reviews, edits, tracks, and analyzes everything
```

## Layer 0 — Research Agent

Research Agent collects and prepares source material.

### Input Sources

- Instagram profiles and reels
- Telegram channels
- LinkedIn profiles/posts
- YouTube/TikTok competitor videos
- Web reports and articles
- Internal notes and voice transcripts
- Discovery scans for similar sources

### Research Agent Responsibilities

- source discovery;
- compliance check;
- source collection;
- deduplication;
- normalization;
- evidence logging;
- confidence scoring;
- routing.

### Required Evidence Fields

Every source-derived item needs:

- source URL;
- timestamp;
- raw excerpt;
- source type;
- source name;
- confidence score;
- routing decision;
- audience segment;
- content theme.

### Routing Rules

| Signal Type | Route |
|---|---|
| Video refs, reels, TikTok/YouTube, strong visual hooks | Workflow A |
| Text insight, market observation, founder angle, expert pain | Workflow B |
| Strong video with useful text/transcript depth | Both |
| Weak or unsupported signal | Drop |

## Workflow A — Video Pipeline

Workflow A turns video-native signals into production-ready video assets.

### Workflow A Steps

1. Receive video signal from Research Agent.
2. Capture video reference, title, caption, transcript, source link, and public metrics.
3. Extract hook patterns.
4. Develop 3-5 video hook/script angles.
5. Select the strongest script.
6. Create script-ready output.
7. Create filming card.
8. Send to manual filming/publishing queue.
9. Track performance after publishing.
10. Feed top hooks/topics back to Research Agent.

### Workflow A Output Objects

- Video Source Note
- Hook Candidates
- Selected Hook
- Video Script
- Filming Card
- Publish Calendar Item
- Performance Record

### Workflow A Admin View

The admin should show:

- video source preview;
- source URL and transcript;
- extracted hook pattern;
- selected hook;
- script text;
- filming instructions;
- priority;
- status;
- publish platform;
- performance after publishing.

## Workflow B — Content Farm

Workflow B turns text-heavy signals into written content assets.

Workflow B is split into two entities:

```text
Analyst Entity -> creates Writer-ready TZ
Writer Entity  -> writes final content asset
```

Workflow B does not write directly from a topic.

It writes from:

- source note;
- insight card;
- audience fit;
- proof boundaries;
- Analyst TZ;
- platform lane;
- tone/register.

## Analyst Entity — Workflow B Phase 1/2

Analyst Entity sits between Research Agent and Writer Entity.

It does not write posts.

It converts raw source material into a clear task specification for the writer.

### Analyst Entity Input

- source URL;
- source type;
- source name;
- transcript/raw text;
- timestamp;
- public metrics;
- audience segment;
- content theme;
- routing decision;
- evidence excerpt;
- confidence score.

### Analyst Entity Output

Analyst produces:

- Source Note;
- Insight Card;
- Writer Entity TZ.

### Writer Entity TZ Template

````markdown
## Writer Entity TZ

### Phase 1 Source Note
- Source ID:
- Source URL:
- Platform:
- Audience:
- Content theme:
- Raw excerpt:

### Phase 2 Insight Card
- Topic:
- Angle:
- Emotional Trigger:
- Audience Fit:
- Useful Lesson:
- Narrative Type:
- Reuse Score:
- Confidence:

### Marketing Research Adaptation
- JTBD / Customer Job:
- Pain Point:
- Trigger Event:
- Desired Outcome:
- Behavioral Trigger:

### Writer Constraints
- Purpose:
- Tone/Register:
- Format:
- Opening guide:
- Key points:
- Facts allowed:
- Reference sources:

### Opening Sentence Guardrails
- First line of Final Text = opening_sentence; no separate Hook block.
- 5-14 words, source-specific, concrete, understandable without context.
- Must create tension, recognition, useful problem, conflict, fear, benefit, or precise audience pain.
- Reject tautology and repeated-root loops: `дешёвый/дешево`, `cheap/cheap`, `risk/risky`.
- Banned weak examples: `Дешёвый вход на Бали...`, `Дешёвый риск почти никогда не выглядит дешево`, `Cheap risk rarely looks cheap`.
- If the sentence can fit any post, merely restates the topic, or repeats the same semantic hit twice, regenerate it.
- Do not end Final Text with a standalone CTA question.

### Required Output Format
```markdown
## Final Content Asset
**Content ID:**
**Title:**
**Platform:**
**Pillar:**
**Format:**
**Approval Status:**

### Final Text
...
```

Do not output `Hook`, `CTA`, `Traceability`, or `QA` sections in the final asset.
````

## Writer Entity — Workflow B Writing Layer

Writer Entity consumes Analyst TZ and creates platform-specific final text.

### Writer Rules

- Do not write from a raw topic.
- Use the source note as factual boundary.
- Do not invent claims.
- Opening sentence is part of Final Text, not a separate Hook field.
- Final Content Asset should not expose internal QA/traceability blocks.
- LinkedIn publish text is English.
- Russian master/context can still exist internally for review.
- Instagram text is in Russian.
- Human review is required before publishing.

### Workflow B Final Asset Template

```markdown
## Final Content Asset
**Content ID:**
**Title:**
**Platform:**
**Pillar:**
**Format:**
**Approval Status:**

### Final Text
...
```

## Admin Panel As The New Operating Hub

The admin panel replaces Notion.

It should be simple, professional, and focused on operational clarity.

### Admin Responsibilities

- receive and store all Research Agent outputs;
- show pipeline status for each item;
- show final outputs for Workflow A and Workflow B;
- support review actions;
- display evidence and traceability;
- show analytics and performance feedback;
- help improve future runs.

## Recommended Admin Information Architecture

Keep the admin to 7 main sections for MVP.

### 1. Dashboard

Purpose: quick health overview.

Show:

- today's research run status;
- number of collected sources;
- routed to Workflow A;
- routed to Workflow B;
- items awaiting review;
- items approved;
- failed/error items;
- top content themes;
- top performing hooks/topics;
- recent alerts.

### 2. Sources & Research

Purpose: inspect what Research Agent collected.

Show:

- source list;
- platform;
- source type;
- source URL;
- raw excerpt;
- timestamp;
- confidence score;
- routing decision;
- compliance status;
- dedupe status;
- source theme;
- audience segment.

Useful filters:

- platform;
- route;
- confidence;
- source theme;
- audience;
- date collected;
- status.

### 3. Workflow A — Video

Purpose: manage video production pipeline.

Show:

- video refs;
- extracted hooks;
- selected script;
- filming card;
- filming status;
- publish status;
- platform;
- priority;
- performance metrics.

Recommended board statuses:

- `source_collected`
- `hooks_extracted`
- `script_ready`
- `filming_needed`
- `filmed`
- `published`
- `measured`

### 4. Workflow B — Content

Purpose: manage written-content pipeline.

Show:

- source note;
- Insight Card;
- Writer Entity TZ;
- ideas;
- content brief;
- draft/final asset;
- review status;
- publish language;
- platform lane.

Recommended board statuses:

- `source_collected`
- `analyst_ready`
- `brief_ready`
- `draft_ready`
- `awaiting_review`
- `approved`
- `needs_rewrite`
- `re_brief`
- `deleted`
- `published`
- `measured`

### 5. Review Queue

Purpose: the main daily working screen.

This should be the most important screen for the user.

Show cards for items that require human decision.

Each card should show:

- final asset preview;
- platform;
- audience;
- pillar;
- source evidence;
- confidence score;
- risk flags;
- AI generated text;
- approval status.

Actions:

- approve;
- request rewrite;
- re-brief;
- delete;
- add human note;
- copy final text;
- mark as published.

### 6. Content Calendar

Purpose: see what is ready, scheduled, published, and measured.

Show:

- platform;
- title;
- final text preview;
- publish language;
- publish date target;
- approval status;
- published URL;
- performance status.

Important:

- Publishing remains manual in MVP.
- Admin prepares and tracks publish-ready assets.
- The user can paste published URL after manual publication.

### 7. Analytics & Feedback

Purpose: close the loop back into Research Agent.

Show:

- views;
- likes;
- saves;
- shares;
- comments;
- DMs;
- profile visits;
- inquiries;
- engagement rate;
- performance tier: `top`, `average`, `weak`;
- top hooks;
- top topics;
- best source themes;
- weak source themes;
- recommendations for next Research Agent run.

Feedback examples:

- "Boost boutique hotel market-observation sources."
- "Reduce generic villa sources with low proof."
- "More video hooks around legal-structure risk."
- "LinkedIn B2B performs better with operator-discipline angle."

## Recommended Data Objects For Admin

The admin does not need to expose every backend field, but it should support these core objects.

### SourceItem

```json
{
  "id": "source_001",
  "source_type": "telegram_post",
  "source_name": "Wellstate",
  "source_url": "https://...",
  "external_item_id": "2001",
  "collected_at": "2026-04-26T09:00:00Z",
  "published_at": "2026-04-26T08:10:00Z",
  "audience_segment": "developer_investor",
  "content_theme": "boutique_hotels",
  "raw_excerpt": "...",
  "transcript_text": "...",
  "media_urls": [],
  "engagement_signals": {},
  "routing_decision": "workflow_b",
  "routing_confidence": 0.9,
  "processing_state": "collected"
}
```

### Workflow A Asset

```json
{
  "id": "video_asset_001",
  "source_item_id": "source_001",
  "status": "script_ready",
  "platform": "instagram",
  "video_title": "...",
  "selected_hook": "...",
  "script_text": "...",
  "filming_card": {
    "priority": 1,
    "shooting_notes": "...",
    "visual_device": "..."
  },
  "publish_status": "manual_pending",
  "performance_tier": null
}
```

### Workflow B Asset

```json
{
  "id": "content_asset_001",
  "source_item_id": "source_001",
  "status": "awaiting_review",
  "platform": "linkedin",
  "platform_lane": "linkedin_b2b",
  "working_language": "ru",
  "publish_language": "en",
  "audience": "developer_investor",
  "pillar": "expertise_proof",
  "analyst_tz": "...",
  "final_content_asset": "## Final Content Asset...",
  "final_text_ru": "...",
  "final_text_en": "...",
  "risk_flags": [],
  "human_review_required": true
}
```

### PerformanceRecord

```json
{
  "id": "performance_001",
  "content_asset_id": "content_asset_001",
  "platform": "linkedin",
  "published_url": "https://...",
  "published_at": "2026-04-30T10:00:00Z",
  "views": 0,
  "likes": 0,
  "saves": 0,
  "shares": 0,
  "comments": 0,
  "profile_visits": 0,
  "dms_received": 0,
  "inquiries": 0,
  "performance_tier": "average",
  "feedback_signal": "boost_topic"
}
```

## Simple Backend Recommendation

For MVP, keep infrastructure boring and reliable.

Recommended:

- one backend API;
- one database;
- one admin frontend;
- one file/object storage area for raw transcripts, KMD files, screenshots, and exports;
- one event log table for pipeline actions.

Good stack options:

- Next.js admin + Supabase/Postgres;
- FastAPI backend + Postgres + React admin;
- Django admin-style backend if speed matters more than custom UI.

The next GPT should choose a stack only after confirming implementation constraints. For design/spec purposes, focus on product structure and data contracts first.

## MVP Scope

Build the admin around the real workflow, not around every possible future feature.

### MVP Must Have

- Dashboard
- Sources & Research table
- Workflow A board/table
- Workflow B board/table
- Review Queue
- Content Calendar
- Analytics & Feedback
- detail page for each source/item
- detail page for each final asset
- approve/rewrite/re-brief/delete actions
- published URL and metrics entry

### MVP Should Not Have Yet

- automatic publishing;
- complex role-based permissions;
- multi-client workspace switching;
- advanced drag-and-drop automation builder;
- chat interface;
- billing;
- CRM;
- complex prompt marketplace.

## Key UX Principle

The user should always understand:

```text
Where did this content come from?
Why did the system create it?
Which workflow produced it?
What is ready for review?
What should I do next?
What performed well?
What should Research Agent look for next?
```

If a screen does not answer one of those questions, it probably does not belong in MVP.

## Suggested Admin Screens

### Dashboard Layout

Top cards:

- Research run status
- Awaiting review
- Workflow A ready to film
- Workflow B ready to approve
- Published this week
- Top-performing theme

Main sections:

- Recent pipeline activity
- Items needing action
- Top signals from analytics
- Failed runs / warnings

### Source Detail Page

Tabs:

- Evidence
- Raw transcript
- Routing
- Workflow outputs
- Analytics feedback

### Workflow A Detail Page

Tabs:

- Source
- Hooks
- Script
- Filming card
- Publish tracking
- Performance

### Workflow B Detail Page

Tabs:

- Source Note
- Analyst TZ
- Brief
- Final Asset
- Review Notes
- Performance

### Review Queue Detail

Two-column layout:

Left:

- source evidence;
- Analyst TZ summary;
- risk flags.

Right:

- final asset preview;
- language versions;
- action buttons.

## Analytics Model

Analytics should not only report metrics. It should produce decisions.

### Metrics

- views;
- likes;
- saves;
- shares;
- comments;
- profile visits;
- DMs;
- inquiries;
- engagement rate;
- content-to-inquiry signal.

### Decision Metrics

- performance tier: `top`, `average`, `weak`;
- strongest platform;
- strongest content theme;
- strongest audience segment;
- strongest opening pattern;
- best source type;
- best route.

### Feedback To Research Agent

The admin should show and store feedback signals:

- `boost_source_type`
- `reduce_source_type`
- `boost_topic`
- `reduce_topic`
- `boost_platform_lane`
- `avoid_angle`
- `repeat_hook_pattern`

## Review And Status Rules

### Workflow A Statuses

```text
collected
video_intake_ready
hooks_ready
script_ready
filming_needed
filmed
manual_publish_ready
published
measured
```

### Workflow B Statuses

```text
collected
analyst_ready
brief_ready
draft_ready
awaiting_review
approved
needs_rewrite
re_brief
deleted
manual_publish_ready
published
measured
```

### Review Actions

```text
approve
request_rewrite
re_brief
delete
mark_published
add_metrics
send_feedback_to_research
```

## Language Policy

- Instagram output: Russian.
- Telegram output: Russian.
- LinkedIn publish output: English.
- For LinkedIn, keep Russian working/master context internally when useful, but the visible publish-ready text should be English.
- Admin UI can be Russian-first because the user works in Russian.

## What The Next GPT Should Produce

The next GPT should create a professional admin design/spec file, not implementation code yet.

Required deliverable:

```text
admin_panel_product_spec.md
```

The spec should include:

- product goal;
- user roles;
- information architecture;
- screen list;
- screen-by-screen requirements;
- key tables/cards;
- data objects;
- status model;
- review actions;
- analytics model;
- MVP scope;
- out-of-scope list;
- acceptance criteria;
- recommended implementation approach.

## Prompt For The Next GPT

Use this prompt:

```text
You are designing a professional admin panel for an AI Content Engine.

Notion has been removed as the operating/output layer. The admin panel is now the main operating hub where all results from both workflows are stored, reviewed, edited, approved, published manually, and analyzed.

Read the architecture handoff below and create a clean product spec file for the admin panel.

Do not overcomplicate the product.
Do not design a Notion clone.
Do not add unnecessary automation.
Focus on operational clarity, review workflow, final content visibility, evidence traceability, and analytics feedback.

The admin must support:
- Research Agent source collection and routing visibility;
- Workflow A video outputs: hooks, scripts, filming cards, publish tracking, performance;
- Workflow B content outputs: Analyst TZ, briefs, final content assets, review queue, LinkedIn EN publish text, Instagram/TG RU output;
- all final results displayed in a convenient format inside the admin;
- manual review and publishing workflow;
- analytics and feedback loops back into Research Agent.

Create `admin_panel_product_spec.md` with:
1. Product goal
2. MVP scope
3. Information architecture
4. Screen list
5. Screen-by-screen UX requirements
6. Data objects
7. Status model
8. Review actions
9. Analytics model
10. Feedback loop model
11. Out-of-scope items
12. Acceptance criteria
13. Recommended simple implementation approach

Keep it professional, structured, and simple.
```

## Acceptance Criteria For The Admin Spec

The generated admin spec is successful if:

- it fully removes Notion as a required destination;
- it makes the admin panel the operating hub;
- both workflows are visible end to end;
- final outputs are easy to review and copy/use;
- every final asset can be traced back to source evidence;
- analytics produce clear feedback for future Research Agent runs;
- the MVP is realistic and not overbuilt;
- the spec is clear enough for a developer/designer to start building.
