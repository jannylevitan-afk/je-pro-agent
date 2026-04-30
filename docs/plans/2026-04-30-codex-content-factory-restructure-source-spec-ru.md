# Codex Implementation Spec — перестройка Jane Superstar Content Factory

> Agent-first status: historical/source implementation spec.
> Canonical current architecture lives in
> `docs/architecture/2026-04-29-content-factory-producer-restructure.md`.
> If this file conflicts with `AGENTS.md`, `docs/README.md`, current
> architecture docs, or ADRs, follow the canonical docs.
>
> Use this file for background context and gap analysis only. Do not treat it as
> an executable runbook.

**Дата:** 2026-04-28  
**Репозиторий:** `Je Pro Agent`  
**Текущая ветка:** `codex/content-engine-core`  
**Цель документа:** дать Codex/developer точное задание: как перестроить текущую систему в правильный content-factory flow, что оставить, что убрать, какие новые сущности добавить, какие файлы изменить и как проверить результат.

---

## 0. Главный вывод

Текущая система уже имеет сильную базу:

```text
Approved sources / seed config
  -> Research Agent
  -> compliance check
  -> native collectors + MCP/actor-backed extraction
  -> best-performing post selection
  -> canonical SourceItem
  -> evidence log
  -> routing
  -> Workflow A and/or Workflow B
  -> Analyst / Writer / Video pipeline
  -> Admin Hub-ready final outputs
```

Её не нужно ломать. Нужно перестроить **зону между Analyst и Writer**, потому что сейчас Analyst слишком много делает сам: анализирует, формирует ТЗ, частично направляет Writer и потом проверяет результат. Это смешивает роли.

Новая архитектура должна быть такой:

```text
Approved Sources / Seed Config
  -> Research Agent
  -> SourceItem + Evidence Log
  -> Analyst Entity
  -> Opportunity Queue
  -> Producer Orchestrator
  -> Brief Builder
  -> Workflow A / Workflow B
  -> Editor / QA Gate
  -> Human Review Assets
  -> Admin Operating Hub / Jane Superstar
```

В этом этапе **НЕ НУЖНЫ** и должны быть убраны из активного flow:

```text
[Visual / Format / Adaptation]
[Publisher / Scheduler]
```

Это значит:

- не делать визуальные ассеты;
- не делать форматные адаптации как отдельный слой;
- не делать multi-platform repurposing;
- не делать scheduled/publish queue;
- не делать auto-publishing;
- не готовить отдельный Publisher Agent;
- не строить Scheduler;
- не выводить publish/schedule logic в Admin UI.

Система должна готовить **research-backed briefs, video scripts, text drafts, editorially reviewed final assets** для ручного human review.

---

## 1. Неприкосновенные правила

### 1.1 Research Agent остаётся единственным search/data collection layer

Оставить текущее системное правило:

```text
Research Agent is the only layer that searches and collects data.
Workflows do not search.
They only process prepared source items.
```

Нельзя давать Analyst, Writer, Producer, Brief Builder или Editor прямой web/platform search.

Они могут работать только с:

- `SourceItem`;
- `ResearchHandoffRow`;
- evidence log;
- approved source metadata;
- already-collected metrics;
- internal Brand OS / rubric context.

### 1.2 Source evidence нельзя терять

На каждом этапе downstream нужно сохранять traceability:

```text
source_url
source_name
source_type
published_at / collected_at
raw excerpt / transcript_text
engagement_signals
routing_decision
confidence / risk flags
```

Но traceability не должна обязательно показываться в user-facing final asset. Она должна быть доступна в internal JSON/Admin Hub backend structure.

### 1.3 Аналитик больше не должен напрямую командовать писателем

Старый implicit flow:

```text
Research -> Analyst -> WriterSpec -> Writer -> Analyst Review
```

Новый flow:

```text
Research -> Analyst -> OpportunityCandidate
OpportunityCandidate -> ProducerDecision
ProducerDecision -> Brief Builder -> WriterSpec / VideoBrief
WriterSpec / VideoBrief -> Writer / Workflow A
Draft -> Editor Gate -> Human Review Asset
```

Analyst даёт инсайт и возможность.  
Producer решает, что производить.  
Brief Builder превращает решение в ТЗ.  
Writer пишет.  
Editor защищает качество.

### 1.4 Убрать Publisher/Scheduler из активного production flow

Убрать или отключить:

- `Publish Queue` блоки в Workflow A output;
- scheduled status;
- scheduler fields;
- publisher/service concepts;
- auto-publish hooks;
- Admin UI секции/фильтры, которые подразумевают scheduled publishing;
- обязательный `n8n` dispatch для script-ready publish flow.

