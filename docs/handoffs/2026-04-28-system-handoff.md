# Jane Superstar / Je Pro Agent — Full System Handoff

**Date:** 2026-04-28  
**Repository:** `Je Pro Agent`  
**Current branch:** `codex/content-engine-core`  
**Purpose:** explain the full current system so another GPT, developer, or product designer can continue work without re-discovering architecture.

---

## 1. Short Summary

This project is a standalone content operating system for Jane Levitan / Jane Superstar.

The system has one main rule:

**Research Agent is the only layer that searches and collects data. Workflows do not search. They only process prepared source items.**

Current system path:

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
  -> Admin Operating Hub-ready final outputs
```

The system does **not** publish automatically. It prepares content, scripts, filming cards, and final text assets. Human review and manual publication remain required.

---

## 2. Current Product Goal

Build a content engine that helps Jane create a repeatable blog/content system from sources that already perform well.

The engine should:

- monitor approved Instagram, Telegram, TikTok, YouTube, LinkedIn, and web sources
- detect which posts or videos performed best using public metrics
- extract source URL, text, caption, topic, metrics, and source evidence
- route video-native signals into Workflow A
- route market/founder/text signals into Workflow B
- turn source-backed insights into writer-ready briefs
- generate video scripts and text content in Jane's tone
- expose ready outputs in a future admin interface named **Jane Superstar**

---

## 3. Main System Components

### 3.1 Research Agent

Primary files:

- `src/content_engine/orchestration/search_agent.py`
- `src/content_engine/collectors/native.py`
- `src/content_engine/collectors/apify.py`
- `src/content_engine/knowledge/research_dependencies.py`
- `.agents/skills/research-agent-runner/SKILL.md`
- `.agents/skills/compliance-gate-skill/SKILL.md`
- `.agents/skills/evidence-log-skill/SKILL.md`
- `.agents/skills/routing-skill/SKILL.md`

What it does:

- checks whether a target source is safe to collect
- collects public pages / feeds / actor-backed source data
- chooses the best-performing post from monitored sources
- stores raw source evidence in `SourceItem`
- builds evidence logs before downstream handoff
- routes each item into `workflow_a`, `workflow_b`, `both`, or `drop`

Current collector support:

| Platform | Current behavior |
|---|---|
| Telegram | Reads public `t.me/s/...` pages, extracts recent posts, text, views, post URL, selects best-performing post by engagement score. |
| Instagram | Uses Apify profile fallback for profile monitoring, selects best post/reel from `latestPosts`, extracts caption, URL, media, likes/comments/views, optional carousel/image text if actor provides it. |
| TikTok | Tries public page payload first; if unavailable, uses Apify `clockworks/tiktok-scraper`, selects best video by views/likes/comments/shares/saves. |
| YouTube | Reads RSS feeds, extracts video title, description, thumbnail, views/ratings when available. |
| Web | Extracts metadata / JSON-LD from public articles, reports, and web pages. |
| LinkedIn | Compliance is modeled, but robust native profile/post collection is not yet implemented. |

Best-performing post rule:

```text
engagement_score =
  likes
  + comments * 4
  + shares * 5
  + saves * 5
  + views * 0.02
  + video_views * 0.02
  + ratings * 0.5
```

Comments, saves, and shares are stronger signals than passive views.

---

## 4. Canonical Source Contract

Every collected source becomes a `SourceItem`.

Primary file:

- `src/content_engine/models/source_item.py`

Required fields:

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

Important rules:

- `raw_payload` is treated as immutable evidence.
- `transcript_text` is the normalized source text used by analyst/writer layers.
- `engagement_signals` are public metrics only.
- `source_url`, timestamp, raw excerpt, and confidence are required before downstream use.
- If public/API extraction includes `carousel_text`, `image_text`, `ocrText`, or equivalent fields, they are preserved for Analyst handoff.

---

## 5. Source Pools And Rubrics

Primary files:

- `examples/seed_config.sample.yaml`
- `src/content_engine/context/jane_blog_rubrics.py`
- `src/content_engine/context/workflow_b_rules.py`

Audience segments:

- `developer_investor`
- `broker`
- `architect_designer`
- `lifestyle_expat`
- `dreamer_woman`

Canonical content themes:

- `founder_journey`
- `expert_pain_bali`
- `land_and_legal`
- `market_reports`
- `bali_travel`
- `global_trends`
- `wellness_architecture`
- `boutique_hotels`
- `marketing_cases`

Jane blog rubrics:

| Rubric | Meaning |
|---|---|
| `#bali life` | New places, hotels, restaurants, art, events, Bali news in context. |
| `lifestyle` | Jane's personal Bali life and lived experience. |
| `#недвижка` | Bali real estate, land, market, legal, investment risks. |
| `#отношения` | Husband/business partner, family, child, motherhood, partnership. |
| `#заметки фаундера` | Business, founder lessons, psychology, money, not burning out. |
| `#experience` | Art/wellness/hospitality/business experiences and global examples. |

