# Research Directives: Jane Health Villa Season

**Season ID:** `2026-04-jane-health-villa`  
**ProducerOutput:** `producer-output.md`  
**Route:** Workflow A hook research  
**Status:** active current search contract

Search Agent must read this file before Workflow A hook research.

## Producer Context

Season title: `Снова дышать: здоровье, восстановление и запуск виллы будущего`

Season thesis: Jane turns personal recovery into a serialized pre-launch season:
she restores health and breathing, explains invisible quality on Bali, shifts
from broker to creator, and opens the first circle for a phygital ocean-view
villa.

Product bridge: phygital ocean-view villa on Bali for weddings, private events,
brand events, retreats, dinners, creative productions, and premium experience
clients.

Audience:

- event, wedding, retreat, and brand producers;
- Bali investors, buyers, renters, and real estate operators;
- founder/lifestyle audience following Jane's recovery, motherhood, business,
  and role transition;
- potential team and launch partners.

## Workflow A Hook Search Task

```yaml
directive_type: HOOK_RESEARCH_FOR_WORKFLOW_A
route: workflow_a
source_count_target: 50
platform_source_targets:
  youtube: 15
  tiktok: 15
  instagram: 20
language_source_targets:
  ru: 25
  en: 25
short_form_source_count_target: 45
max_long_form_sources: 5
max_short_form_duration_seconds: 180
preferred_aspect_ratio: "9:16"
topic_search_order:
  - recovery_energy
  - invisible_quality
  - bali_real_estate
  - phygital_villa_experience
  - founder_ceo_transition
per_topic_platform_targets:
  youtube: 3
  tiktok: 3
  instagram: 4
per_topic_language_targets:
  ru: 5
  en: 5
topic_source_targets:
  recovery_energy: 10
  invisible_quality: 10
  bali_real_estate: 10
  phygital_villa_experience: 10
  founder_ceo_transition: 10
```

The final validation set must contain exactly 50 qualified videos. Discovery-only
links do not count.

## Topic Targets

| Topic Key | Producer Rubric | What To Search | Required Qualified Videos |
|---|---|---|---:|
| `recovery_energy` | Линия восстановления | septoplasty transformation, deviated septum recovery, breathing reset, mom entrepreneur burnout, health forced pause, body as system, founder energy crash, post-overload recovery | 10 |
| `invisible_quality` | Линия невидимого качества | tropical build rot, drywall mold Bali, waterproofing failure villa, flat roof drainage, air quality hidden defects, gypsum humidity damage, material degradation tropics | 10 |
| `bali_real_estate` | Линия недвижимости на Бали | Bali villa demolition 2025, PBG permit enforcement, construction quote scam, Bali villa buying mistakes, due diligence checklist, construction delays, market saturation 39000 listings | 10 |
| `phygital_villa_experience` | Линия проекта | phygital luxury activation, immersive wedding venue ocean view, holographic architecture, brand event villa, clifftop venue viral, architecture as experience | 10 |
| `founder_ceo_transition` | Линия предпринимательства + смены роли | woman CEO real estate transition, full circle moment founder, NDA project reveal, day in my life CEO, founder team building launch, broker to creator | 10 |

`audience_participation is a CTA/feedback mechanic`, not a search topic.

## Search Loop Algorithm

Search each topic sequentially until its qualified count is met. Do not run one
broad search and then hope the final distribution works.

For each topic:

1. Search both Russian and English public videos.
2. Search YouTube Shorts, TikTok, and Instagram Reels.
3. Fill the per-topic quota before moving to the next topic:
   - YouTube: 3 qualified videos;
   - TikTok: 3 qualified videos;
   - Instagram: 4 qualified videos.
4. Keep collecting candidates until the topic has 10 qualified videos or the
   connector reports a hard blocker.
5. Record blocked candidates separately. Missing metrics, off-format videos, and
   low-metric videos do not count toward the topic quota.

This creates the final board quota:

```yaml
language_source_targets:
  ru: 25
  en: 25
per_topic_platform_targets:
  youtube: 3
  tiktok: 3
  instagram: 4
```

## RU/EN Query Expansion