Разрешено оставить только нейтральный status для human review:

```text
created
needs_revision
approved_for_human_review
archived
```

Если нужно оставить старые поля ради обратной совместимости, пометить их deprecated и не заполнять в новом pipeline.

### 1.5 Убрать Visual / Format / Adaptation из активного production flow

В этом этапе нельзя добавлять отдельный слой:

```text
Visual Producer
Format Adapter
Platform Adapter
Multi-platform adaptation
Repurpose engine
```

Важно: это не означает удаление Workflow A Video. Workflow A остаётся, потому что это script/filming pipeline, а не visual production engine.

Разрешено:

- video script;
- filming card;
- caption draft, если он нужен как часть video asset;
- one selected platform per asset.

Не разрешено:

- генерация визуалов;
- carousel design specs;
- cross-platform variants;
- automatic adaptation for Instagram/LinkedIn/Telegram/TikTok in one run;
- format repurposing stage after writing.

---

## 2. Target architecture

### 2.1 Целевая схема

```text
┌────────────────────────────────────────────────────────────┐
│ Brand OS / Jane Rubrics / Voice Rules / Audience Segments  │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               v
Approved Sources / Seed Config
                               │
                               v
┌────────────────────────────────────────────────────────────┐
│ Research Agent                                              │
│ - compliance check                                           │
│ - native collectors / Apify / public extraction              │
│ - best-performing post selection                            │
│ - SourceItem + Evidence Log                                 │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               v
┌────────────────────────────────────────────────────────────┐
│ Analyst Entity                                              │
│ - SourceNote                                                │
│ - InsightCard                                               │
│ - ResearchHandoffRow                                        │
│ - OpportunityCandidate                                      │
│ - risk flags                                                │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               v
┌────────────────────────────────────────────────────────────┐
│ Opportunity Queue                                           │
│ - scored candidates                                         │
│ - route suggestion: workflow_a / workflow_b / drop           │
│ - source-backed reason                                      │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               v
┌────────────────────────────────────────────────────────────┐
│ Producer Orchestrator                                       │
│ - approves / rejects / holds candidates                     │
│ - chooses workflow                                          │
│ - chooses one platform lane                                 │
│ - sets priority                                             │
│ - creates ProducerDecision                                  │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               v
┌────────────────────────────────────────────────────────────┐
│ Brief Builder                                               │
│ - converts ProducerDecision into WriterSpec or VideoBrief   │
│ - preserves evidence boundaries                             │
│ - applies Jane voice/rubrics                                │
└──────────────────────────────┬─────────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              v                                 v
┌──────────────────────────────┐  ┌───────────────────────────┐
│ Workflow A — Video            │  │ Workflow B — Text          │
│ - hook development            │  │ - source-backed draft      │
│ - script generation           │  │ - Jane voice writing       │
│ - filming card                │  │ - final content asset      │
│ - NO publish queue            │  │ - NO platform variants     │
└──────────────┬───────────────┘  └──────────────┬────────────┘
               │                                  │
               └────────────────┬─────────────────┘
                                v
┌────────────────────────────────────────────────────────────┐
│ Editor / QA Gate                                            │
│ - source integrity                                           │
│ - factual safety                                             │
│ - Jane voice                                                 │
│ - generic AI style removal                                   │
│ - final approval for human review                            │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               v
┌────────────────────────────────────────────────────────────┐
│ Human Review Assets / Admin Operating Hub                   │
│ - final text assets                                          │
│ - video scripts / filming cards                              │
│ - approve / needs revision / archive                         │
│ - NO scheduling                                              │
│ - NO publishing                                              │
└────────────────────────────────────────────────────────────┘
```

---

## 3. Responsibilities by component

## 3.1 Research Agent — keep mostly unchanged

### Keep

Files from current system:

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

Research Agent continues to:

- check source compliance;
- collect public source data;
- select best-performing post/video;
- create canonical `SourceItem`;
- preserve raw payload;
- create evidence log;
- route item into `workflow_a`, `workflow_b`, `both`, or `drop`.

### Do not change

Do not let workflows perform search.  
Do not move compliance checks downstream.  
Do not let Analyst/Writer fetch live platform content.

### Optional improvement

Add persistent monitoring records if low-risk:

```text
source_scanned
selected_post_url
selected_post_metrics
collected_at
collector_errors
routing_decision
```

But this is secondary. The main task is the Producer/Brief/Editor refactor.

