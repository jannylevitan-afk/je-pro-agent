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
short_form_source_count_target: 45
max_long_form_sources: 5
max_short_form_duration_seconds: 180
preferred_aspect_ratio: "9:16"
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
| `recovery_energy` | Линия восстановления | recovery after burnout, health reset, breathing, body as system, founder energy, post-overload recovery | 10 |
| `invisible_quality` | Линия невидимого качества | mold, humidity, waterproofing, air quality, hidden systems, invisible defects, material choices | 10 |
| `bali_real_estate` | Линия недвижимости на Бали | Bali villa buying mistakes, due diligence, construction delays, project risks, quality checks, investor mistakes | 10 |
| `phygital_villa_experience` | Линия проекта | phygital spaces, immersive villas, ocean-view event venues, wedding venues, brand events, architecture as experience | 10 |
| `founder_ceo_transition` | Линия предпринимательства + смены роли | founder role shift, CEO reality, launch behind the scenes, team building, from broker/operator to creator | 10 |

`audience_participation is a CTA/feedback mechanic`, not a search topic.

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
- If Instagram metrics are missing, mark the row as blocked and do not count it toward 50.
- If a video has zero/low metrics, move it to dropped discovery and do not count it toward 50.
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

## Handoff Rule

Only rows with all of the following may reach Brief Builder:

- `human_decision = APPROVE_FOR_WORKFLOW_A`
- `qa_status = PASS`
- acceptable risk
- `qualified_topic_counts` matches `topic_source_targets`
- `qualified_platform_counts` matches `platform_source_targets`

Workflow A receives only approved `WorkflowABrief` objects. It must not perform
new research and must not create publish queue.