| Topic Key | Russian Search Examples | English Search Examples |
|---|---|---|
| `recovery_energy` | септопластика восстановление дыхание; мама предприниматель выгорание; 20 раз болела иммунитет; нервная система восстановление энергия; тело остановило раньше головы | septoplasty transformation breathing; deviated septum changed my life; mom entrepreneur burnout recovery; health crisis forced pause best thing; body as system recovery |
| `invisible_quality` | плесень Бали гипсокартон влажность; гидроизоляция вилла провал; тропическая гниль стройка; скрытые дефекты плоская крыша дренаж | tropical build rot villa 3 years; drywall mold Bali humidity; waterproofing failure flat roof drainage; villa hidden defects material degradation |
| `bali_real_estate` | Бали снос вилл 2025; PBG разрешение Бали; смета 30-40% разница; 39000 листингов загрузка 65%; Бали покупка ошибки due diligence | Bali villa demolition 2025 48 villas; PBG permit enforcement; construction quote 30-40% difference scam; Bali 39000 listings occupancy 65%; Bali buying mistakes checklist |
| `phygital_villa_experience` | иммерсивное пространство свадьба океан; фиджитал архитектура голограмма; вилла событие бренд ивент; свадебная площадка океан вид | immersive wedding venue ocean view clifftop; phygital hologram architecture luxury; Hugo Boss hologram viral; brand event villa experience; wedding venue millions views |
| `founder_ceo_transition` | женщина CEO недвижимость переход; full circle moment квартира 4 года назад; NDA проект раскрытие; день из жизни CEO; от брокера к создателю команда | woman CEO real estate transition CNBC; full circle moment founder apartment hologram; NDA project reveal launch; day in my life CEO founder; broker to creator team building |

## Required Board Counts

```yaml
qualified_sources: 50
qualified_platform_counts:
  youtube: 15
  tiktok: 15
  instagram: 20
qualified_topic_counts:
  recovery_energy: 10
  invisible_quality: 10
  bali_real_estate: 10
  phygital_villa_experience: 10
  founder_ceo_transition: 10
qualified_format_counts:
  short_form: 45
  long_form: 5
```

`qualified_topic_counts must match topic_source_targets`.

## Minimum Gate

Analyze only short-form videos with public metrics. A candidate qualifies only if
one of these keep rules is true and no hard drop rule applies:

```text
BROAD_VIRAL:
views >= 100000 AND like_rate >= 2% AND comments >= 30

NICHE_VIRAL:
views >= 20000 AND views_to_followers_ratio >= 5 AND like_rate >= 3%

STRONG_DISCUSSION:
comments >= 100 AND comment_rate >= 0.1%

HIGH_VALUE_SIGNAL:
share_rate >= 0.5% OR save_rate >= 0.5%

SMALL_ACCOUNT_BREAKOUT:
views >= 10000 AND views_to_followers_ratio >= 10

DROP unless small-account override applies:
views < 10000
OR like_rate < 1%
OR comments < 10
OR known views_to_followers_ratio < 1
```

Views alone are not proof. Shares, saves, and comments are stronger signals than
likes.

## Search Rules

- Search TikTok, Instagram Reels, YouTube Shorts, and producer-approved public video sources.
- Prefer 9:16 short-form videos under 180 seconds.
- Long educational YouTube sources are support-only and max 5 in the 50-video validation set.
- If Firecrawl MCP fails on TLS/certificate handling, use Firecrawl CLI/API outside the MCP path for public URL discovery.
- Use Apify actor-backed extraction for Instagram Reels and TikTok public videos when platform metrics are needed.
- If Instagram metrics are missing, mark the row as blocked and do not count it toward 50.
- If a video has zero/low metrics, move it to dropped discovery and do not count it toward 50.
- If an actor returns `no_items`, 400, private/empty data, or no public metrics, record a blocked candidate and keep searching.
- If one topic fills all qualified rows, block the board even if platform and metric gates pass.
- Search Agent must not write scripts, captions, publish queue, or final assets.

## Evidence Required Per Qualified Video

- public source URL;
- platform;
- topic key;
- title or visible first-frame text;
- observed source hook/opening when available;
- duration;
- public metrics: views, likes, comments, shares, saves when available;
- calculated rates and minimum gate classification;
- topic alignment reason;
- reuse boundary: adapt pattern only, never copy wording, creator identity, footage, or sequence.