---

## 3.2 Analyst Entity — refactor to insight layer only

Current Analyst produces:

```text
SourceNote
InsightCard
ResearchHandoffRow
WriterSpec
ContentBrief
risk flags / preflight status
```

### New rule

Analyst should no longer create final writer-ready TZ directly for Writer.

Analyst should produce:

```text
SourceNote
InsightCard
ResearchHandoffRow
OpportunityCandidate
risk flags / preflight status
```

Move `WriterSpec` / `ContentBrief` creation to `Brief Builder`.

### Analyst should answer

```text
What happened outside?
Why did this source perform?
What theme/angle/emotion is inside?
Which Jane rubric/audience might fit?
What is the opportunity?
What are the risks?
Should this become workflow_a, workflow_b, both, or drop?
```

### Analyst should NOT answer

```text
Write this exact post.
Give final instructions to Writer.
Choose final production priority.
Approve production.
Create platform variants.
Schedule publication.
```

### Add model: OpportunityCandidate

Create or add to existing analyst/producer model layer:

```python
class OpportunityCandidate:
    opportunity_id: str
    source_item_id: str
    source_name: str
    source_type: str
    source_url: str
    topic: str
    core_idea: str
    jane_adaptation_brief: str
    audience_segment: str
    content_theme: str
    suggested_workflow: Literal["workflow_a", "workflow_b", "both", "drop"]
    suggested_platform: Optional[str]
    popularity_label: str
    public_metrics: dict
    what_performed: str
    emotional_trigger: str
    strategic_fit_score: float
    evidence_strength_score: float
    novelty_score: float
    production_complexity_score: float
    risk_level: Literal["low", "medium", "high"]
    risk_flags: list[str]
    analyst_reason: str
    created_at: datetime
```

Scoring can stay simple at first:

```text
opportunity_score =
  0.30 * evidence_strength_score
+ 0.25 * strategic_fit_score
+ 0.20 * novelty_score
+ 0.15 * audience_fit_score
- 0.10 * production_complexity_score
- risk_penalty
```

If existing score fields already exist, reuse them. Do not create unnecessary complexity.

### Files likely to modify

```text
src/content_engine/services/analyst.py
src/content_engine/llm/analyst.py
src/content_engine/models/workflow_b.py
src/content_engine/models/writer_entity.py
src/content_engine/models/source_item.py  # only if necessary, avoid if possible
```

### Tests to add/update

```text
tests/services/test_analyst_service.py
tests/llm/test_analyst.py
```

Acceptance:

- Analyst output includes OpportunityCandidate.
- Analyst still returns ResearchHandoffRow.
- Analyst no longer needs to create final WriterSpec for direct writer execution in the new pipeline.
- Existing old tests can pass via compatibility wrappers, but new pipeline must use OpportunityCandidate -> Producer -> BriefBuilder.

---

## 3.3 Producer Orchestrator — add new decision layer

### Purpose

Producer is the central orchestration layer. It decides what moves into production.

Producer receives Analyst opportunities and returns production decisions.

### Producer should answer

```text
Do we make this or drop it?
Which workflow should it enter?
What is the priority?
Which one platform lane should be used now?
What is the production intent?
What should Brief Builder create?
```

### Producer should NOT do

```text
Search.
Collect data.
Write final content.
Generate visuals.
Adapt to multiple platforms.
Schedule/publish.
```

### New files

```text
src/content_engine/models/producer.py
src/content_engine/services/producer.py
tests/services/test_producer_service.py
```

### New model: ProducerDecision

Use existing project style: Pydantic/dataclass depending on current codebase.

```python
class ProducerDecision:
    decision_id: str
    opportunity_id: str
    source_item_id: str
    decision: Literal["approve", "reject", "hold"]
    selected_workflow: Optional[Literal["workflow_a", "workflow_b"]]
    selected_platform: Optional[str]
    priority: Literal["low", "medium", "high", "urgent"]
    production_intent: str
    reason: str
    constraints: list[str]
    required_evidence: list[str]
    human_notes: Optional[str]
    created_at: datetime
```

### New model: ApprovedOpportunity

```python
class ApprovedOpportunity:
    approved_id: str
    decision_id: str
    opportunity_id: str
    source_item_id: str
    selected_workflow: Literal["workflow_a", "workflow_b"]
    selected_platform: str
    priority: str
    production_intent: str
    core_idea: str
    jane_adaptation_brief: str
    evidence_refs: list[str]
    risk_flags: list[str]
    created_at: datetime
```

### Default producer rules

