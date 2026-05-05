# Jane Superstar Content Factory — системный handoff

**Дата:** 2026-04-30
**Статус:** current snapshot / актуальная передача контекста
**Назначение:** быстро передать следующему агенту, разработчику или GPT, как сейчас устроена система, что уже сделано, какие правила нельзя ломать и что делать дальше.
**Важно:** этот handoff является снимком состояния. Если он конфликтует с `AGENTS.md`, `docs/README.md`, `docs/architecture/` или `docs/decisions/`, побеждают canonical docs.

## 1. Быстрый reading order

Новый агент должен читать в таком порядке:

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/architecture/2026-04-29-content-factory-producer-restructure.md`
4. `docs/architecture/2026-04-29-producer-agent-entity.md`
5. `docs/architecture/2026-04-30-producer-output-contract.md`
6. `docs/runbooks/validation-and-deploy.md`
7. Этот handoff

Не восстанавливать текущую архитектуру из чатов, старых outputs или старых root-файлов. Durable rules должны жить в `docs/architecture`, `docs/decisions` или `docs/runbooks`.

## 2. Текущий продуктовый смысл

Мы строим **Jane Superstar Content Factory**: систему, где контент Джейн создаётся не случайными постами, а продюсерской цепочкой.

Главная идея:

```text
человеческий сезонный seed
  -> продюсерская стратегия
  -> поиск доказательных источников
  -> аналитика
  -> opportunity queue
  -> решение продюсера
  -> brief builder
  -> Workflow A или Workflow B
  -> редакторская проверка
  -> human review asset
  -> будущая админка Jane Superstar
