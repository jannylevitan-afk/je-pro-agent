# Jane Superstar Content Factory — Producer-Orchestrated Restructure

**Date:** 2026-04-29  
**Status:** architecture plan / implementation blueprint  
**Source documents analyzed:**

- `/Users/vasini/Downloads/codex_content_factory_restructure_spec_ru.md`
- `/Users/vasini/Downloads/deep-research-report (2).md`
- `/Users/vasini/Downloads/producer_agent_послкдний).md`
- Current repo architecture: `content_engine_architecture_v3.md`, `docs/handoffs/2026-04-28-system-handoff.md`, current `src/content_engine/*`

## 1. Core Decision

The current Search / Research Agent layer is working and must not be rebuilt.

The restructure happens after evidence-backed `SourceItem` creation and around the current Analyst-to-Writer boundary.

Current active flow:

```text
Approved Sources / Seed Config
  -> Research Agent
  -> compliance check
  -> native collectors + actor-backed extraction
  -> best-performing post selection
  -> SourceItem + evidence log
  -> routing
  -> Workflow A and/or Workflow B
  -> Analyst / Writer / Video pipeline
  -> Admin-ready outputs
```

Target active flow:

```text
User Season Seed / Strategy Input
  -> Producer Agent creates Season Bible + Research Directives
  -> Research Agent collects only approved public data
  -> SourceItem + Evidence Log
  -> Analyst Entity creates SourceNote + InsightCard + OpportunityCandidate
  -> Opportunity Queue
  -> Producer Orchestrator approves / rejects / holds opportunities
  -> Brief Builder creates ContentBrief or VideoBrief
  -> Workflow A or Workflow B creates one asset
  -> Editor / QA Gate reviews with max 3 passes
  -> HumanReviewAsset
  -> Jane Superstar Admin Hub
```

The Producer also exposes a separate readable `ProducerOutput` document for
human review and interface handoff. This document is not a replacement for the
runtime models. Its current contract lives in
`2026-04-30-producer-output-contract.md`.

## 2. Non-Negotiable Rules

- Research Agent remains the only layer allowed to search, scrape, crawl, or collect external data.
- Producer can create search tasks, but never fetches sources itself.
- Analyst analyzes evidence and creates opportunities, but does not directly command Writer in the new pipeline.
- Brief Builder is the only layer that converts approved opportunities into Writer/Video tasks.
- Workflow A creates video hooks, script, and filming card only.
- Workflow B creates one final text asset per approved opportunity and selected platform.
- No automatic multi-platform variants in the active pipeline.
- No Publisher, Scheduler, Auto-publishing, publish queue, visual producer, platform adapter, or format adapter in this stage.
- Readable ProducerOutput may show planning blocks for Designer, Sales/Automation, Manual Publishing/Calendar, and Analytics, but these are not active runtime services.
- Source evidence stays traceable internally, but final user-facing assets stay clean.
- LinkedIn remains special: final publish text is English, internal Russian master can exist for review.
- Editor / QA Gate has maximum 3 review passes before human review handoff.

## 3. The Producer Change

The Producer Agent is not just another downstream reviewer. It has two roles.

### 3.1 Upstream Season Producer

Before Research runs, Producer receives a human seed:

```text
current season idea
product / offer context
Jane's agenda
rubrics to emphasize
audience focus
constraints
desired business outcome
```

Producer creates:

```text
ProducerBrief
SeasonBible
EpisodePlan[]
SceneCard[]
ResearchDirective[]
SeriesMemory update
```

The key output for Search is `ResearchDirective`.

Producer tells Research Agent what to look for, for example:

```text
Find strong public posts in #недвижка where Bali legal/land risk performed well.
Prefer posts with public metrics, concrete source text, and clear audience pain.
Do not collect private data.
Return SourceItem with evidence fields.
```

Producer does not search. It only creates the task.

### 3.2 Downstream Opportunity Producer

After Analyst creates `OpportunityCandidate`, Producer decides what actually moves into production.

Producer answers:

```text
Do we make this now?
Which workflow: A or B?
Which one platform lane?
What priority?
What production intent?
What constraints must Brief Builder preserve?
```

Producer creates:

```text
ProducerDecision
ApprovedOpportunity
WorkflowTask for Brief Builder
```

## 4. Updated Component Responsibilities

### 4.1 Research Agent

Keep mostly unchanged.

Current files to protect:

```text
src/content_engine/orchestration/search_agent.py
src/content_engine/collectors/native.py
src/content_engine/collectors/apify.py
src/content_engine/knowledge/research_dependencies.py
.agents/skills/research-agent-runner/SKILL.md
.agents/skills/compliance-gate-skill/SKILL.md
.agents/skills/evidence-log-skill/SKILL.md
.agents/skills/routing-skill/SKILL.md
```

Keep:

- compliance first;
- public-source-only collection;
- best-performing post selection;
- engagement scoring;
- `SourceItem` contract;
- evidence log;
- route suggestion: `workflow_a`, `workflow_b`, `both`, `drop`;
- KMD/source material handoff.

Add later, without breaking current collectors:

- optional `ResearchDirective` input from Producer;
- persistent monitoring fields:
  - `source_scanned`;
  - `selected_post_url`;
  - `selected_post_metrics`;
  - `collected_at`;
  - `collector_errors`;
  - `routing_decision`.

### 4.2 Analyst Entity

Current Analyst is too broad. It currently creates `WriterSpec` directly.

New Analyst role:

```text
SourceItem
  -> SourceNote
  -> InsightCard
  -> ResearchHandoffRow
  -> OpportunityCandidate
```

Analyst should answer:

- What happened in the source?
- Why did it perform?
- What theme, angle, emotional trigger, and audience fit are visible?
- Which Jane rubric does it fit?
- What is the opportunity?
- What risks exist?
- Suggested route only.

Analyst should not answer:

- Write this post.
- Make final Writer TZ.
- Pick final priority.
- Approve production.
- Create platform variants.
- Schedule or publish.

Compatibility rule:

- Keep old `WriterSpec` fields temporarily if needed for tests and legacy commands.
- The new content factory pipeline must use `OpportunityCandidate -> ProducerDecision -> BriefBuilder`.

### 4.3 Opportunity Queue

This is the backlog between Analyst and Producer.

It stores:

```text
OpportunityCandidate[]
score
risk level
evidence strength
suggested workflow
suggested platform
status: new / producer_review / approved / rejected / hold
```

Business priority should live in application state or output JSON, not only in an external queue.

### 4.4 Producer Orchestrator

Producer is the decision layer.

It receives:

```text
SeasonBible
EpisodePlan[]
SceneCard[]
OpportunityCandidate[]
SeriesMemory
optional MetricsSnapshot
```

It returns:

```text
ProducerDecision[]
ApprovedOpportunity[]
WorkflowTask[]
ProducerQAReport
SeriesMemory update
```

Producer must never:

- search;
- write final content;
- generate visuals;
- create platform variants;
- schedule;
- publish;
- invent proof, cases, metrics, or fake urgency.

### 4.5 Brief Builder

Brief Builder is the new TZ layer.

It converts:

```text
ApprovedOpportunity
+ OpportunityCandidate
+ ResearchHandoffRow
+ SourceItem evidence
+ Jane rubrics
+ Producer scene context
```

Into:

```text
ContentBrief / WriterSpec for Workflow B
VideoBrief for Workflow A
```

Brief Builder should include:

- selected workflow;
- selected platform;
- Jane rubric;
- audience segment;
- production intent;
- core idea;
- angle;
- emotional trigger;
- source summary;
- source text excerpt;
- what performed;
- factual boundaries;
- must include;
- must not include;
- tone rules;
- opening direction;
- quality criteria;
- risk flags;
- scene function if coming from Producer season plan;
- producer scene type;
- producer plot function;
- producer sales intensity;
- producer scene hook as direction;
- producer CTA or next hook as direction.

Route rule:

- `ApprovedOpportunity.selected_workflow` and `selected_platform` must match `ProducerDecision`.
- `season_id`, `episode_id`, and `scene_id` must match when both sides provide them.
- If a `SceneCard` is attached, it must match the approved `scene_id` and `episode_id`.

Brief Builder must not include:

- visual asset specs;
- platform adaptation matrix;
- publish date;
- scheduled time;
- publisher assignment.

### 4.6 Workflow A — Video

New Workflow A starts from `VideoBrief`, not raw research.

It should output:

```markdown
## Video Content Asset
**Content ID:**
**Title:**
**Platform:**
**Audience:**
**Theme:**
**Approval Status:**

### Selected Hook
...

### Script
...

### Filming Card
...
```

It should not output:

```text
Publish Queue
Scheduled At
Publisher
Auto Publish Status
Distribution Status
```

Legacy note:

- `VideoPublishItem` currently exists in `src/content_engine/models/workflow_a.py`.
- It should be deprecated or removed from the new pipeline after tests are updated.

### 4.7 Workflow B — Text