Implement deterministic rules first. Do not make a new LLM dependency unless existing code already supports it cleanly.

Example decision logic:

```text
Reject if:
- risk_level == high and no human override
- source_url missing
- transcript/source_text too weak
- opportunity score below threshold
- source evidence missing

Hold if:
- evidence exists but source text is incomplete
- platform is unclear
- routing says both but priority is low

Approve if:
- evidence is strong
- Jane adaptation brief is concrete
- strategic/audience fit is sufficient
- risk is low/medium
```

Workflow choice:

```text
workflow_a if source is video-native or route == workflow_a
workflow_b if source is text/founder/market/lifestyle/expert signal
if route == both, choose exactly one workflow for now based on stronger fit
```

Platform choice:

```text
Choose one platform only.
Do not create variants.
Do not call Platform Adapter.
```

---

## 3.4 Brief Builder — add new TZ layer

### Purpose

Brief Builder converts an approved producer decision into a production-ready brief.

This is the missing layer between decision and writing.

### New files

```text
src/content_engine/models/brief_builder.py
src/content_engine/services/brief_builder.py
tests/services/test_brief_builder.py
```

### Inputs

```text
ApprovedOpportunity
OpportunityCandidate
ResearchHandoffRow
SourceItem / evidence refs
Jane rubrics / voice rules
Workflow route
```

### Outputs

For Workflow B:

```text
WriterSpec
ContentBrief
```

For Workflow A:

```text
VideoBrief / WorkflowABrief
```

If existing models already have `WriterSpec`, `ContentBrief`, or Workflow A input models, reuse them instead of inventing duplicates.

### Brief Builder should include

```text
brief_id
source_item_id
opportunity_id
decision_id
workflow
selected_platform
content_theme / rubric
audience_segment
production_intent
core_idea
angle
emotional_trigger
source_summary
source_text_excerpt
what_performed
jane_adaptation_instruction
factual_boundaries
must_include
must_not_include
tone_rules
opening_direction
quality_criteria
risk_flags
```

### Brief Builder must not include

```text
visual asset specs
carousel design instructions
multi-platform adaptation matrix
publish date
scheduled time
publisher assignment
```

### Important behavior

Brief Builder should transform this:

```text
Analyst: “This Bali legal risk post performed because it made invisible bureaucracy concrete.”
Producer: “Approve for Workflow B, Instagram, high priority, lived expert warning.”
```

Into this:

```text
WriterSpec:
- Write a Russian Instagram text in Jane's voice.
- Start with a concrete, non-generic opening.
- Use source-backed real estate/legal risk angle.
- Do not invent laws, prices, or personal events.
- Keep 1 thought / 1 emotion / 1 plot.
- No standalone CTA question.
```

---

## 3.5 Workflow A — keep video, remove publish queue

Current Workflow A does:

```text
1. Video intake
2. Hook development
3. Best hook selection
4. Script generation
5. Filming card generation
6. Publish queue preparation
7. Optional n8n/Telegram script_ready payload
```

### New Workflow A should do

```text
1. Receive VideoBrief from Brief Builder
2. Hook development
3. Best hook selection
4. Script generation
5. Filming card generation
6. Editor/QA handoff
7. Human Review Asset output
```

### Remove/disable

```text
Publish queue preparation
scheduled publishing fields
publisher/scheduler status
required n8n script_ready dispatch
```

Optional `n8n` notification can remain only if it is clearly not publishing/scheduling. It should be disabled by default and not required for core tests.

### Workflow A output should be

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

### Workflow A output should NOT include

```text
Publish Queue
Scheduled At
Publisher
Auto Publish Status
Distribution Status
```

### Files likely to modify

```text
src/content_engine/services/workflow_a.py
src/content_engine/models/workflow_a.py
src/content_engine/orchestration/video_gate.py
outputs/2026-04-27_workflow_a_only_video_run.md  # update example if needed
```

### Tests to update

```text
tests/services/test_workflow_a_pipeline.py
```

Acceptance:

- Workflow A tests no longer expect `Publish Queue`.
- Workflow A still produces hook, script, filming card.
- Workflow A final object is human-review-ready, not publish-ready.

---

## 3.6 Workflow B — keep text writing, remove platform adaptation variants

Current Workflow B phases:

```text
Phase 1 — Intake + Structure
Phase 2 — Extract
Phase 3 — Ideas
Phase 4 — Brief
Phase 5 — Draft
Phase 6 — Edit
Phase 7 — Review
```

### New Workflow B phases