## Validated Viral References (May 2026 Research)

Research Agent verified the following viral patterns and data points for each
topic. Use these as hook templates and evidence anchors when scoring candidates.

### recovery_energy

| Reference | Platform | Signal | Adaptation |
|---|---|---|---|
| @hallebuttafuso septoplasty transformation | TikTok | millions views, "septoplasty changed my LIFE" | "2 года дышала одной ноздрёй. Управляла бизнесом на 50% кислорода" |
| @izzybizzyspider breathing hack | TikTok | 6M+ views, deviated septum self-test | Simple hook: "раздвинь ноздри и вдохни — если разница огромная, ты дышишь неправильно" |
| Mompreneur burnout trend | IG/TikTok | 71% мам несут невидимую когнитивную нагрузку (2025 study); 68% креаторов — алгоритмическое давление | "20 простуд за 2 года. Иммунитет сдался раньше, чем я" |
| "Charger for myself" format | IG Reels | viral comparison: зарядка для телефона vs зарядка для себя | Show recovery routine as "recharging the system" |

### invisible_quality

| Reference | Platform | Signal | Adaptation |
|---|---|---|---|
| Tropical Build Rot exposés | IG/TikTok/Web | Villas at $600-800/m² degrade in 3-5 years; drywall molds fastest in Bali | "Гипсокартон на Бали = плесень через 2 года" |
| Bali villa demolition wave 2025 | Web/News | 48 illegal villas demolished, 40% investors skip zoning checks | "В 2025 году на Бали снесли 48 вилл. Без компенсации" |
| Flat roof drainage failures | Web | Flat roofs without drainage → leaks and mold during rainy season | "Плоская крыша без дренажа = плесень к первому сезону дождей" |

### bali_real_estate

| Reference | Platform | Signal | Adaptation |
|---|---|---|---|
| Construction cost exposés | Web | Quotes differ 30-40% for similar villas; cheapest = unlicensed subcontractors | "Разница в сметах 30-40% — дешёвая = без лицензии" |
| Bali market saturation data | Web | 39,000+ short-term listings, median occupancy 65%, stock grew 20% annually | "39,000 вилл на Airbnb. Медианная загрузка 65%" |
| PBG permit enforcement | Web | 50% demolished villas lacked valid PBG; Governor-led demolition July 2025 | "50% снесённых вилл — без PBG" |

### phygital_villa_experience

| Reference | Platform | Signal | Adaptation |
|---|---|---|---|
| Hugo Boss 20m hologram viral | Web/Social | Gisele Bündchen + Lee Min-ho holograms at Tower Bridge, millions views | Phygital = not just lights; it transforms the event |
| Wedding venue viral estates | IG | 70+ estates with millions of views; ocean view + architecture = top content | "Представьте свадьбу, где пространство — часть церемонии" |
| Villa Plenilunio Bali | Web/IG | Clifftop wedding venue with panoramic ocean views, viral bookings | Competitor reference for positioning |
| Looking Glass holographic displays | Web | Home holograms, 2-inch thick, no subscription | Technology anchor for "phygital is real, not sci-fi" |

### founder_ceo_transition

| Reference | Platform | Signal | Adaptation |
|---|---|---|---|
| CNBC Changemakers 2026 | Web | Women leaders redefining real estate; vulnerable founder stories trending | "Весь год я была CEO проекта под NDA" |
| "Day in my life as CEO" format | IG Reels | Consistently viral format across platforms | Show 9-17 work + evening culture in Moscow |
| Full circle moment trend | IG/TikTok | "X years ago in this room" → present transformation | "4 года назад в этой квартире муж сделал голограммы. Теперь мы строим это на Бали" |

## Handoff Rule

Only rows with all of the following may reach Brief Builder:

- `human_decision = APPROVE_FOR_WORKFLOW_A`
- `qa_status = PASS`
- acceptable risk
- `qualified_topic_counts` matches `topic_source_targets`
- `qualified_platform_counts` matches `platform_source_targets`

Workflow A receives only approved `WorkflowABrief` objects. It must not perform
new research and must not create publish queue.