New Workflow B starts from `ContentBrief`.

It should output exactly one final content asset per approved opportunity.

Final user-facing format:

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

Do not include final user-facing:

```text
Hook block
CTA block
Traceability block
QA block
```

Internal JSON can keep traceability.

### 4.8 Editor / QA Gate

This replaces the public idea of “Analyst reviews Writer.”

It may reuse existing review logic internally, but responsibility becomes editorial QA.

Checks:

- source integrity;
- factual safety;
- Jane voice;
- strong non-generic opening;
- rubric fit;
- audience fit;
- one thought / one emotion / one plot;
- no invented facts;
- no unsupported claims;
- no banned generic intros;
- no standalone CTA question in Workflow B final text;
- scene function and business function if Producer scene card exists.

Review loop:

```text
draft -> Editor Gate
if pass -> HumanReviewAsset
if fail and pass_count < 3 -> revision
if fail after 3 -> HumanReviewAsset with needs_revision and notes
```

### 4.9 Jane Superstar Admin Hub

The Admin Hub is the output surface, not Notion.

Show:

- Research Monitor;
- Analyst Handoff;
- Opportunity Queue;
- Producer Decisions;
- Workflow A Video Assets;
- Workflow B Text Assets;
- Human Review Status;
- Series / Season view later.

Do not show:

- Scheduler;
- Publisher;
- visual production;
- platform variants;
- publish queue;
- auto-publish status.

## 5. New Data Contracts

### 5.1 SeasonSeed

Human input that starts a season.

```text
seed_id
season_goal
current_context
offer_focus
rubrics_to_emphasize
audience_focus
channels
constraints
date_range
success_metrics
```

### 5.2 ProducerBrief

Strategic context for the season.

```text
creator
brand
audience
offers
season_goal
constraints
metrics
memory
```

### 5.3 SeasonBible

```text
season_id
title
season_thesis
narrative_question
main_conflict
audience_goal
product_role
emotional_arc
sales_arc
episodes
success_metrics
```

### 5.4 EpisodePlan

```text
episode_id
season_id
title
day_range
episode_question
conflict
insight
sales_function
hook_to_next_episode
scene_ids
```

### 5.5 SceneCard

```text
scene_id
episode_id
channel
format
scene_type
plot_function
sales_intensity
hook
context
conflict_or_question
value_point
proof_point
offer_bridge
cta
next_hook
required_assets
qa_status
```

Rule:

```text
Hook -> Context -> Tension/Question -> Value/Proof -> CTA or Next Hook
```

If a scene has neither narrative function nor business function, Producer must drop it.

### 5.6 ResearchDirective

Producer output for Search Agent.

```text
directive_id
season_id
episode_id
scene_id
rubric
audience_segment
content_theme
platform_targets
approved_source_groups
search_goal
must_collect
must_avoid
evidence_requirements
priority
created_at
```

Research Agent consumes this as instruction, but remains the only collector.

### 5.7 OpportunityCandidate

Analyst output.

```text
opportunity_id
source_item_id
source_name
source_type
source_url
topic
core_idea
jane_adaptation_brief
audience_segment
content_theme
rubric
suggested_workflow
suggested_platform
popularity_label
public_metrics
what_performed
emotional_trigger
strategic_fit_score
evidence_strength_score
novelty_score
audience_fit_score
production_complexity_score
risk_level
risk_flags
analyst_reason
created_at
```

### 5.8 ProducerDecision

```text
decision_id
opportunity_id
source_item_id
decision: approve / reject / hold
selected_workflow
selected_platform
priority
production_intent
season_id
episode_id
scene_id
reason
constraints
required_evidence
human_notes
created_at
```

### 5.9 ApprovedOpportunity

```text
approved_id
decision_id
opportunity_id
source_item_id
selected_workflow
selected_platform
priority
production_intent
core_idea
jane_adaptation_brief
evidence_refs
risk_flags
season_id
episode_id
scene_id
created_at
```

### 5.10 ContentBrief / VideoBrief

Brief Builder output. Reuse existing `ContentBrief` where possible, but add producer fields.

Required shared fields:

```text
brief_id
source_item_id
opportunity_id
decision_id
workflow
selected_platform
rubric
audience_segment
production_intent
core_idea
angle
emotional_trigger
source_summary
source_text_excerpt
what_performed
factual_boundaries
must_include
must_not_include
tone_rules
opening_direction
quality_criteria
risk_flags
season_id
episode_id
scene_id
producer_scene_type
producer_plot_function
producer_sales_intensity
producer_scene_hook
producer_cta_or_next_hook
```