```text
Phase 1 — Receive ContentBrief from Brief Builder
Phase 2 — Draft with Writer Entity
Phase 3 — Internal Writer self-edit if already implemented
Phase 4 — Editor / QA Gate
Phase 5 — Human Review Asset output
```

The old Analyst-heavy phases should move upstream:

```text
Research/SourceNote/Insight/Handoff -> Analyst
Opportunity choice -> Producer
Brief/TZ -> Brief Builder
```

Workflow B should no longer expand into multiple platform lanes.

### Remove/disable

```text
multi-platform lane expansion
platform adapter stage
format adaptation stage
visual adaptation stage
scheduled/published fields
```

### Keep

```text
Jane voice constraints
source-backed writing
no invented facts
no generic intros
no standalone CTA question
clean final asset format
LinkedIn English final rule only if selected_platform == LinkedIn
```

### Important LinkedIn policy

If selected platform is LinkedIn, keep current rule:

```text
LinkedIn publish version is English.
Internal working version can remain Russian.
```

But do not create additional Instagram/Telegram/TikTok variants in the same run.

### Files likely to modify

```text
src/content_engine/services/workflow_b.py
src/content_engine/models/workflow_b.py
src/content_engine/services/writer_entity.py
src/content_engine/models/writer_entity.py
src/content_engine/llm/writer.py
outputs/2026-04-27_workflow_b_final_jane_rubric_run.md
outputs/2026-04-28_research_to_analyst_handoff_run.md
```

### Tests to update

```text
tests/services/test_workflow_b_pipeline.py  # if exists
tests/services/test_writer_entity.py
tests/llm/test_writer.py
```

Acceptance:

- Workflow B receives a brief, not raw Analyst task.
- Workflow B produces one final asset per approved opportunity.
- No platform variants are generated.
- Final user-facing asset still uses clean format:

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

- Do not include final `Hook`, `CTA`, `Traceability`, or `QA` blocks in the user-facing asset.

---

## 3.7 Editor / QA Gate — add or refactor from Analyst review loop

Current system has:

```text
Analyst review loop before human review.
Maximum review passes: 3.
```

### New rule

Public architecture should expose this as:

```text
Editor / QA Gate
```

Internally it may reuse existing Analyst review logic, but responsibility should be renamed/centralized as editorial quality control.

### New files

```text
src/content_engine/models/editorial_gate.py
src/content_engine/services/editorial_gate.py
tests/services/test_editorial_gate.py
```

### Editor Gate should check

```text
source integrity
factual safety
Jane voice
opening strength
non-generic style
rubric fit
audience fit
one thought / one emotion / one plot
no invented facts
no unsupported claims
no banned generic intros
no standalone CTA question in Workflow B final text
```

### New model: EditorialReviewResult

```python
class EditorialReviewResult:
    review_id: str
    content_id: str
    source_item_id: str
    passed: bool
    approval_status: Literal["approved_for_human_review", "needs_revision", "rejected"]
    score: float
    failed_checks: list[str]
    revision_notes: list[str]
    factual_risk_flags: list[str]
    voice_risk_flags: list[str]
    review_pass_number: int
    created_at: datetime
```

### Review loop

Keep maximum review passes:

```text
max_review_passes = 3
```

Loop:

```text
Writer draft -> Editor Gate
if pass -> Human Review Asset
if fail and pass_count < 3 -> Writer revision
if fail after 3 -> Human Review Asset with needs_revision status and notes
```

### Important

Do not send failed drafts to Publisher/Scheduler because those layers do not exist in this stage.

---

## 3.8 Admin Operating Hub / Jane Superstar — show review assets only

Current target product surface:

```text
Admin Operating Hub / Jane Superstar interface
```

The handoff says Notion is no longer intended final destination. Keep that direction.

### Admin UI should show

```text
Research Monitor
Analyst Handoff
Opportunity Queue
Producer Decisions
Workflow A — Video Assets
Workflow B — Text Assets
Human Review Status
```

### Admin UI should NOT show for this stage

```text
Visual production section
Format adaptation section
Publisher section
Scheduler section
Scheduled posts
Auto publish status
Publishing queue
```

### Suggested status values

Use:

```text
new
analyzed
producer_approved
brief_ready
drafting
editorial_review
needs_revision
approved_for_human_review
archived
```

Do not use as active pipeline statuses:

```text
scheduled
published
auto_published
queued_for_publish
```

If UI currently has `copy / approve / filmed / published` states, adjust to:

```text
copy
approve
needs_revision
archived
```

For video, `filmed` can exist only as a manual human note outside the core generation pipeline. It must not trigger publishing/scheduling logic.