```

Система не должна автоматически публиковать контент. Она готовит материалы для ручного ревью и дальнейшей работы.

## 3. Canonical pipeline

Актуальный target flow:

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

Readable ProducerOutput существует отдельно:

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

Readable ProducerOutput нужен для клиента, продюсера и будущего интерфейса. Runtime `ProducerOutput` остаётся машинным контрактом.

## 4. Нельзя ломать

- Research Agent остаётся единственным слоем поиска, scraping, crawling и collection.
- Producer может ставить задачи Research Agent, но не собирает данные сам.
- Analyst анализирует source-backed данные и создаёт opportunity, но не командует Writer напрямую в новой цепочке.
- Brief Builder является единственным слоем, который превращает approved opportunity в Writer/Video task.
- Workflow A и Workflow B полностью разделены.
- Workflow A создаёт только video hook, script, filming card.
- Workflow A hook research идёт только через `ProducerHookSearchTask -> HookResearchOutcomeBoard`; без task Research Agent возвращает `BLOCKED`.
- Workflow A hook research должен сканировать минимум 50 релевантных публичных видео за loop и сохранять реальные public video URLs + observed metrics.
- Workflow B создаёт один final text asset на approved opportunity и selected platform.
- LinkedIn: publish text на английском, internal RU master может существовать для ревью.
- Нет активного Publisher, Scheduler, Auto-publishing, publish queue, visual producer, platform adapter или format adapter.
- `Manual Publishing / Calendar` в readable ProducerOutput — это только ручное планирование, не runtime-сервис.
- Source evidence сохраняется internally, но final user-facing assets должны быть чистыми.
- Editor / QA Gate имеет максимум 3 прохода перед human review handoff.
- Не коммитить secrets. Все ключи только через `.env` / runtime env.

## 5. Главные сущности

### Research Agent

Назначение:

- получает Producer ResearchDirective или seed/source список;
- для Workflow A hook research требует `ProducerHookSearchTask`;
- проверяет compliance;
- собирает только public data;
- выбирает high-performing posts/signals;
- для Workflow A ищет по Producer brief на TikTok / Instagram / YouTube / Shorts и approved public video sources;
- для Workflow A hook research валидирует ровно 50-video set по платформам: YouTube 15, TikTok 15, Instagram 20;
- short-form является дефолтом: Reels / TikTok / YouTube Shorts / vertical 9:16, обычно <= 180 секунд;
- long educational YouTube допускается только как support, максимум 5 из 50;
- перед hook mining применяет minimum analysis gate: views alone не считаются доказательством залёта;
- ранжирует видео по public engagement score: `likes + comments*4 + shares*5 + saves*5 + views*0.02 + video_views*0.02`;
- для research-mined hook rows сохраняет `source_video_url`, observed hook/opening, first-frame text, public metrics, engagement score/rank, scan batch size и selection reason;
- создаёт `SourceItem` и evidence fields;
- маршрутизирует сигнал в Workflow A, Workflow B, both или drop.
- создаёт `HookResearchOutcomeBoard` только для producer-directed hook research.

Ключевые файлы:

- `src/content_engine/orchestration/search_agent.py`
- `src/content_engine/collectors/native.py`
- `src/content_engine/collectors/apify.py`
- `src/content_engine/collectors/http_json.py`
- `.agents/skills/research-agent-runner/SKILL.md`
- `.agents/skills/source-discovery-skill/SKILL.md`
- `.agents/skills/compliance-gate-skill/SKILL.md`
- `.agents/skills/evidence-log-skill/SKILL.md`
- `.agents/skills/routing-skill/SKILL.md`

MCP / external stack policy:

- Exa for discovery and competitor expansion.
- Firecrawl for search + clean scrape.
- Apify for actor-backed platform collection.
- Playwright for rendered public pages / interaction fallback.

Нужные env vars:

- `FIRECRAWL_API_KEY`
- `APIFY_TOKEN`
- `EXA_API_KEY` if configured
- `ANTHROPIC_API_KEY` for writer/LLM layers

Не записывать реальные ключи в код, docs или git.

### Producer Agent

Назначение:

- принимает human season seed;
- создаёт `ProducerBrief`, `SeasonBible`, `EpisodePlan[]`, `SceneCard[]`;
- создаёт `ResearchDirective[]`;
- после Analyst review принимает решения по `OpportunityCandidate`;
- создаёт `ProducerDecision` и `ApprovedOpportunity`;
- сохраняет `SeriesMemory`;
- создаёт readable ProducerOutput для клиента/интерфейса.

Ключевые файлы:

- `src/content_engine/models/producer.py`
- `src/content_engine/services/producer.py`
- `src/content_engine/models/producer_output_contract.py`
- `src/content_engine/services/producer_output_contract.py`
- `.codex/agents/producer_entity.md`
- `docs/architecture/2026-04-29-producer-agent-entity.md`
- `docs/architecture/2026-04-30-producer-output-contract.md`

Важно:

- Producer не пишет финальные посты.
- Producer не пишет видеоскрипты.
- Producer не ищет и не скрейпит источники.
- Producer не публикует и не планирует публикации автоматически.

### Analyst Entity

Назначение:

- принимает `SourceItem`;
- делает Phase 1: intake, structure, normalization, dedupe, source note;
- делает Phase 2: insight extraction;
- создаёт structured insight / opportunity для продюсера;
- готовит ТЗ дальше по цепочке только через новую opportunity/brief chain.

Ключевые файлы:

- `src/content_engine/llm/analyst.py`
- `src/content_engine/services/analyst.py`
- `.codex/agents/analyst_entity.md`
- `.agents/skills/insight-extraction-skill/SKILL.md`

Важно:

- Analyst не должен напрямую обходить Producer + Brief Builder.
- Analyst не пишет финальные тексты.
- Video hooks/scripts не принадлежат Workflow B.

### Opportunity Queue

Назначение:

- получает `OpportunityCandidate[]`;
- сортирует и дедуплицирует;
- применяет scoring;
- передаёт Producer для approve / hold / reject.

Ключевые файлы:

- `src/content_engine/models/opportunity.py`
- `src/content_engine/services/opportunity_queue.py`
- `tests/services/test_opportunity_queue.py`

### Brief Builder

Назначение:

- превращает `ApprovedOpportunity` в один из двух brief types:
- `WorkflowABrief` для видеоворкфлоу;
- `WorkflowBBrief` для текстового воркфлоу.
- превращает `ApprovedWorkflowAHandoff` из `HookResearchOutcomeBoard` в `WorkflowABrief`.
- переносит Producer scene context, если есть `SceneCard`:
- `producer_scene_type`;
- `producer_plot_function`;
- `producer_sales_intensity`;
- `producer_scene_hook`;
- `producer_cta_or_next_hook`.

Ключевые файлы:

- `src/content_engine/models/brief_builder.py`
- `src/content_engine/services/brief_builder.py`
- `tests/models/test_brief_builder_models.py`
- `tests/services/test_brief_builder.py`

Важно:

- Brief Builder не создаёт platform variants.
- Brief Builder не создаёт publish dates / scheduler / publisher fields.
- Brief Builder должен сохранять factual boundaries и evidence refs.
- Brief Builder должен переносить public `source_video_url` из `ApprovedWorkflowAHandoff.source_context` в `WorkflowABrief.video_refs`.
- Brief Builder должен отклонять route mismatch между `ApprovedOpportunity` и `ProducerDecision`.
- `SceneCard` должен совпадать по `scene_id` / `episode_id`; иначе brief не создаётся.
- Hook rows проходят в Workflow A только если `human_decision = APPROVE_FOR_WORKFLOW_A`, `qa_status = PASS`, risk acceptable.
- Research-mined hook rows проходят в Workflow A только если есть public source video URL, observed hook/first frame, public metrics, engagement score/rank, scan batch size >= 50 и selection reason.
- Research-mined hook rows также должны пройти minimum analysis gate: `BROAD_VIRAL`, `NICHE_VIRAL`, `STRONG_DISCUSSION`, `HIGH_VALUE_SIGNAL` или `SMALL_ACCOUNT_BREAKOUT`.

### HookResearchOutcomeBoard

Назначение:

- human-facing board для producer-directed hook research;
- показывает Producer task, research scope, source evidence, hook opportunities, expanded hook cards, QA, approved handoffs;
- не является viral hook bank;
- не создаёт scripts, filming cards, publish queue, scheduler или final captions.
- блокируется, если `search_summary.sources_scanned` меньше `ProducerHookSearchTask.source_count_target`.
- блокируется, если `platform_scan_counts` не равен `youtube=15, tiktok=15, instagram=20`.
- блокируется, если `format_scan_counts.long_form > 5` или `format_scan_counts.short_form < 45`.
- блокируется, если source evidence использует internal refs вместо public video URLs.
- блокируется, если research-mined video не проходит minimum analysis gate:
- keep: `views >= 100000 AND like_rate >= 2%`;
- keep: `views >= 20000 AND views_to_followers_ratio >= 5`;
- keep: `comments >= 100 AND comment_rate >= 0.1%`;
- keep: `share_rate >= 0.5% OR save_rate >= 0.5%`;
- keep: `views >= 10000 AND views_to_followers_ratio >= 10`;
- drop unless small-account override applies: `views < 10000`, `like_rate < 1%`, `comments < 10`, or known `views_to_followers_ratio < 1`.

Ключевые файлы:

- `src/content_engine/models/hook_research.py`
- `src/content_engine/services/hook_research.py`
- `tests/models/test_hook_research_models.py`
- `tests/services/test_hook_research.py`
- `tests/services/test_brief_builder_hook_research.py`

### Workflow A — Video

Назначение:

- принимает `WorkflowABrief`;
- создаёт selected hook;
- создаёт script;
- создаёт filming card;
- отдаёт `HumanReviewAsset` для ручной съёмки/ревью.

Ключевые файлы:

- `src/content_engine/models/workflow_a.py`
- `src/content_engine/services/workflow_a.py`
- `src/content_engine/orchestration/video_gate.py`
- `.agents/skills/video-intake-skill/SKILL.md`
- `.agents/skills/hook-mining-skill/SKILL.md`
- `tests/services/test_workflow_a_pipeline.py`

Важно:

- Workflow A не пишет final text.
- Workflow A не выполняет research и не расширяет источники.
- Workflow A не создаёт publish queue.
- Workflow A не публикует.
- В readable ProducerOutput Workflow A отображается как `Video / AssetAgent`.

### Workflow B — Text

Назначение:

- принимает `WorkflowBBrief`;
- Writer Entity создаёт один source-backed final text asset;
- для LinkedIn final text на английском;
- internal RU master может быть сохранён для ревью;
- результат идёт в `HumanReviewAsset`.

Ключевые файлы:

- `src/content_engine/models/workflow_b.py`
- `src/content_engine/models/writer_entity.py`
- `src/content_engine/services/writer_entity.py`
- `src/content_engine/services/workflow_b.py`
- `src/content_engine/context/workflow_b_rules.py`
- `tests/services/test_writer_entity.py`
- `tests/services/test_workflow_b_pipeline.py`

Важно:

- Workflow B не пишет видео hooks/scripts.
- Workflow B не показывает финальные Traceability/QA/CTA blocks в user-facing output.
- Workflow B должен начинать Final Text с сильной цепляющей первой фразы, но без отдельного столбца Hook в финальном output.

### Editor / QA Gate

Назначение:

- проверяет source integrity;
- factual safety;
- voice;
- audience/rubric fit;
- one thought / one emotion / one plot;
- отсутствие generic intro;
- отсутствие unsupported claims;
- максимум 3 passes before human review.

Ключевые файлы:

- `src/content_engine/models/editorial_gate.py`
- `src/content_engine/services/editing.py`
- `src/content_engine/orchestration/review_gate.py`
- `tests/models/test_editorial_gate_models.py`
- `tests/services/test_editing_gate.py`

### HumanReviewAsset / Admin Hub

Назначение:

- финальный review-ready object для будущей админки;
- показывает Workflow A video assets и Workflow B text assets;
- не показывает internal pipeline noise как основной UI;
- не является Notion sync.

Ключевые файлы:

- `src/content_engine/models/content_factory.py`
- `src/content_engine/services/content_factory.py`
- `tests/models/test_content_factory_models.py`
- `tests/services/test_content_factory.py`

## 6. Что уже сделано

### Agent-first repository layer

Сделано:

- root `AGENTS.md`;
- nested AGENTS;
- `docs/README.md`;
- `.github/copilot-instructions.md`;
- `.github/instructions/*`;
- `.github/agents/*`;
- `.github/workflows/*`;
- smoke policy;
- ADR;
- validation/deploy runbook;
- `.env.example`;
- `scripts/check.sh`;
- `scripts/smoke/README.md`.

Цель: новый агент должен быстро понять source of truth, high-risk files, validation commands и ограничения.

### Producer restructure

Сделано:

- Producer models and service;
- Producer readable output contract;
- readable HTML/Markdown formatter;
- dry-run now returns both machine `producer_output` and `readable_producer_output`;
- Producer docs and prompt updated.

Последний relevant commit:

```text
dac6901 feat: add readable producer output contract
```

### Opportunity Queue + Brief Builder

Сделано:

- `OpportunityCandidate -> ProducerDecision -> ApprovedOpportunity`;
- `ApprovedOpportunity -> WorkflowABrief | WorkflowBBrief`;
- Producer scene context now passes into both brief types;
- route mismatch validation is enforced before Writer/Video handoff;
- service/model tests.

### Workflow B adapter

Сделано:

- `WorkflowBBrief -> Writer Entity`;
- no placeholder in dry-run;
- Writer Entity produces final text;
- LinkedIn RU master support;
- tests.

Relevant commit:

```text
13a3353 feat: route workflow b briefs through writer entity
```

### Workflow A adapter

Сделано:

- `WorkflowABrief -> Workflow A video pipeline`;
- `HookResearchOutcomeBoard -> approved handoff -> WorkflowABrief`;
- selected hook, script, filming card;
- no publish queue in new output;
- tests.

Relevant commit:

```text
9ab419e feat: route workflow a briefs through video pipeline
```

### Current Russian ProducerOutput artifact

Сгенерирован локальный русский ProducerOutput по сезону:

```text
outputs/2026-04-30_jane_health_villa_producer_output.html
outputs/2026-04-30_jane_health_villa_producer_output.md
```

Содержание:

- 4 эпизода;
- 28 scene cards;
- аудитории;
- продуктовая карта;
- emotional arc;
- sales arc;
- proof plan;
- objection handling;
- content rhythm;
- visual system;
- sales/manual funnel setup;
- metrics plan;
- tasks for workflow agents;
- QA score;
- guardrails;
- first actions.

Важно: `outputs/` — не source of truth. Это generated artifact для просмотра.

## 7. Что пока не сделано / открытые gaps

1. Нет отдельного CLI для генерации readable ProducerOutput из season seed. Сейчас formatter есть в сервисе, а последний HTML был создан локальным Python-прогоном.
2. Admin Hub UI ещё не подключён к новым `HumanReviewAsset` / `readable_producer_output` как runtime data source.
3. ResearchDirective ещё нужно полностью связать с Search Agent runtime в новом producer-first flow.
4. Нужно сделать end-to-end dry run именно новой цепочки: Season Seed -> Producer -> ResearchDirective -> Research -> Analyst -> Opportunity Queue -> ProducerDecision -> Brief Builder -> Workflow A/B -> HumanReviewAsset.
5. Старые Notion modules остаются в коде как legacy/compatibility, но Notion больше не является финальным output layer.
6. Outputs не должны становиться source of truth. Если нужен постоянный результат для интерфейса, надо определить storage/export strategy.
7. Нужна админка Jane Superstar, которая покажет:
   - ProducerOutput season view;
   - Workflow A video assets;
   - Workflow B final text assets;
   - Human review statuses;
   - metrics/feedback loop.

## 8. Current generated season output

Актуальный локальный HTML:

```text
/Users/vasini/Downloads/Je Pro Agent /outputs/2026-04-30_jane_health_villa_producer_output.html
```

Актуальный локальный Markdown:

```text
/Users/vasini/Downloads/Je Pro Agent /outputs/2026-04-30_jane_health_villa_producer_output.md
```

Документ уже переведён на русский. Брендовые / технические исключения допустимы только если это имя бренда или устоявшийся термин. При следующем редактировании лучше проверять:

```bash
rg -n "[A-Za-z]{3,}" outputs/2026-04-30_jane_health_villa_producer_output.md
```

## 9. Validation

Основная команда:

```bash
make check
```

Что делает:

- readonly smoke;
- весь pytest;
- mypy по `src`.

Последний известный полный результат после readable ProducerOutput contract:

```text
347 passed
Success: no issues found in 73 source files
```

Targeted tests для текущих зон:

```bash
pytest tests/services/test_producer_output_contract.py -q
pytest tests/services/test_content_factory.py -q
pytest tests/services/test_producer_service.py -q
pytest tests/services/test_opportunity_queue.py tests/services/test_brief_builder.py -q
pytest tests/services/test_workflow_a_pipeline.py tests/services/test_writer_entity.py -q
```

Перед финальным handoff:

```bash
git diff --check
git status --short
```

## 10. Git / repo status на момент handoff

Текущая ветка:

```text
codex/content-engine-core
```

Последние commits:

```text
dac6901 feat: add readable producer output contract
9ab419e feat: route workflow a briefs through video pipeline
13a3353 feat: route workflow b briefs through writer entity
45145d2 docs: promote imported specs into agent-first structure
c1f9128 docs: complete agent-first repository architecture
```

На момент создания handoff были локальные unrelated изменения:

```text
D docs/handoffs/2026-04-26-admin-panel-gpt-handoff.md
D docs/handoffs/2026-04-27-client-results-interface-handoff.md
?? outputs/2026-04-30_jane_health_villa_producer_output.html
?? outputs/2026-04-30_jane_health_villa_producer_output.md
```

Две deletions в `docs/handoffs` не были сделаны текущей задачей. Не восстанавливать и не удалять их без отдельного решения пользователя.

Output files являются локальными generated artifacts. Не коммитить их как source of truth без отдельного решения.

## 11. Recommended next steps

### Step 1 — ProducerOutput CLI/export command

Добавить маленький CLI:

```text
content-engine-producer-output
```

Задача:

- принять JSON/YAML season seed;
- создать runtime `ProducerOutput`;
- создать readable ProducerOutput;
- сохранить `.html`, `.md`, `.json`.

Это уберёт ручные Python-прогоны.

### Step 2 — Admin Hub data contract

Сделать контракт данных для будущего интерфейса:

```text
SeasonView
ProducerOutputView
WorkflowAVideoAssetView
WorkflowBTextAssetView
HumanReviewAssetView
MetricsSnapshotView
```

Не начинать UI без контракта, иначе админка быстро превратится в статичный красивый файл.

### Step 3 — Connect ResearchDirective to Search Agent

Связать Producer upstream output с Research Agent:

```text
ResearchDirective -> search target profile -> collector run -> SourceItem[]
```

Сохранять compliance + evidence rules.

### Step 4 — End-to-end dry run

Собрать один deterministic dry-run:

```text
season seed
  -> producer directives
  -> sample/public sources
  -> analyst opportunities
  -> queue decisions
  -> briefs
  -> workflow assets
  -> readable/admin outputs
```

### Step 5 — Storage strategy

Решить, где живут результаты вместо Notion:

- local JSON files for MVP;
- SQLite/Postgres later;
- admin-readable export;
- event log for auditability.

## 12. If another agent takes over

Do:

- read `AGENTS.md` first;
- trust `docs/architecture` over handoff/history;
- keep Workflow A and Workflow B separated;
- keep Research Agent as only collection layer;
- use tests before changing contracts;
- preserve generated output vs source-of-truth separation.

Do not:

- add Publisher/Scheduler/auto-publish back;
- make Notion the final output layer again;
- bypass Brief Builder;
- let Analyst directly command Writer in new chain;
- turn readable ProducerOutput task blocks into runtime services;
- commit secrets;
- stage unrelated handoff deletions without user approval.

## 13. One-sentence summary

Система сейчас находится в состоянии: **producer-orchestrated content factory with separate Research, Analyst, Opportunity Queue, Brief Builder, Workflow A Video, Workflow B Text, QA Gate, HumanReviewAsset, and readable ProducerOutput; next step is formal export/CLI + Admin Hub data contract + producer-first end-to-end dry run.**