### 5.11 EditorialReviewResult

```text
review_id
content_id
source_item_id
passed
approval_status
score
failed_checks
revision_notes
factual_risk_flags
voice_risk_flags
review_pass_number
created_at
```

### 5.12 HumanReviewAsset

```text
content_id
source_item_id
opportunity_id
decision_id
brief_id
workflow
platform
title
pillar
audience_segment
approval_status
final_text
internal_ru_master
selected_hook
script
filming_card
editor_score
revision_notes
source_refs
season_id
episode_id
scene_id
created_at
```

## 6. State Machine

New active state machine:

```text
season_seeded
  -> producer_brief_ready
  -> season_bible_ready
  -> research_directives_ready
  -> captured_signal
  -> source_verified
  -> analyst_handoff_ready
  -> opportunity_scored
  -> producer_review
  -> producer_approved / producer_rejected / producer_hold
  -> brief_ready
  -> drafting
  -> editorial_review
  -> revision
  -> approved_for_human_review
  -> archived
```

Deprecated active states:

```text
visual_production
format_adaptation
scheduled
published
queued_for_publish
auto_published
```

## 7. What To Keep From Deep Research

Use the deep research report as production guidance, not as immediate dependency installation.

### Adopt now in codebase

- Pydantic contracts for typed handoffs.
- Deterministic skeletons before LLM enrichment.
- Explicit evidence refs and trace IDs.
- Domain-specific policy checks in code, not hidden in prompts.
- Local JSON/Markdown outputs for Admin Hub.

### Consider later for production infrastructure

- Temporal or Step Functions as durable orchestration spine.
- SQS / PubSub / Kafka / NATS as event layer.
- PostgreSQL or Directus/Supabase as domain state store.
- LangSmith / Braintrust / DeepEval / Ragas for evals and observability.
- Appsmith / ToolJet / Retool / React-admin for the full Admin Hub.

### Do not add now

- A new heavy workflow engine before contracts are stable.
- A publisher/scheduler platform.
- A visual-generation system.
- A multi-platform repurposing engine.

## 8. Implementation Plan

### Step 0 — Freeze current working baseline

Goal: know what currently passes before changing contracts.

Actions:

- Run `pytest`.
- Run mypy if available in the project workflow.
- Save current status in a short implementation note.

No code changes.

### Step 1 — Add Producer architecture docs

Goal: make Producer responsibilities explicit before code.

Actions:

- Add this architecture document.
- Add Producer Agent entity document.
- Do not change runtime code.

### Step 2 — Add new models without changing pipeline

Add:

```text
src/content_engine/models/producer.py
src/content_engine/models/opportunity.py
src/content_engine/models/brief_builder.py
src/content_engine/models/editorial_gate.py
src/content_engine/models/content_factory.py
```

Tests:

```text
tests/models/test_producer_models.py
tests/models/test_opportunity_models.py
tests/models/test_brief_builder_models.py
tests/models/test_editorial_gate_models.py
tests/models/test_content_factory_models.py
```

Acceptance:

- Existing tests still pass.
- New models validate required fields.

### Step 3 — Add Producer service without wiring it into old flow

Add:

```text
src/content_engine/services/producer.py
```

Functions:

```text
create_producer_brief
create_season_bible
plan_episodes
create_scene_cards
create_research_directives
review_opportunities
approve_opportunity
hold_opportunity
reject_opportunity
update_from_metrics
```

Tests:

```text
tests/services/test_producer_service.py
```

Acceptance:

- Producer can create a season and research directives from fixture input.
- Producer can approve/reject/hold opportunity fixtures.
- Producer never fetches URLs.

### Step 4 — Make Analyst emit OpportunityCandidate

Modify:

```text
src/content_engine/services/analyst.py
src/content_engine/llm/analyst.py
```

Rules:

- Keep `ResearchHandoffRow`.
- Add `OpportunityCandidate`.
- Keep legacy `WriterSpec` only as compatibility until new pipeline is wired.
- New code paths must consume `OpportunityCandidate`, not `WriterSpec`.

Tests:

```text
tests/services/test_analyst_service.py
tests/llm/test_analyst.py
```

Acceptance:

- Analyst no longer needs to be the direct Writer TZ authority in the new pipeline.

### Step 5 — Add Opportunity Queue service

Add:

```text
src/content_engine/services/opportunity_queue.py
```

Responsibilities:

- dedupe opportunities;
- compute or normalize score;
- sort by priority;
- expose Producer review list.

Tests:

```text
tests/services/test_opportunity_queue.py
```

### Step 6 — Add Brief Builder

Add:

```text
src/content_engine/services/brief_builder.py
```

Responsibilities:

- convert `ApprovedOpportunity` into `ContentBrief` or `VideoBrief`;
- preserve evidence boundaries;
- apply Jane rubrics and Producer scene context;
- include `must_include` and `must_not_include`.

Tests:

```text
tests/services/test_brief_builder.py
```

### Step 7 — Refactor Workflow B to accept ContentBrief from Brief Builder

Modify carefully:

```text
src/content_engine/services/workflow_b.py
src/content_engine/services/writer_entity.py
src/content_engine/llm/writer.py
src/content_engine/orchestration/live_pipeline.py
```

Rules:

- One approved opportunity produces one asset.
- No platform-lane expansion in new pipeline.
- Keep LinkedIn English final / Russian internal master policy.
- User-facing asset keeps clean format.

Tests:

```text
tests/services/test_workflow_b_pipeline.py
tests/services/test_writer_entity.py
tests/llm/test_writer.py
```

### Step 8 — Refactor Workflow A to accept VideoBrief and remove publish queue from new output

Modify:

```text
src/content_engine/models/workflow_a.py
src/content_engine/services/workflow_a.py
src/content_engine/orchestration/video_gate.py
```

Rules:

- Keep hook/script/filming card.
- Deprecate `VideoPublishItem` in new pipeline.
- Optional n8n notification can remain disabled by default and not required.

Tests:

```text
tests/services/test_workflow_a_pipeline.py
tests/orchestration/test_video_gate.py
tests/n8n/test_workflow_a_n8n_payloads.py
```

### Step 9 — Add Editor / QA Gate

Add or refactor:

```text
src/content_engine/models/editorial_gate.py
src/content_engine/services/editorial_gate.py
```

Rules:

- max 3 review passes;
- failed after 3 becomes `needs_revision`;
- no Publisher/Scheduler handoff.

Tests:

```text
tests/services/test_editorial_gate.py
```

### Step 10 — Add Content Factory orchestrator

Add:

```text
src/content_engine/services/content_factory.py
```

Optional CLI later:

```text
python -m content_engine.cli run-content-factory --seed examples/seed_config.sample.yaml --output outputs/latest
```

Pipeline:

```text
SeasonSeed
  -> Producer research directives
  -> Research Agent
  -> Analyst opportunities
  -> Opportunity Queue
  -> Producer decisions
  -> Brief Builder
  -> Workflow A/B
  -> Editor Gate
  -> HumanReviewAsset outputs
```

Tests:

```text
tests/services/test_content_factory_pipeline.py
```

### Step 11 — Write Admin Hub-ready outputs

Create:

```text
outputs/latest/research_handoff.json
outputs/latest/opportunity_queue.json
outputs/latest/producer_decisions.json
outputs/latest/workflow_a_video_assets.json
outputs/latest/workflow_b_text_assets.json
outputs/latest/human_review_assets.json
outputs/latest/season_bible.json
outputs/latest/episode_plan.json
```

### Step 12 — Update Jane Superstar UI later

Only after backend contracts are stable.

UI should read or embed:

```text
HumanReviewAsset[]
ProducerDecision[]
OpportunityCandidate[]
SeasonBible
EpisodePlan[]
```

No scheduler/publisher sections.

## 9. Acceptance Criteria

Architecture passes when:

- Research Agent remains the only collection layer.
- Producer can direct Research through `ResearchDirective` without collecting data.
- Analyst outputs `OpportunityCandidate`.
- Producer approves/rejects/holds opportunities.
- Brief Builder creates the Writer/Video task.
- Workflow A/B start from briefs in the new pipeline.
- Workflow A has no publish queue in new output.
- Workflow B has no platform variants in new output.
- Editor Gate produces `approved_for_human_review` or `needs_revision`.
- Admin-ready outputs are human-review assets, not scheduled/published assets.

## 10. Minimal Safe Version

If the full restructure is too large for one coding pass, implement in this order:

1. Add Producer and Opportunity models.
2. Make Analyst emit `OpportunityCandidate`.
3. Add Producer decision service.
4. Add Brief Builder.
5. Run Workflow B from one approved `ContentBrief`.
6. Remove Workflow A publish queue from new output.
7. Add `HumanReviewAsset` output.

The smallest meaningful architecture fix is:

```text
Analyst -> OpportunityCandidate -> ProducerDecision -> BriefBuilder -> Workflow
```

Everything else can be layered on safely after that.