### Files likely to modify

```text
index.html
docs/handoffs/2026-04-27-jane-superstar-interface-outcome-handoff.md
outputs/latest/*.json  # create if missing
```

### Recommended output files

```text
outputs/latest/research_handoff.json
outputs/latest/opportunity_queue.json
outputs/latest/producer_decisions.json
outputs/latest/workflow_a_video_assets.json
outputs/latest/workflow_b_text_assets.json
outputs/latest/human_review_assets.json
```

---

## 4. New end-to-end orchestration command

The existing handoff recommends a stable local run command for `research -> analyst handoff`. Extend that idea into the new review-ready content factory run.

### Add one stable command

Suggested CLI:

```bash
python -m content_engine.cli run-content-factory --seed examples/seed_config.sample.yaml --output outputs/latest
```

If CLI package does not exist, add the smallest clean entrypoint possible.

### Pipeline pseudocode

```python
def run_content_factory(seed_config_path: str, output_dir: str) -> ContentFactoryRunResult:
    # 1. Research only here
    source_items = research_agent.run(seed_config_path)

    # 2. Analyst creates handoff + opportunity candidates
    analyst_result = analyst.analyze_sources(source_items)
    handoff_rows = analyst_result.research_handoff_rows
    opportunities = analyst_result.opportunity_candidates

    # 3. Producer approves/rejects/holds opportunities
    producer_decisions = producer.review_opportunities(opportunities)
    approved = [d.to_approved_opportunity() for d in producer_decisions if d.decision == "approve"]

    # 4. Brief Builder creates workflow-specific briefs
    briefs = brief_builder.build_many(approved, handoff_rows, source_items)

    # 5. Run chosen workflow
    raw_assets = []
    for brief in briefs:
        if brief.workflow == "workflow_a":
            raw_assets.append(workflow_a.run_from_brief(brief))
        elif brief.workflow == "workflow_b":
            raw_assets.append(workflow_b.run_from_brief(brief))

    # 6. Editor Gate reviews and loops revisions if needed
    human_review_assets = []
    for asset in raw_assets:
        reviewed_asset = editor_gate.review_with_revision_loop(asset, max_passes=3)
        human_review_assets.append(reviewed_asset)

    # 7. Write JSON + Markdown outputs
    write_json(output_dir / "research_handoff.json", handoff_rows)
    write_json(output_dir / "opportunity_queue.json", opportunities)
    write_json(output_dir / "producer_decisions.json", producer_decisions)
    write_json(output_dir / "workflow_a_video_assets.json", filter_video_assets(human_review_assets))
    write_json(output_dir / "workflow_b_text_assets.json", filter_text_assets(human_review_assets))
    write_json(output_dir / "human_review_assets.json", human_review_assets)

    return ContentFactoryRunResult(...)
```

### Do not include

```python
publisher.run(...)
scheduler.schedule(...)
visual_producer.generate(...)
platform_adapter.adapt(...)
```

---

## 5. State machine

Replace vague stage names with a clear internal state machine.

```text
captured_signal
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

Do not use in current active state machine:

```text
visual_production
format_adaptation
scheduled
published
queued_for_publish
```

If old code expects `processing_state`, map carefully:

```text
old: publish_queue_ready -> new: approved_for_human_review
old: scheduled -> deprecated / not emitted
old: published -> manual_external_status only, not pipeline state
```

---

## 6. Data contract summary

### 6.1 Keep existing SourceItem

Do not break existing `SourceItem` contract:

```text
item_id
source_type
source_name
source_url
external_item_id
collected_at
published_at
content_hash
dedupe_key
audience_segment
content_theme
raw_payload
transcript_text
media_urls
engagement_signals
routing_decision
routing_reason
routing_confidence
processing_state
```

### 6.2 Add/standardize these contracts

```text
ResearchHandoffRow       # already exists
OpportunityCandidate     # Analyst output
ProducerDecision         # Producer output
ApprovedOpportunity      # Producer-approved object for Brief Builder
ContentBrief / WriterSpec # Brief Builder output for Workflow B
VideoBrief               # Brief Builder output for Workflow A
EditorialReviewResult    # Editor Gate output
HumanReviewAsset         # final Admin Hub-ready output
```

### 6.3 HumanReviewAsset

```python
class HumanReviewAsset:
    content_id: str
    source_item_id: str
    opportunity_id: str
    decision_id: str
    brief_id: str
    workflow: Literal["workflow_a", "workflow_b"]
    platform: str
    title: str
    pillar: str
    audience_segment: str
    approval_status: Literal["approved_for_human_review", "needs_revision", "rejected"]
    final_text: Optional[str]
    selected_hook: Optional[str]
    script: Optional[str]
    filming_card: Optional[str]
    editor_score: float
    revision_notes: list[str]
    source_refs: list[str]
    created_at: datetime