Core content rule:

```text
1 thought / 1 emotion / 1 plot
anchor or intrigue -> story or context -> conclusion
every Instagram post should feel like an info occasion inside a recurring rubric
```

---

## 6. Workflow A — Video

Primary files:

- `src/content_engine/services/workflow_a.py`
- `src/content_engine/models/workflow_a.py`
- `src/content_engine/orchestration/video_gate.py`
- `.agents/skills/video-intake-skill/SKILL.md`
- `.agents/skills/hook-mining-skill/SKILL.md`
- `outputs/2026-04-27_workflow_a_only_video_run.md`

Workflow A receives video-native material from Research Agent.

It currently does:

1. Video intake
2. Hook development
3. Best hook selection
4. Script generation
5. Filming card generation
6. Publish queue preparation
7. Optional n8n/Telegram `script_ready` payload

Workflow A output shape:

```text
Title
Platform
Audience
Theme
Status
Selected Hook
Script
Filming Card
Publish Queue
Caption
```

Important product decision:

- There is no separate publish gate for auto-publishing.
- Human films manually.
- Human publishes manually.
- The system prepares scripts and filming assets only.

---

## 7. Workflow B — Content Farm / Text

Primary files:

- `src/content_engine/services/analyst.py`
- `src/content_engine/llm/analyst.py`
- `src/content_engine/services/writer_entity.py`
- `src/content_engine/models/writer_entity.py`
- `src/content_engine/services/workflow_b.py`
- `src/content_engine/models/workflow_b.py`
- `src/content_engine/llm/writer.py`
- `outputs/2026-04-27_workflow_b_final_jane_rubric_run.md`
- `outputs/2026-04-28_research_to_analyst_handoff_run.md`

Workflow B receives text-heavy, founder, market, expert, or lifestyle signals.

Current phases:

```text
Phase 1 — Intake + Structure
  normalize source item into SourceNote
  dedupe
  preserve source evidence

Phase 2 — Extract
  Analyst extracts topic, angle, emotional trigger, audience fit, useful lesson
  Analyst builds ResearchHandoffRow

Phase 3 — Ideas
  Theme and platform decisions expand into one or more platform lanes

Phase 4 — Brief
  Analyst creates WriterSpec / TZ for each lane

Phase 5 — Draft
  Writer Entity generates text from source-backed brief

Phase 6 — Edit
  Writer Entity / editor checks opening, tone, factual safety, Jane voice

Phase 7 — Review
  Analyst review loop before human review
```

Workflow B final asset format:

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

Do not include final `Hook`, `CTA`, `Traceability`, or `QA` blocks in user-facing Workflow B final assets.

LinkedIn policy:

- LinkedIn publish version is English.
- Internal working version stays Russian.
- When LinkedIn final output exists, it can include an internal Russian master version for admin review.

---

## 8. Analyst Entity

Primary files:

- `src/content_engine/services/analyst.py`
- `src/content_engine/llm/analyst.py`
- `scripts/start_codex_analyst.sh`
- `.codex/agents/analyst_entity.md`

The Analyst Entity is the bridge between Research Agent and Writer Entity.

It currently produces:

- `SourceNote`
- `InsightCard`
- `ResearchHandoffRow`
- `WriterSpec`
- `ContentBrief`
- risk flags / preflight status

`ResearchHandoffRow` is the latest important addition. It contains:

```text
source_name
source_type
post_url
topic
public_metrics
metrics_summary
popularity_label
what_performed
source_text
carousel_or_image_text
core_idea
jane_adaptation_brief
```

Purpose:

- show what Research found
- explain why the post performed
- preserve source text
- give Writer a source-backed adaptation task
- avoid generic writing from raw topics

Current Analyst LLM rule:

- Working fields should be returned in Russian.
- Enum labels remain as required.
- No invented facts outside source transcript.

---

## 9. Writer Entity

Primary files:

- `src/content_engine/services/writer_entity.py`
- `src/content_engine/models/writer_entity.py`
- `src/content_engine/llm/writer.py`
- `writer_entity_combined_technical_spec.md` if present locally as source reference

Writer Entity role:

- generate source-backed content in Jane's tone
- avoid generic AI style
- preserve factual boundaries
- produce final clean assets
- review and edit draft before final output

Jane voice constraints include:

- no generic intros like `Сегодня поговорим...`, `Давайте разберёмся...`, `В современном мире...`
- no standalone CTA question in Workflow B final text
- no tautological opening lines
- first sentence should be unique, concrete, source-specific, and strong
- final text should start directly with the opening sentence, not with a separate hook block
- text should feel like lived expertise, not an abstract advice post

Analyst review loop:

- Analyst checks Writer result before human review.
- If the result fails rubric/audience/source checks, it goes back to Writer.
- Maximum review passes: 3.
- If it passes earlier, return immediately.

---

## 10. Storage And Output Layer

Current intended product direction:

**Admin Operating Hub / Jane Superstar interface is the target output layer. Notion is no longer the intended final destination.**

What exists now:

- static interface file: `index.html`
- final interface handoff: `docs/handoffs/2026-04-27-jane-superstar-interface-outcome-handoff.md`
- generated output examples in `outputs/`
- KMD source materials in `outputs/..._kmd/` and `knowledge/kmd` when configured

Legacy / still present in code:

- `src/content_engine/notion/*`
- `NotionClientLike`
- `InMemoryNotionClient`
- Notion-shaped database IDs in test/dry-run targets

How to interpret this:

- Notion adapters are still useful as old persistence contracts and test doubles.
- They should not be treated as the future product surface.
- Future work should write Admin Hub-ready data structures and UI files, not rebuild Notion as the main output.

---

## 11. Integrations And Environment

Required env variables for live integrations:

```text
ANTHROPIC_API_KEY
ANTHROPIC_MODEL
APIFY_TOKEN
FIRECRAWL_API_KEY
EXA_API_KEY
N8N_WEBHOOK_URL
CONTENT_ENGINE_KMD_ROOT
```

Do not commit real secret values.

Current integration roles:

| Integration | Role |
|---|---|
| Anthropic | Analyst and Writer LLM brain. |
| Apify | Instagram profile collection and TikTok actor-backed collection. |
| Firecrawl | Web search/scrape integration path and future deeper web extraction. |
| Exa | Source discovery, competitor/source expansion. |
| Playwright | Rendered public pages / fallback when static extraction is insufficient. |
| n8n | Optional script-ready dispatch for Workflow A; not required for core tests. |

---

## 12. Admin Interface Direction — Jane Superstar

The frontend should show final user-facing outcomes only.

Do show:

- Workflow A video assets
- Workflow B final content assets
- source-backed research handoff rows if building an internal analyst dashboard
- copy / approve / filmed / published states
- filters by platform/status/search

Do not show in the main final-output interface:

- internal pipeline mechanics
- analyst matrices
- traceability blocks
- QA blocks
- legacy Notion setup
- raw backend implementation details

Recommended product sections:

| Section | Purpose |
|---|---|
| Research Monitor | Shows selected best-performing posts and why they were selected. |
| Analyst Handoff | Shows topic, idea, source text, metrics, and Jane adaptation brief. |
| Workflow A — Video | Shows hooks, scripts, filming cards, publish queue. |
| Workflow B — Text | Shows final content assets and internal RU master when needed. |
| Analytics / Feedback | Later: post performance, what themes/hooks to boost back into Research Agent. |

---

## 13. Current Live Run Evidence

Latest Research -> Analyst handoff output:

- `outputs/2026-04-28_research_to_analyst_handoff_run.md`

It contains 7 live rows:

- TorbosovLife
- Bali_expert
- Wellstate
- Anna Lutaeva
- Ksenia ASAP
- Baligasm TikTok
- Realinfo Market Reports

Example row fields:

```text
Источник
Платформа
Пост
Метрики
Популярность
Тема
Идея
Исходный текст
Карусель/OCR
Адаптированный текст для Writer
```

Known limitation:

- carousel/OCR is supported by the data contract, but only appears when the upstream API/actor returns it.
- In the latest live run, carousel/OCR was not available for the selected sources.

---

## 14. Tests And Verification

Project test command:

```bash
PYTHONPATH=. pytest -q
```

Typecheck command:

```bash
python3 -m mypy src
```

Most recent verified state before this handoff:

```text
297 passed
mypy: no issues found in 62 source files
```

Key test groups:

- `tests/collectors/test_native_collectors.py`
- `tests/orchestration/test_search_agent.py`
- `tests/services/test_analyst_service.py`
- `tests/services/test_workflow_a_pipeline.py`
- `tests/services/test_writer_entity.py`
- `tests/llm/test_analyst.py`
- `tests/llm/test_writer.py`
- `tests/config/test_research_agent_skill_contracts.py`

---

## 15. What Is Done

- Standalone repo structure is created.
- Core source models exist.
- Native collectors exist for Telegram, Instagram, TikTok, YouTube, and web metadata.
- Instagram profile monitoring uses Apify fallback.
- TikTok profile monitoring uses Apify fallback when public HTML does not expose usable payload.
- Best-performing post selection exists.
- Evidence log checks exist.
- Routing exists.
- Workflow A video pipeline exists.
- Workflow B analyst/writer pipeline exists.
- Jane rubrics and audience/story rules are encoded.
- Writer Entity has Jane voice, opening, QA, and privacy constraints.
- Research -> Analyst handoff rows exist.
- Static Jane Superstar interface exists as a local-only `index.html`.
- Tests pass.

---

## 16. Known Gaps / Next Work

High priority:

- Build a first real Admin Operating Hub data model that is not Notion-shaped.
- Connect ResearchHandoffRow, Workflow A assets, and Workflow B final assets to the Jane Superstar interface data arrays or local JSON.
- Add a CLI command for collector-only and Research -> Analyst handoff runs so we stop using one-off scripts.
- Add persistent monitoring run records: source scanned, selected post, metrics, timestamp, errors.

Medium priority:

- Add robust LinkedIn public collection strategy or explicitly mark LinkedIn manual-only until approved tooling exists.
- Improve carousel/OCR extraction for Instagram only if the chosen Apify actor reliably returns image text.
- Add Firecrawl/Exa discovery runs for finding similar sources and posts.
- Convert source discovery candidates into an approval queue before Monitoring List.
- Add analytics feedback loop from published performance back into Research Agent source/theme scoring.

Low priority:

- Clean or archive legacy Notion docs/adapters after Admin Hub storage is finalized.
- Add a richer browser-based admin UI with import/export of local JSON state.
- Add scheduled automation once the stable run command exists.

---

## 17. Practical Commands

Run all tests:

```bash
PYTHONPATH=. pytest -q
```

Run mypy:

```bash
python3 -m mypy src
```

Start Codex Analyst Entity:

```bash
scripts/start_codex_analyst.sh
```

Open local interface:

```text
/Users/vasini/Downloads/Je Pro Agent /index.html
```

Latest useful output file:

```text
/Users/vasini/Downloads/Je Pro Agent /outputs/2026-04-28_research_to_analyst_handoff_run.md
```

---

## 18. Recommended Next Step

The best next implementation step is:

**Create a stable local run command for `research -> analyst handoff` that writes JSON + Markdown outputs, then wire that JSON into the Jane Superstar admin interface.**

Reason:

- Research collection now works.
- Analyst handoff rows now work.
- Workflow A/B outputs exist.
- The missing bridge is a clean product-facing data contract for the admin UI.

Recommended output files for that next step:

```text
outputs/latest/research_handoff.json
outputs/latest/workflow_a_video_assets.json
outputs/latest/workflow_b_text_assets.json
```

Then `index.html` can load or embed those arrays and become the real review hub.

