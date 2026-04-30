# ProducerOutput Readable Contract

**Date:** 2026-04-30
**Status:** current architecture / human-readable Producer handoff contract
**Implements:** `src/content_engine/models/producer_output_contract.py`, `src/content_engine/services/producer_output_contract.py`
**Boundary:** this is a display/export contract. It does not replace the runtime `ProducerOutput` model and does not add publishing, scheduling, or visual production to the active pipeline.

## 1. Purpose

The Producer has two outputs:

- Runtime output for the content factory: `ProducerBrief`, `SeasonBible`, `EpisodePlan[]`, `SceneCard[]`, `ResearchDirective[]`, `WorkflowTask[]`, `ProducerQAReport`.
- Human-readable output for review, admin display, and handoff: a full `ProducerOutput` document in the format `brief -> season -> episodes -> scene cards -> sales plan -> QA -> tasks for workflow agents`.

The second output is what Jane reviews as a season plan. It must look like a professional production document, not like a raw JSON dump or a list of disconnected post ideas.

## 2. Non-Negotiable Separation

Workflow A and Workflow B stay separate inside the readable ProducerOutput.

| Area | Owner in readable ProducerOutput | What it receives |
|---|---|---|
| Workflow A | `Video / AssetAgent` | video briefs, selected hook direction, short-form script requirements, filming card requirements |
| Workflow B | `CopywriterAgent` / Writer Entity | content briefs, scene conflict, audience, sales function, final text requirements |
| Cross-workflow visual support | `DesignerAgent` | visual direction and NDA-safe references only |
| Manual calendar | `Manual Publishing / Calendar` | ordering of approved scenes only |
| Sales/DM setup | `Sales / AutomationAgent` | keyword and manual lead-flow copy only |
| Analytics | `AnalyticsAgent` | weekly metric reading and feedback to Producer |

`Video / AssetAgent` is the handoff name for Workflow A. It must not write Workflow B final text.

`CopywriterAgent` / Writer Entity is the handoff name for Workflow B. It must not write Workflow A video hooks, scripts, or filming cards.

`Manual Publishing / Calendar` is not a Publisher/Scheduler service. It is a manual planning block for review order and posting rhythm.

## 3. Required Section Order

Readable ProducerOutput must keep this section order:

```text
Producer Brief
Audience
Product Map
Product-to-Story Mapping
Season Bible
Content Lines
Emotional Arc
Sales Arc
Episodes
Scene Cards
CTA Library
Lead Magnets
Proof Plan
Objection Handling
Content Rhythm
Visual System
Sales / Automation Setup
Metrics Plan
SeriesMemory
Tasks for Workflow Agents
QA Report
Guardrails
Final Producer Assembly
What To Do First
```

This mirrors the approved season document format:

```text
brief -> season -> episodes -> scene cards -> sales plan -> QA -> tasks for other agents
```

## 4. Required Agent Task Blocks

The readable output must include these blocks.

### CopywriterAgent

Purpose:

- create Workflow B final text assets;
- use Producer scene cards as the writing direction;
- preserve Jane tone, audience fit, source-backed logic, and sales function.

Must not:

- create video scripts;
- mine or invent Workflow A hooks;
- create multi-platform variants unless a new approved architecture says so.

### Video / AssetAgent

Purpose:

- receive Workflow A briefs;
- prepare selected hook, short-form script, and filming card;
- keep manual filming explicit.

Must not:

- write Workflow B final text;
- create publish queue;
- publish or schedule.

### DesignerAgent

Purpose:

- support approved scenes with visual direction, moodboard notes, and carousel structure;
- check NDA-safe reference usage before project visuals appear.

Must not:

- become an active visual-production pipeline;
- invent proof assets.

### Sales / AutomationAgent

Purpose:

- prepare DM keywords, segmentation questions, lead magnet delivery copy, and manual follow-up prompts.

Must not:

- make fake urgency;
- promise ROI;
- release price, deadline, or legal claims without approval.

### Manual Publishing / Calendar

Purpose:

- arrange approved scenes into a manual review calendar;
- keep direct CTA scenes after proof and objection-handling scenes.

Must not:

- auto-publish;
- schedule automatically;
- bypass human review.

### AnalyticsAgent

Purpose:

- read weekly metrics and audience signals;
- return correction signals to Producer.

Must not:

- infer private user data;
- rewrite the season alone.

## 5. HTML Export Rule

`format_producer_output_html()` exists for local review and admin handoff.

Rules:

- one self-contained HTML string;
- no external fonts, CDN, JS libraries, or remote dependencies;
- readable text size: body `font-size: 17px`;
- calm premium document style;
- clear headings and generous spacing;
- no internal pipeline noise beyond the task blocks listed above.

The reference HTML had small text in several areas. The current export intentionally uses a larger base font and a wider content area.

## 6. Runtime Integration

`run_content_factory_dry_run()` now returns both:

```text
producer_output
readable_producer_output
```

This lets the dry-run keep the machine-safe runtime contract while also exposing the human-readable Producer season document to future CLI, admin, or export layers.

## 7. Guardrails

- Producer does not search, scrape, write final posts, publish, schedule, or generate visuals.
- Research Agent remains the only collection layer.
- Brief Builder remains the layer that converts approved opportunities into Workflow A or Workflow B briefs.
- Workflow A creates video hook/script/filming card only.
- Workflow B creates one final text asset per approved opportunity.
- No active Publisher/Scheduler/Auto-publishing layer exists in this stage.
- Sales must be embedded after context, proof, and objections; no glued-on pitch.
- Product claims, timelines, proof assets, and NDA-sensitive details require human confirmation.