```

### 6.4 Forbidden fields in new output JSON

The new pipeline should not emit these as active fields:

```text
publish_queue
scheduled_at
publisher
scheduler
visual_assets
visual_brief
format_variants
platform_variants
auto_publish_status
```

If they exist for legacy compatibility, they must be null/empty/deprecated and not shown in Admin UI.

---

## 7. File-level implementation plan

### 7.1 Add

```text
src/content_engine/models/producer.py
src/content_engine/services/producer.py
src/content_engine/models/brief_builder.py
src/content_engine/services/brief_builder.py
src/content_engine/models/editorial_gate.py
src/content_engine/services/editorial_gate.py
src/content_engine/models/content_factory.py
src/content_engine/services/content_factory.py
```

Optional CLI files depending on existing structure:

```text
src/content_engine/cli.py
src/content_engine/cli/run_content_factory.py
```

Tests:

```text
tests/services/test_producer_service.py
tests/services/test_brief_builder.py
tests/services/test_editorial_gate.py
tests/services/test_content_factory_pipeline.py
```

### 7.2 Modify

```text
src/content_engine/services/analyst.py
src/content_engine/llm/analyst.py
src/content_engine/services/workflow_a.py
src/content_engine/models/workflow_a.py
src/content_engine/services/workflow_b.py
src/content_engine/models/workflow_b.py
src/content_engine/services/writer_entity.py
src/content_engine/models/writer_entity.py
src/content_engine/llm/writer.py
index.html
```

### 7.3 Update docs/examples

```text
docs/handoffs/2026-04-27-jane-superstar-interface-outcome-handoff.md
outputs/2026-04-27_workflow_a_only_video_run.md
outputs/2026-04-27_workflow_b_final_jane_rubric_run.md
outputs/2026-04-28_research_to_analyst_handoff_run.md
```

Create:

```text
outputs/latest/research_handoff.json
outputs/latest/opportunity_queue.json
outputs/latest/producer_decisions.json
outputs/latest/workflow_a_video_assets.json
outputs/latest/workflow_b_text_assets.json
outputs/latest/human_review_assets.json
```

### 7.4 Remove/disable references

Search codebase for:

```text
Publish Queue
publish_queue
scheduled
scheduler
publisher
platform_adapter
format_adapter
visual
visual_asset
visual_brief
platform_variants
format_variants
```

For each found reference:

- remove if obsolete;
- rename if it means human review;
- mark deprecated if needed for tests/backward compatibility;
- ensure new pipeline does not call it.

---

## 8. Migration strategy

### Step 1 — Add models without changing pipeline

Add:

```text
OpportunityCandidate
ProducerDecision
ApprovedOpportunity
BriefBuilder output models
EditorialReviewResult
HumanReviewAsset
```

Run tests.

### Step 2 — Make Analyst emit OpportunityCandidate

Keep old output if needed for backwards compatibility, but new pipeline must consume `OpportunityCandidate`.

Run Analyst tests.

### Step 3 — Add Producer service

Add deterministic approval/reject/hold logic.

Run Producer tests.

### Step 4 — Add Brief Builder service

Move WriterSpec/ContentBrief creation out of Analyst path.

Run Brief Builder tests.

### Step 5 — Refactor Workflow B to accept brief

Workflow B should not start from raw source item or Analyst task in the new pipeline.

Run Writer and Workflow B tests.

### Step 6 — Refactor Workflow A to accept brief and remove publish queue

Keep video script/filming card. Remove publish queue output.

Run Workflow A tests.

### Step 7 — Add Editor Gate

Refactor existing Analyst review loop into editorial gate architecture.

Run editor tests.

### Step 8 — Add end-to-end content factory run

Add service/CLI that writes JSON outputs.

Run integration-style test with fixture SourceItems.

### Step 9 — Update Admin UI

Wire latest JSON arrays or embedded sample arrays into `index.html`.

Remove visual/publisher/scheduler sections.

### Step 10 — Full verification

Run:

```bash
PYTHONPATH=. pytest -q
python3 -m mypy src
```

Expected:

```text
all tests pass
mypy: no issues
```

---

## 9. Acceptance criteria

### Architecture acceptance

- Research Agent remains the only collection/search layer.
- Analyst creates insight/opportunity, not direct writer orders.
- Producer exists and approves/rejects/holds opportunities.
- Brief Builder exists and creates WriterSpec/VideoBrief.
- Workflow A and Workflow B receive briefs.
- Editor Gate exists before human review.
- Admin Hub receives human-review-ready assets only.

### Removal acceptance

New pipeline does not include:

- Visual Producer;
- Format Adapter;
- Platform Adapter;
- Publisher;
- Scheduler;
- Publish Queue;
- scheduled publishing;
- auto publishing;
- multi-platform variants.

### Output acceptance

Generated outputs include:

```text
outputs/latest/research_handoff.json
outputs/latest/opportunity_queue.json
outputs/latest/producer_decisions.json
outputs/latest/workflow_a_video_assets.json
outputs/latest/workflow_b_text_assets.json
outputs/latest/human_review_assets.json
```

Workflow A final markdown does not include:

```text
Publish Queue
Scheduled At
Publisher
```

Workflow B final markdown keeps:

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

Workflow B final markdown does not include:

```text
Hook block
CTA block
Traceability block
QA block
```

Internal JSON may include traceability/source refs.

### Quality acceptance

- No invented facts outside source transcript/evidence.
- Jane voice rules remain enforced.
- Generic openings remain banned.
- Workflow B final text has no standalone CTA question.
- Editor Gate max revision passes: 3.
- Failed after 3 passes returns `needs_revision`, not publish-ready.

---

## 10. Codex prompt

Use this exact task prompt for Codex:

```text
You are working in repository `Je Pro Agent`, branch `codex/content-engine-core`.

Implement a restructuring of the current content engine into this target flow:

Approved Sources -> Research Agent -> SourceItem + Evidence Log -> Analyst Entity -> Opportunity Queue -> Producer Orchestrator -> Brief Builder -> Workflow A / Workflow B -> Editor / QA Gate -> Human Review Assets -> Jane Superstar Admin Hub.

Hard constraints:
1. Research Agent remains the only layer allowed to search or collect data.
2. Analyst must no longer directly command Writer or create final writer-ready tasks in the new pipeline.
3. Add Producer as the decision layer that approves/rejects/holds opportunities.
4. Add Brief Builder as the TZ/brief layer that creates WriterSpec for Workflow B and VideoBrief for Workflow A.
5. Add or refactor Editor / QA Gate before human review.
6. Remove/disable Visual / Format / Adaptation from the active pipeline.
7. Remove/disable Publisher / Scheduler from the active pipeline.
8. Workflow A must keep hook/script/filming card but remove Publish Queue.
9. Workflow B must produce one source-backed final asset per approved opportunity, not multi-platform variants.
10. Admin UI/output JSON should show human-review-ready assets only, with no scheduler/publisher/visual sections.

Add models/services/tests for:
- OpportunityCandidate
- ProducerDecision
- ApprovedOpportunity
- Brief Builder outputs
- EditorialReviewResult
- HumanReviewAsset

Update existing Analyst, Workflow A, Workflow B, Writer Entity, and Admin UI to use the new flow.

Do not break existing SourceItem evidence contract.
Do not rebuild Notion.
Do not add auto-publishing.
Do not add visual generation.
Do not add multi-platform adaptation.

Run:
PYTHONPATH=. pytest -q
python3 -m mypy src

Return a concise implementation summary with changed files and any remaining gaps.
```

---

## 11. Minimal implementation if Codex needs to avoid overbuilding

If Codex cannot implement full refactor in one pass, do the minimal viable version:

1. Add `ProducerDecision` and `producer.py`.
2. Add `BriefBuilder` service.
3. Make Analyst output `OpportunityCandidate`.
4. Make Workflow B accept `ContentBrief` from Brief Builder.
5. Remove `Publish Queue` from Workflow A output.
6. Add `HumanReviewAsset` output JSON.
7. Update tests.

Do not start with Admin UI redesign if backend contracts are not stable yet.

The highest-value change is this:

```text
Analyst -> OpportunityCandidate -> ProducerDecision -> BriefBuilder -> Writer/Workflow
```

That single change fixes the architecture.

---

## 12. Final target in one sentence

The system should become a source-backed, producer-orchestrated content factory where Research finds evidence, Analyst extracts opportunities, Producer chooses what to make, Brief Builder creates clean TZ, Writer/Video workflows produce assets, Editor approves quality, and Jane reviews final content manually — with no visual production, no platform adaptation, no scheduler, and no publisher in this stage.
