# Content Engine — Architecture v3

> **Ключевой принцип:** Research Agent делает весь сбор и поиск данных.
> Воркфлоу не ищут — они принимают данные от Research Agent и обрабатывают их.
> Система не публикует. Публикация — ручная.

---

## Общая структура

```
Research Agent (Layer 0)
│
├── 0A · Seed Config   — статичный конфиг: профили + критерии поиска
├── 0B · Discovery     — динамичный: похожие → Human approval → Monitoring
└── 0C · Monitoring    — ежедневный сбор + маршрутизация
│
├─────────────────────┬───────────────────────┐
│                     │                       │
Workflow A            Workflow B              │
Video Pipeline        Content Farm           │
                      │                       │
                      ├── CD1: Target Audience│
                      ├── CD2: Voice & Tone   │
                      ├── CD3: Fact Dossier   │
                      └── Platform Rules      │
│                                             │
└─────────────────────┴───────────────────────┘
                      ↓
            Notion Content Hub
      (два раздела по воркфлоу)
                      ↓
      Feedback loops → Research Agent
```

---

## Layer 0 — Research Agent

### Роль
Research Agent — единственный компонент системы, который выполняет сбор данных. Воркфлоу не делают никакого поиска самостоятельно. Они только принимают готовые данные от Research Agent и выполняют следующие шаги.

---

### Архитектура Research Agent: три слоя

```
┌─────────────────────────────────────────────────────┐
│  Layer 0A — SEED CONFIG (статичный)                  │
│  Эталонные профили + параметры поиска                │
│  Загружается один раз, обновляется вручную           │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  Layer 0B — DISCOVERY (динамичный)                   │
│  Агент находит похожих от seed-профилей              │
│  Новые профили → очередь → Human approval            │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  Layer 0C — MONITORING (постоянный)                  │
│  Одобренные профили → мониторинг по расписанию       │
│  Новый контент → pull → маршрутизация в A или B      │
└─────────────────────────────────────────────────────┘
```

---

### Layer 0A — Seed Config (статичный конфиг-файл)

Загружается в агент как конфиг-файл через system prompt или как контекстный документ. Обновляется вручную.

Конфиг устроен по **двум осям**:

```
Ось 1: Audience Segment Seeds — КТО источник (для discovery похожих)
Ось 2: Content Theme Seeds    — ЧТО собираем (сигналы по темам)
```

Каждый собранный item получает два тега: `audience_segment` + `content_theme`. Это ускоряет Phase 2 (Insight Extraction) и Phase 3 (Idea Generation) — AI уже знает контекст до анализа.

#### Канонический контракт collected item

Чтобы дедупликация, маршрутизация, переобработка и feedback loop были надёжными, у каждого собранного item должен быть один и тот же базовый контракт данных независимо от источника.

```json
{
  "item_id": "itm_01H...",
  "source_type": "instagram_post",
  "source_name": "@handle",
  "source_url": "https://...",
  "external_item_id": "platform-native-id",
  "collected_at": "2026-04-24T08:00:00Z",
  "published_at": "2026-04-23T15:22:00Z",
  "content_hash": "sha256(normalized_payload)",
  "dedupe_key": "instagram:platform-native-id",
  "audience_segment": "developer_investor",
  "content_theme": "boutique_hotels",
  "raw_payload": "immutable snapshot",
  "transcript_text": "...",
  "media_urls": ["https://..."],
  "engagement_signals": {
    "likes": 0,
    "comments": 0,
    "views": 0
  },
  "routing_decision": "workflow_b",
  "routing_reason": "market observation + textual depth",
  "routing_confidence": 0.82,
  "processing_state": "collected"
}
```

Правила:
- `raw_payload` не редактируется никогда. Все последующие преобразования создают новые сущности, а не переписывают оригинал.
- `dedupe_key` обязателен. Если у платформы нет стабильного `external_item_id`, используется fallback: `source_url + published_at + content_hash`.
- Один upstream item может быть связан и с Workflow A, и с Workflow B, но хранится как одна каноническая запись.
- Любой feedback из аналитики должен ссылаться на `item_id`, иначе система не сможет корректно учиться на том, что реально сработало.

---

#### Ось 1 — Audience Segment Seeds

Эталонные профили по аудиторным сегментам. Используются для discovery похожих аккаунтов (Layer 0B).

```json
{
  "audience_segments": [
    {
      "name": "Девелопер-инвестор",
      "role_in_funnel": "ЗАКАЗЧИК",
      "seed_profiles": [
        { "platform": "instagram", "handle": "artur_mkhitaryan_", "why": "Forbes, Taryan Group, MBA, Дубай/СНГ" },
        { "platform": "instagram", "handle": "anton.karotki", "why": "Предприниматель Бали, строит отель" }
      ],
      "discovery_criteria": {
        "bio_keywords": ["real estate", "developer", "investor", "CEO", "девелопер", "инвестор", "hotel"],
        "geo": ["Bali", "Dubai", "Singapore", "Jakarta", "Moscow"],
        "follower_range": "5K–500K",
        "content_signals": ["рендеры", "бизнес-форумы", "ROI", "стройки"]
      },
      "route_to": "workflow_b"
    },
    {
      "name": "Брокер недвижимости",
      "role_in_funnel": "ПАРТНЕР-ЛИДОГЕНЕРАТОР",
      "seed_profiles": [
        { "platform": "instagram", "handle": "kseniya_asap", "why": "Люксовая недвижимость Дубай/Таиланд" },
        { "platform": "instagram", "handle": "joravdubae", "why": "Агент-провокатор, Бали + ОАЭ + Москва" },
        { "platform": "instagram", "handle": "demuntergilles", "why": "Senior Realtor Бали с 2012, 6 языков" }
      ],
      "discovery_criteria": {
        "bio_keywords": ["realtor", "broker", "agent", "luxury homes", "риелтор", "брокер"],
        "geo": ["Bali", "Dubai", "Thailand", "Moscow", "London"],
        "follower_range": "1K–100K",
        "content_signals": ["видео объектов", "обзоры вилл", "сделки"]
      },
      "route_to": "workflow_b"
    },
    {
      "name": "Архитектор и дизайнер",
      "role_in_funnel": "ПАРТНЕР-КРЕАТОР",
      "seed_profiles": [
        { "platform": "instagram", "handle": "antoniusrichard", "why": "Founder RAD+ar, архитектурная студия Бали" },
        { "platform": "instagram", "handle": "alyona_miller__", "why": "Urban development, Co-founder Horovod Space" }
      ],
      "discovery_criteria": {
        "bio_keywords": ["architect", "designer", "architecture", "studio", "архитектор", "дизайнер"],
        "geo": ["Bali", "Jakarta", "Singapore", "Europe", "СНГ"],
        "follower_range": "1K–50K",
        "content_signals": ["рендеры", "фото проектов", "скетчи"]
      },
      "route_to": "workflow_b"
    },
    {
      "name": "Lifestyle-экспат",
      "role_in_funnel": "ENGAGEMENT-ЯДРО",
      "seed_profiles": [
        { "platform": "instagram", "handle": "viktoriya.onelife", "why": "Living my Best Life, Bali туры, комьюнити" },
        { "platform": "instagram", "handle": "polinka.apelsinka", "why": "Фотограф, Бали + фестивали" }
      ],
      "discovery_criteria": {
        "bio_keywords": ["Bali", "travel", "photographer", "community", "lifestyle", "digital nomad", "expat"],
        "geo": ["Bali", "Canggu", "Ubud", "Seminyak", "Uluwatu"],
        "follower_range": "500–50K",
        "content_signals": ["фото Бали", "travel-контент", "эстетичный визуал"]
      },
      "route_to": "workflow_b"
    }
  ]
}
```

---

#### Ось 2 — Content Theme Seeds

Курированные источники по контентным темам. Мониторируются постоянно. Не требуют discovery — они уже отобраны вручную.

---

##### Тема 1 — Личная жизнь предпринимателя

> Инсайты для личного нарратива: founder journey, семья + бизнес, женский путь.

| Платформа | Источник | Что берём |
|---|---|---|
| Instagram | [@annalutaeva](https://www.instagram.com/annalutaeva/) | личный бренд, lifestyle, семья |
| Telegram | [@TorbosovLife](https://t.me/TorbosovLife) | предпринимательский путь, откровения |
| Instagram | [@kseniya_asap](https://www.instagram.com/kseniya_asap/) | бизнес + личный бренд брокера |
| Instagram | [@burimova](https://www.instagram.com/burimova/) | женский предпринимательский блог |
| Instagram | [@marinamogilko](https://www.instagram.com/marinamogilko/) | lifestyle предпринимателя, Бали-контекст |

**Маппинг в Workflow B:**

| Параметр | Значение |
|---|---|
| Content pillars | lifestyle · journey · human struggle |
| Narrative types | founder struggle · journey of creation · aesthetic reflection |
| Audience portrait | Женщина-мечтательница · Lifestyle-экспат |
| Suggested registers | 7 (выдох) · 8 (исповедь) · 9 (семейный) |
| Route | Workflow B |

---

##### Тема 2 — Экспертные боли / Bali real estate

> Рыночная аналитика, юридические нюансы, профессиональные инсайты по Бали.

| Платформа | Источник | Что берём |
|---|---|---|
| Telegram | [@Bali_expert](https://t.me/Bali_expert) | экспертные наблюдения по рынку |
| Telegram | [@AlexLandSale](https://t.me/AlexLandSale) | земля, сделки, юридика |
| Web | [hotelier-indonesia.com/2026](https://www.hotelier-indonesia.com/2026/) | индустриальная аналитика |
| Telegram | [@BaliLawyer](https://t.me/BaliLawyer) | правовые изменения, риски |
| Web | [realinfo.id/market-reports](https://www.realinfo.id/market-reports) | рыночные отчёты с цифрами |
| Telegram | [@wellstate](https://t.me/wellstate) | wellness + недвижимость пересечение |

**Маппинг в Workflow B:**

| Параметр | Значение |
|---|---|
| Content pillars | expertise · proof |
| Narrative types | authority · market observation · professional lesson |
| Audience portrait | Девелопер-инвестор · Брокер |
| Suggested registers | 3 (аналитика) · 4 (фактура) · 6 (манифест) |
| Route | Workflow B |

---

##### Тема 3 — Bali Travel

> Визуальный и lifestyle-контент про Бали. Источник хуков, атмосферы, локаций.

| Платформа | Источник | Что берём |
|---|---|---|
| Instagram | [@thebalibible](https://www.instagram.com/thebalibible/) | топовый Бали-контент, форматы |
| Instagram | [@baligasm](https://www.instagram.com/baligasm/) | визуальные хуки, локации |
| Web | [nowbali.co.id](https://www.nowbali.co.id/) | события, новости, тренды Бали |
| Web | [thebalibible.com](https://www.thebalibible.com/) | editorial контент о Бали |

**Маппинг в Workflow B + A:**

| Параметр | Значение |
|---|---|
| Content pillars | lifestyle · invitation |
| Narrative types | aesthetic reflection · invitation/community |
| Audience portrait | Lifestyle-экспат · Женщина-мечтательница |
| Suggested registers | 1 (обзор) · 2 (линза) · 7 (выдох) |
| Route | **Оба воркфлоу** — текст (B) + визуальные хуки для видео (A) |

---

##### Тема 4 — Глобальные тренды

> Мировые тренды в travel, wellness, hospitality. Источник для аналитических постов и хуков.

| Платформа | Источник | Что берём |
|---|---|---|
| Web | [htrends.com / Travel Trends](https://www.htrends.com/trends-category-category-Travel%20Trends.html) | трендовые форматы путешествий |
| Web | [globalwellnessinstitute.org / reports](https://globalwellnessinstitute.org/industry-research/featured-reports/) | исследования wellness индустрии |
| Web | [globalwellnessinstitute.org / blog](https://globalwellnessinstitute.org/global-wellness-institute-blog/2022/08/22/presentations/) | презентации и тезисы |

**Маппинг в Workflow A + B:**

| Параметр | Значение |
|---|---|
| Content pillars | expertise · market signals |
| Narrative types | market observation · authority |
| Audience portrait | Все сегменты |
| Suggested registers | 3 (аналитика) · 4 (фактура) |
| Route | **Оба воркфлоу** — тренд-хуки для видео (A) + аналитика для текста (B) |

---

##### Тема 5 — Wellness Architecture

> Пересечение wellness и архитектуры — ключевая тема для AILLA и Clear Visionary.

| Платформа | Источник | Что берём |
|---|---|---|
| Web | [elitetraveler.com / home-spa-design](https://elitetraveler.com/design-culture/architecture-interiors/home-spa-design-tip) | дизайн, spa, luxury интерьеры |

**Маппинг в Workflow B:**

| Параметр | Значение |
|---|---|
| Content pillars | expertise · lifestyle |
| Narrative types | authority · aesthetic reflection |
| Audience portrait | Девелопер-инвестор · Архитектор · Lifestyle-экспат |
| Suggested registers | 2 (линза) · 6 (манифест) |
| Route | Workflow B (+ визуальные хуки для A) |

---

##### Тема 6 — Boutique Hotels & Hospitality

> Кейсы, интервью, индустриальные инсайты по бутик-отелям. Контент для девелоперов и архитекторов.

| Платформа | Источник | Что берём |
|---|---|---|
| Web | [thehoteljournal.com](https://thehoteljournal.com/bill-bensley-interview-sustainable-hotel-designer/) | интервью дизайнеров, кейсы |
| Web | [blla.org / blog](https://blla.org/blla-blog/) | индустриальные тренды бутик-отелей |
| Instagram | [@thestanzamedia](https://www.instagram.com/thestanzamedia/) | hospitality media, визуальные тренды |

**Маппинг в Workflow A + B:**

| Параметр | Значение |
|---|---|
| Content pillars | expertise · proof |
| Narrative types | authority · market observation |
| Audience portrait | Девелопер-инвестор · Брокер · Архитектор |
| Suggested registers | 3 (аналитика) · 6 (манифест) |
| Route | **Оба воркфлоу** — визуальный контент (A) + экспертные тексты (B) |

---

##### Тема 7 — Marketing Cases: Hospitality & Real Estate

> Маркетинговые кейсы именно в нише hospitality и real estate. Источник профессиональных уроков.

| Платформа | Источник | Что берём |
|---|---|---|
| Telegram | [@artemmkey](https://t.me/artemmkey) | кейсы маркетинга, разборы, инсайты |

**Маппинг в Workflow B:**

| Параметр | Значение |
|---|---|
| Content pillars | expertise · proof |
| Narrative types | professional lesson · market observation |
| Audience portrait | Девелопер-инвестор · Брокер |
| Suggested registers | 3 (аналитика) · 8 (исповедь-разворот) |
| Route | Workflow B |

---

#### Сводная таблица маппинга тем

| Тема | Pillars | Аудитория | Registers | Route |
|---|---|---|---|---|
| Личная жизнь предпринимателя | lifestyle · journey · struggle | Женщина-мечтательница · Lifestyle | 7 · 8 · 9 | B |
| Экспертные боли / Bali RE | expertise · proof | Девелопер · Брокер | 3 · 4 · 6 | B |
| Bali Travel | lifestyle · invitation | Lifestyle · Женщина | 1 · 2 · 7 | A + B |
| Глобальные тренды | expertise · market | Все | 3 · 4 | A + B |
| Wellness Architecture | expertise · lifestyle | Девелопер · Архитектор | 2 · 6 | B (+ A хуки) |
| Boutique Hotels | expertise · proof | Девелопер · Брокер · Архитектор | 3 · 6 | A + B |
| Marketing Cases | expertise · proof | Девелопер · Брокер | 3 · 8 | B |

---

#### Как content_theme тег ускоряет пайплайн

Каждый собранный item получает автоматический тег `content_theme` на основе источника. Это убирает лишнюю работу в Phase 2:

```
Item от @artemmkey (Telegram)
  → content_theme = "marketing_cases_hospitality"
  → audience_guess = "Девелопер-инвестор / Брокер"    ← уже известно
  → content_pillar = "expertise / proof"               ← уже известно
  → suggested_register = "3 или 8"                    ← уже известно

Phase 2 (Insight Extraction) только уточняет:
  → конкретный угол
  → emotional trigger
  → reuse score
  → итоговый narrative_type
```

Без тега AI тратит токены на то, что уже определено конфигом.

---

```json
"schedule": {
  "monitoring_frequency": "daily",
  "discovery_run": "weekly",
  "content_theme_sources": "daily",
  "trend_sources": "weekly",
  "internal_sources": "on_demand"
}
```

---

### Layer 0B — Discovery (динамичный поиск похожих)

Агент использует seed-профили как якоря и еженедельно ищет новые релевантные аккаунты.

#### Логика discovery

```
Seed profile
→ найти похожих по: bio_keywords + geo + follower_range + content_signals
→ scoring:
    +3 — точное совпадение bio_keyword
    +2 — совпадение геолокации
    +2 — контент совпадает с content_signals
    +1 — follower_range совпадает
    -2 — явно нерелевантный контент
→ score ≥ 6 → добавить в Notion: Discovery Queue
→ Human review → ✓ одобрен / ✗ отклонён
→ ✓ → переходит в Monitoring List
```

#### Правило: ни один новый профиль не добавляется в мониторинг автоматически.
Всегда требуется human approval. Иначе база засорится нерелевантным контентом.

#### Notion: Discovery Queue

| Поле | Описание |
|---|---|
| Handle | @username |
| Platform | Instagram / LinkedIn / TikTok / Telegram |
| Segment | Девелопер / Брокер / Архитектор / Lifestyle / Video |
| Score | 0–10 |
| Why relevant | 1–2 строки от агента |
| Approved | ✓ / ✗ / pending |
| Added to monitoring | Checkbox |

---

### Layer 0C — Monitoring (постоянный сбор)

Одобренные профили попадают в Monitoring List и сканируются ежедневно.

#### Что собирается по расписанию

| Источник | Частота | Что тянем |
|---|---|---|
| Instagram profiles (одобренные) | ежедневно | новые посты, reels captions, engagement |
| Telegram channels | ежедневно | новые посты, сохранённые сообщения |
| LinkedIn profiles | ежедневно | новые посты |
| YouTube / TikTok | ежедневно | новые видео + captions |
| Internal (notes, voice) | по запросу | транскрибированный текст |
| Discovery scan | еженедельно | поиск новых похожих профилей |

#### Инструменты (рекомендуемые)

| Задача | Инструмент |
|---|---|
| Instagram / TikTok scraping | Apify, PhantomBuster |
| LinkedIn scraping | Apify LinkedIn scrapers |
| Telegram | Telethon (Python), n8n Telegram node |
| YouTube | YouTube Data API |
| Оркестрация и расписание | n8n, Make (Integromat) |
| Reasoning / маршрутизация | Claude API (system prompt с конфигом) |
| Human approval queue | Notion |

---

### Операционная надёжность ingestion

Ежедневный мониторинг без операционного слоя быстро начнёт молча ломаться из-за rate limits, приватных профилей, падения парсеров и неполных выборок. Поэтому для каждого коннектора нужен отдельный технический контур наблюдения.

Для каждого run сохраняем:
- `run_id`
- `connector`
- `source_name`
- `started_at / finished_at`
- `fetched_count`
- `failed_count`
- `last_success_at`
- `error_type`
- `retry_count`
- `staleness_hours`

Правила:
- На любой fetch-ошибке: до 3 retry с backoff.
- Если источник не обновлялся дольше ожидаемого окна, он получает статус `stale`, а не исчезает тихо из пайплайна.
- Partial fetch не идёт дальше как полный success: он маркируется `partial`, чтобы не искажать аналитику.
- Источники с repeated failures попадают в отдельную очередь operator review.
- Любой ручной rerun должен использовать тот же `dedupe_key`, чтобы повторный сбор не плодил дубликаты.

---

### Маршрутизация выходных сигналов

После сбора агент оценивает каждый item и маршрутизирует:

| Тип сигнала | Направление |
|---|---|
| Видеоссылки, trending-форматы, хуки для видео | → Workflow A |
| Текстовые инсайты, основательские углы, рыночные наблюдения | → Workflow B |
| Сильный хук с потенциалом для видео и текста | → Оба |
| Нерелевантный сигнал (score низкий) | → Drop |

---

## Workflow A — Video Pipeline

### Назначение
Производить готовые скрипты для съёмки коротких видео. Платформы: Instagram Reels, TikTok, YouTube Shorts, LinkedIn video.

### Step 1 — Develop Hooks `/video-hooks`
Принимает video-данные от Research Agent. 1 тема → 5 углов → лучший → хук написан.
**Выход:** angle + hook

### Step 2 — Script `/content-scripter`
Скрипт по proven-паттернам: hook → body → CTA. Факт-чек перед съёмкой.
**Выход:** готовый к съёмке скрипт → Notion Scripts Queue

### Step 3 — Film `/film-today` *(human step)*
Система формирует ранжированные filming cards. Человек снимает.

### Step 4 — Publish `/post-content` *(human step)*
Человек публикует вручную. IG, TikTok, YouTube, LinkedIn. Система не публикует.

### Step 5 — Measure `/content-analyst`
Статистика ежедневно. Top hooks + topics → feedback в Research Agent.

**Feedback loop:**
```
Measure → top hook patterns + topics → Research Agent adjusts search params
```

---

## Workflow B — Content Farm

### Назначение
Производить платформо-специфичные текстовые черновики для Instagram, LinkedIn, Telegram. Хранятся в Notion. Публикация — ручная после human review.

---

## Writer Entity — обязательный writing workflow

Workflow B не пишет посты напрямую из темы. Любой пост, тема, video hook, content brief или draft проходит через `Writer Entity`.

Принцип:

```text
Пост не пишется из темы.
Пост пишется из инсайта.

Голос не имитируется "по стилю".
Голос собирается из фактов, регистров, запретов, ритма и границ автора.
```

### Writer Entity = Universal Writing Engine + Author Voice Module

| Слой | За что отвечает |
|---|---|
| Universal Writing Engine | task classification, insight extraction, idea generation, idea gate, brief, draft, editing, platform adaptation, QA |
| Author Voice Module | факты автора, регистры, табу, forbidden phrases, privacy boundaries, rhythm, lexicon, platform rules |

Для Jane Levitan используется `Voice_Jane_Levitan_Agent`. Если для текста от имени Jane нет Fact Dossier или Voice Profile, финальный текст не генерируется.

### Required Writer Input

```json
{
  "raw_topic": "тема или сырой запрос",
  "source_material": "source note, transcript, тезисы, ссылка или описание идеи",
  "target_audience": "кто читает",
  "platform": "LinkedIn | Instagram | Telegram | TikTok | YouTube Shorts",
  "goal": "sales | authority | engagement | nurture | education | personal_brand",
  "tone_of_voice": "expert | sharp | personal | analytical | emotional | manifesto",
  "length": "short | medium | long",
  "cta_type": "comment | save | share | DM | click | no_CTA",
  "author_profile": "generic | jane_levitan | custom",
  "available_context": {
    "fact_dossier": true,
    "voice_profile": true,
    "source_material": true
  }
}
```

### Step-by-step Writer Entity

| Stage | Name | Gate / Output |
|---|---|---|
| 0 | Preflight / Fact / Privacy Gate | `ready / needs_context / blocked`; проверяет тему, source material, audience, platform, goal, Jane dossier/voice/profile/privacy |
| 1 | Task Classification | content type, platform, audience, goal, voice mode, risk level, fact verification required |
| 2 | Insight Extraction | topic, angle, emotional trigger, audience fit, hidden tension, promise, risk |
| 3 | Voice / Register Selection | generic register или Jane register 1–9, rhythm, opening, ending, emoji policy |
| 4 | Idea Generation | 1 insight → 3–5 идей; слабые идеи убиваются здесь |
| 5 | Idea Gate | проходит только идея с инсайтом, эмоцией, пользой, tension/promise, platform fit, voice fit, no invented facts |
| 6 | Content Brief Builder | audience, platform, goal, core message, hook direction, emotional trigger, structure, tone, voice register, CTA, facts, avoid |
| 7 | Draft Generation | platform-native first draft: LinkedIn journey arc, Instagram hook→tension→payoff, Telegram direct thought, Shorts retention logic |
| 8 | AI Editing Layer | усиливает hook, clarity, rhythm, specificity, ending, CTA alignment, voice preservation, fact safety |
| 9 | Voice & Quality QA | generic QA + Jane 7-point QA; high-risk outputs require human review |

### Writer Entity Output Contract

```json
{
  "preflight": {},
  "task_classification": {},
  "insight_card": {},
  "ideas": [],
  "selected_idea": {},
  "content_brief": {},
  "draft": {},
  "edited_final": {},
  "hook_options": [],
  "cta_options": [],
  "qa_report": {}
}
```

### Jane Levitan Voice Module — hard rules

- Facts only from Fact Dossier, source note, or verified public/internal facts.
- Voice only from Voice Profile and selected register.
- Never invent numbers, dates, names, clients, deals, legal details.
- Politics is forbidden.
- Private facts are never used.
- Russian texts address the reader as `ты`.
- No fake AI phrasing, generic motivational endings, hashtag blocks, or generic 3-point sermons.
- Human review is required for financial numbers, deals, clients, legal/regulatory implications, LinkedIn authority positioning, investor/developer content, brand-sensitive content, or confidence below 8/10.

### Separate Video Hooks + Topics Module

Для video-native материала Writer Entity может не писать полный сценарий, а генерировать:

```json
{
  "top_hooks": [],
  "topics": [],
  "best_hook": {},
  "best_topic": {},
  "hook_quality_gate": []
}
```

Hook quality gate проверяет: specificity, curiosity/tension, audience clarity, real payoff, deliverability, emotional sharpness, voice fit, forbidden phrase safety.

---

## КОНТЕКСТНЫЕ ДОКУМЕНТЫ WORKFLOW B

Три документа загружаются в контекст AI-агента перед каждой задачей генерации или редактуры. Они определяют **для кого** пишется контент, **как** он звучит и **на каких фактах** он имеет право строиться.

---

### Context Document 1 — Target Audience Portraits

Используется в: Phase 3 (Idea Generation), Phase 4 (Content Brief), Phase 5 (Draft Generation)

**Бизнес-контекст:**
- Продажа премиальной недвижимости и земли на Бали
- Мультимедиа / experience-проекты (Clear Visionary)
- Личный бренд: бизнесвумен и счастливая мама/жена. Доказательство, что не нужно выбирать между карьерой и семьёй.
- Контент-баланс: 50% личный / 50% профессиональный

---

#### Портрет 1 — Девелопер-инвестор
**Роль:** ЗАКАЗЧИК. Покупает землю, заказывает мультимедиа-проекты. Максимальная ценность сделки.

Кто: мужчина 30–50 лет, CEO/owner девелоперской компании, бюджеты от $500K, мыслит ROI, портфель в нескольких странах.

Боли: где найти качественную землю до роста цен / кому доверить поиск / как дифференцировать проект / нет надёжных партнёров на Бали.

Триггеры: аналитика по зонам с цифрами / кейс с ROI / мультимедиа-визуализация / демонстрация связей.

**Контент для него:** экспертный, аналитика, ROI, цифры, zero bullshit.

---

#### Портрет 2 — Брокер недвижимости
**Роль:** ПАРТНЕР-ЛИДОГЕНЕРАТОР. Реферальные сделки, расширение портфеля.

Кто: 28–45 лет, агент по премиальной недвижимости, ведёт Instagram как инструмент привлечения, хочет выйти на Бали или расширить объекты.

Боли: нет качественных объектов для клиентов / нет партнёра на Бали / конкуренция за клиентов / сложности с legal framework.

Триггеры: "Ищу партнёров-брокеров, условия X%" / off-market листинг / кейс совместной сделки / аналитика почему клиенты скоро спросят про Бали.

**Контент для него:** партнёрский, кейсы, листинги, нетворкинг.

---

#### Портрет 3 — Архитектор и дизайнер
**Роль:** ПАРТНЕР-КРЕАТОР. Совместные мультимедийные проекты для девелоперов.

Кто: 28–45 лет, owner/ведущий специалист архитектурного бюро, ищет заказчиков с бюджетом, ценит эстетику и инновации.

Боли: поиск крупных заказчиков / конкуренция за проекты / нужен партнёр с доступом к земле и клиентам.

Триггеры: уникальные проекты (не "ещё одна вилла") / визуализации / международный портфель / коллаборации.

**Контент для него:** проектный, визуализации, sustainability, архитектурный нарратив.

---

#### Портрет 4 — Lifestyle-экспат и комьюнити-билдер
**Роль:** ENGAGEMENT-ЯДРО. Лайки, комменты, репосты, социальное доказательство.

Кто: 25–40 лет, живёт на Бали или регулярно приезжает, digital nomad / фотограф / организатор ивентов.

Боли: контент должен быть красивым и настоящим / монетизация / поиск своих людей / информационный голод.

Триггеры: атмосферный reel на закате / behind-the-scenes жизни на Бали / приглашение на ивент / рекомендации мест.

**Контент для него:** Бали-lifestyle, визуал, комьюнити, атмосфера.

---

#### Портрет 5 — Женщина-мечтательница
**Роль:** ГЛАВНЫЙ ДРАЙВЕР РОСТА БЛОГА. Самая массовая аудитория, максимальный engagement.

Кто: женщина 25–40 лет, живёт в СНГ или Европе, амбициозная, на развилке "карьера vs семья", ищет реальную ролевую модель — не инфобиз-гуру, а живого человека у которого ПОЛУЧИЛОСЬ.

Подсегменты: "хочу замуж и семью" / "хочу стать мамой, но боюсь потерять себя" / "хочу своё дело" / "хочу ВСЁ одновременно" (ключевой).

Боли: "мне говорят что так не бывает" / чувство вины если работает или если с детьми / нет живых примеров / усталость от выбора "или-или".

Триггеры: "Моё утро: кормлю ребёнка — звонок с клиентом — показ виллы" / "Мне говорили выбери: бизнес или семья. Я выбрала оба" / путь из "офис в Москве" к "бизнес на Бали с детьми".

**Контент для неё:** личный, вдохновляющий, честный, family + business.

---

#### Сводная матрица аудиторий

| Портрет | Бизнес-ценность | Объём | Engagement | Контент |
|---|---|---|---|---|
| Девелопер-инвестор | Максимальная | Малый | Низкий | Экспертный, ROI, аналитика |
| Брокер | Высокая (рефералы) | Средний | Средний | Партнёрский, кейсы |
| Архитектор | Высокая (коллаб) | Малый | Средний | Проектный, визуальный |
| Lifestyle-экспат | Низкая прямая | Средний | Высокий | Бали-lifestyle, визуал |
| Женщина-мечтательница | Косвенная высокая | Максимальный | Максимальный | Личный, вдохновляющий |

---

### Context Document 2 — Voice & Tone of Voice (Jane Levitan)

Используется в: Phase 4 (Content Brief — выбор регистра), Phase 5 (Draft Generation), Phase 6 (AI Editing Layer)

---

#### Кто такая Jane Levitan

CEO и founder двух брендов на Бали:
- **Clear Real Estate** (с января 2023) — брокеридж премиальной недвижимости и земли. Слоган: Zero bullshit.
- **Clear Visionary** (с марта 2025) — разработка experience-проектов. Флагман: AILLA (запуск июль 2026).

Ключевые факты голоса: в декрете закрыла сделок на $7M / первый крупный чек $3M — через неделю после рождения сына / самоучка (медик по образованию) / Zero bullshit — слоган и философия / замужем за Александром (ко-фаундер CV), сын Ваян-Леон / была на Burning Man 2025.

---

#### 9 регистров голоса

| Регистр | Когда использовать |
|---|---|
| 1 — Обзор объекта через историю человека | Посты про виллы, объекты с известным владельцем |
| 2 — Объект как линза трансформации | AILLA, HANDARA, эстетские проекты — важно "что это значит" |
| 3 — Хладнокровная аналитика с личной сценой | Рынок Бали, прогнозы, новости индустрии. Без эмодзи. |
| 4 — Чистая геоэкономическая фактура | Макротренды, регуляторные новости. Без эмодзи. |
| 5 — Короткая рекомендация инсайдера | AI-инструменты, wellness, места, книги. 3–6 предложений. |
| 6 — Корпоративно-манифестный | Clear Visionary как бренд, девелоперы и инвесторы. Без эмодзи. |
| 7 — Эмоциональный пост-выдох | После выступлений, сделок, личных событий. 1–2 эмодзи. |
| 8 — Короткая исповедь-разворот | Reels с уроком из ошибки. Использовать редко — раз в 2 недели. |
| 9 — Короткий семейный пост через предметы | Ваян-Леон, Александр, быт на Бали. Без эмодзи. |

#### Матрица тема → регистр

| Тема | Основной регистр | Запасной |
|---|---|---|
| Experience-продукты | 6 (манифест) | 2 (линза) |
| Бизнес и семья | 9 + 3 | 8 (исповедь) |
| Будни женщины-фаундера | 7 (выдох) | 8, 9 |
| Обзоры недвижимости | 1, 2 | 3 |
| Рынок Бали | 3 (аналитика) | 4 |
| Wellness lifestyle | 5, 9 | 7 |

---

#### Запрещённые фразы (полный запрет)

Нельзя никогда и ни при каких обстоятельствах:
- «В современном быстро меняющемся мире»
- «Давайте погрузимся», «давайте нырнём глубже»
- «Меняющий правила игры», «трансформирующий»
- «Раскройте свой потенциал», «задействовать силу»
- «Синергия», «экосистема», «коллаборация», «масштабировать», «бустить»
- «При этом...», «Тем не менее...», «С учётом этого...», «Примечательно, что...»
- «Каждый провал — это трамплин», «И это совершенно нормально», «Всё к лучшему»
- Три-пунктная проповедь (вступление / пункт 1 / пункт 2 / вывод)
- Мотивационные финалы («будущее принадлежит тем, кто мечтает»)
- Блок хэштегов в конце
- Более 2 жирных элементов на пост

---

#### Фирменная лексика (использовать точно)

- **«Zero bullshit»** — слоган Clear Real Estate. Не разбрасывать.
- **«Отпетые стартаперы»** — про опытных предпринимателей. Уважительно-иронично.
- **«Ахула-махула»** — про женскую энергию и интуицию. Для магического, женского.
- **«Мама олигарха»** — Джейн про себя. Самоироничный маркер.
- **«Банальщина»** — иронично про скучные проекты.

Фирменные связки: «Так вот» / «И знаешь что?» / «Короче» / «Ситуация такова» / «Итого» / «Ибо» / «Вот и»

Фирменные цитаты (использовать точно, не перефразировать):
1. «Я закончила мед — значит могу всё»
2. «У женщины должны быть свои деньги — на чулки, помаду и пентхаус»
3. «Вы не покупаете дом на Бали. Вы покупаете доступ к новой версии себя»
4. «Дешёвая недвижимость на Бали — самая дорогая ошибка»

---

#### Ритм и структура

- Короткие и средние предложения вперемежку. Длинные — редко.
- Одно предложение = один абзац для акцента.
- Перечисления через точку или запятую, не через буллиты.
- Всегда на «ты». Это «ты» равных.
- Открытия никогда не пересказывают тему — парадокс, ударный тезис, личная сцена.
- Финалы никогда не резюмируют — вопрос, образ, ценностная рамка, провокация.

---

#### Табу по темам

- Политика — полный запрет.
- Имена клиентов — никогда в текстах.
- Конкретные цифры выручки (кроме публичных: $3M первый чек, $7M в декрете, $1M инвестиций в AILLA).

---

#### 7-балльный тест перед выдачей черновика

1. Это мог написать кто угодно? Если да — добавь конкретику.
2. Есть запрещённые фразы? Замени или удали.
3. Открытие пересказывает тему? Перепиши.
4. Финал резюмирует или мотивирует? Вырежи.
5. Каждое утверждение подкреплено фактом? Если нет — добавь или убери.
6. Узнает ли Джейн свой голос?
7. Сказала бы она это вслух другу?

---

### Context Document 3 — Fact Dossier & Safe Claims

Используется в: Phase 4 (Content Brief), Phase 5 (Draft Generation), Phase 6 (AI Editing Layer)

CD3 нужен потому, что голос и аудитория сами по себе не защищают от галлюцинаций. В этой системе любое сильное утверждение должно опираться либо на source note, либо на заранее подтверждённый факт о бренде, человеке или рынке.

#### Структура fact record

| Поле | Значение |
|---|---|
| Claim | Само утверждение |
| Fact type | brand / founder / market / project / legal / internal |
| Verification status | `verified_public` / `verified_internal` / `needs_human_confirmation` / `forbidden` |
| Evidence | ссылка, source note, документ или имя оператора |
| Freshness window | evergreen / 30d / 90d / one-off |
| Allowed usage | public / internal only / never in copy |

#### Правила использования CD3

- В черновики можно вставлять только `verified_public` и `verified_internal`.
- `needs_human_confirmation` разрешён в брифе как незакрытый вопрос, но не разрешён в финальном тексте.
- `forbidden` не может попасть ни в один AI output.
- Если freshness window истёк, факт автоматически считается неподтверждённым до обновления.
- Любой market/legal факт без источника или даты должен быть вырезан, а не "смягчён".

#### Минимальные пакеты фактов

- **Evergreen brand facts:** названия брендов, позиционирование, публичные слоганы, подтверждённые биографические вехи.
- **Project facts:** AILLA, HANDARA, объекты, стадии, инвестиции, публичные анонсы.
- **Sensitive facts:** семья, дети, клиенты, выручка, закрытые сделки, внутренние договорённости.
- **Market facts:** цифры по Бали, legal changes, hospitality trends с датой и ссылкой.

Если нужного факта нет в CD3, система должна переформулировать тезис как наблюдение, вопрос или субъективную позицию, а не придумывать "правдоподобную" конкретику.

---

## Platform Strategy Layer — Instagram + LinkedIn

Этот слой не заменяет CD1/CD2/CD3, а накладывает на них правила платформы. Он отвечает на вопрос: **в какой lane идёт контент, на каком языке, с какой ролью в воронке и какой уровень source rigor требуется**.

### Platform lanes

| Platform lane | Audience focus | Primary job | Language | Core rule |
|---|---|---|---|---|
| Instagram — Lifestyle lane | Женщина-мечтательница · Lifestyle-экспат | Близость, узнавание, эмоциональная вовлечённость | Русский по умолчанию | Бизнес встроен в жизнь, а не наоборот |
| Instagram — Professional lane | Брокер · Девелопер · Инвестор · Архитектор | Экспертиза, доверие, сохранения, DM | Русский по умолчанию; английский только если пост целится в международный B2B-сегмент | Экспертно, но визуально и доступно |
| LinkedIn — B2B lane | Девелопер · Инвестор · Land owner · Strategic partner | Thought leadership, partnership inbound, deal credibility | Только английский | Никакого lifestyle ради lifestyle |

### Правила распределения по платформам

- Instagram планируется в горизонте **2–4 недели** с балансом примерно **50/50** между lifestyle lane и professional lane.
- Баланс считается **на уровне плана**, а не по принципу "через день одно, через день другое". Линии должны переплетаться, а не жить как два разных аккаунта.
- LinkedIn — отдельная B2B-площадка: английский язык, экспертные источники, кейсы, аналитика, сделки, девелоперская оптика.
- Для каждого idea/brief/draft обязательно задаются: `platform_lane`, `funnel_role`, `language_mode`.
- Один asset = один основной язык. Билингвальные посты по умолчанию запрещены, если это не отдельное осознанное решение оператора.

### Language policy: Notion vs publish layer

- **Notion — всегда рабочий контур на русском.** Все идеи, брифы, пояснения, review notes и master drafts хранятся в русском языке.
- Для Instagram publish version обычно совпадает с русским master, если оператор не решил иначе.
- Для `LinkedIn B2B` publish language всегда английский, но в Notion всё равно хранятся **две связанные версии**:
  - `ru master` — каноническая рабочая версия
  - `en publish version` — версия для реальной публикации в LinkedIn
- Английская LinkedIn-версия не должна быть буквальным переводом по умолчанию. Это адаптированная publish-version, которая сохраняет смысл, voice и funnel-role русского master-текста.
- Любой human review в первую очередь опирается на `ru master`, но перед публикацией человек видит и `en publish version`.

### Funnel roles для каждого текста

Каждая единица контента должна понимать свою задачу в системе:

| funnel_role | Что делает |
|---|---|
| attention | Останавливает и собирает новый охват |
| affinity | Создаёт близость, узнавание, эмоциональную связь |
| authority | Показывает экспертизу, рынок, кейсы, логику решений |
| conversion | Ведёт к DM, звонку, партнёрскому контакту или вопросу по объекту |

Правило: не каждый пост продаёт напрямую, но каждый пост должен иметь явную роль в воронке.

### Сквозная narrative line: AILLA

AILLA не должна жить отдельной рекламной веткой. Это постоянная narrative line, которая пересекает обе Instagram lanes и LinkedIn, но с разной логикой:

- Instagram lifestyle lane → AILLA как мечта, эстетика, процесс, личное переживание проекта.
- Instagram professional lane → AILLA как девелоперский кейс, планировка, yield logic, product thinking.
- LinkedIn → AILLA как experience-development case, market positioning, hospitality/investor logic.

### Приоритетные экспертные темы

Для professional lane и LinkedIn в приоритете не "общая экспертиза", а темы с высокой дифференциацией:

- rental yield как recurring narrative
- красные флаги рынка: front-loaded payments, dumping, overlaunching
- сделки, структура, legal/market nuance
- оффер для партнёров: брокеры, девелоперы, архитекторы, land owners

---

## Repurposing Logic — Content Atoms

Один source note или insight не должен умирать в одном формате. После Phase 2 система выделяет из материала **content atoms** — короткие самостоятельные единицы смысла, которые можно адаптировать под разные платформы и воркфлоу.

### Что считается content atom

| Atom type | Что это | Куда лучше идёт |
|---|---|---|
| Quotable claim | смелый тезис, формулировка, позиция | LinkedIn post, Instagram carousel opener |
| Story moment | мини-сцена с напряжением и развязкой | Instagram caption, Reel hook, Telegram note |
| Tactical tip | конкретный вывод, framework, warning | LinkedIn, carousel, educational Reel |
| Data/stat callout | цифра, benchmark, market signal | LinkedIn, expert Instagram carousel |
| BTS fragment | закулисье проекта, стройки, переговоров | Instagram lifestyle lane, Workflow A |

### Правила repurposing

- Один сильный atom может пойти одновременно в Workflow A и Workflow B, но с разной упаковкой.
- Для каждой repurpose-версии переписывается хук и CTA под platform lane, а не копируется исходный текст.
- Atom без самостоятельного смысла не идёт в публикацию: каждый фрагмент должен работать вне исходного длинного контента.
- Evergreen atoms можно возвращать в план раз в 3–6 месяцев, если тема не потеряла актуальность.

---

## ЭТАПЫ WORKFLOW B (с привязкой к контекстным документам)

---

### Phase 1 — Intake & Structure
**Входящие данные:** raw data от Research Agent

- Принять raw data
- Дедупликация, нормализация, удаление шума
- Конвертация в структурированную source note
- Прикрепить метаданные: `source_type · source_name · source_url · date_collected · platform · topic_guess · audience_guess · content_type_guess · engagement_signals · raw_text`

**Gate:** item понятен с одного взгляда — о чём, почему важно, какой аудитории.

**Выход:** структурированная source note

---

### Phase 2 — Insight Extraction

Часть тегов уже проставлена автоматически на Phase 1 на основе источника (`content_theme` из Seed Config). AI уточняет и дополняет.

**Что уже известно из source тега:**

| source_theme | audience_guess | pillar_guess | register_hint |
|---|---|---|---|
| личная_жизнь_предпринимателя | Женщина-мечтательница | lifestyle · journey | 7 · 8 · 9 |
| экспертные_боли_bali | Девелопер · Брокер | expertise · proof | 3 · 4 · 6 |
| bali_travel | Lifestyle-экспат · Женщина | lifestyle · invitation | 1 · 2 · 7 |
| глобальные_тренды | Все | expertise | 3 · 4 |
| wellness_architecture | Девелопер · Архитектор | expertise · lifestyle | 2 · 6 |
| boutique_hotels | Девелопер · Брокер · Архитектор | expertise · proof | 3 · 6 |
| marketing_cases | Девелопер · Брокер | expertise · proof | 3 · 8 |

**Что AI извлекает дополнительно:**
- конкретный угол подачи
- emotional trigger (что именно задевает аудиторию)
- полезный урок или напряжение/противоречие
- human story element
- reuse potential
- итоговый narrative_type

Обязательные теги: `audience · platform · content_theme · content_pillar · narrative_type · priority · reuse_score`

Типы нарративов: authority / behind the scenes / journey of creation / founder struggle / professional lesson / market observation / invitation / aesthetic reflection

**Выход:** Insight Card с полным набором тегов

---

### Phase 3 — Idea Generation
#### Использует: Context Document 1 — Target Audience Portraits

Перед генерацией идей AI-агент определяет:
- **Кому** адресован контент → выбирает портрет из CD1
- **Какая боль** этого портрета релевантна инсайту
- **Какой триггер** сработает для этой аудитории

Правило: 1 insight → 3–5 идей

Структура каждой идеи:
```
working title
target platform (Instagram / LinkedIn / Telegram)
platform_lane
language_mode
funnel_role
target audience → портрет из CD1
content pillar
emotional hook → привязан к боли портрета
useful point
desired reaction → специфично для портрета
suggested format
```

**Gate A — релевантность:** важно хотя бы одному портрету из CD1?
**Gate B — ценность/эмоция:** практическая ценность, резонанс, сильная позиция?
**Gate C — engagement trigger:** есть причина среагировать, прокомментировать, сохранить?
**Gate D — platform lane fit:** идея действительно органична для выбранной lane, а не натянута на платформу?

Идеи без явной привязки к аудитории из CD1 не идут дальше.

**Выход:** ranked idea backlog с указанием портрета аудитории для каждой идеи

---

### Phase 4 — Content Brief
#### Использует: Context Document 1 + Context Document 2 + Context Document 3

На основе идеи формируется бриф с явным указанием:

```
audience         → портрет из CD1 (полное описание боли и триггеров)
platform         → Instagram / LinkedIn / Telegram
platform_lane    → Instagram Lifestyle / Instagram Professional / LinkedIn B2B
language_mode    → ru / en
funnel_role      → attention / affinity / authority / conversion
purpose          → что должен сделать читатель после прочтения
angle            → угол из insight card
hook             → специфично для портрета аудитории
key points       → не более 3
CTA type         → вопрос / реакция / комментарий / сохранить / поделиться
tone             → регистр из CD2 (выбирается по матрице тема→регистр)
length target    → short / medium / long
engagement obj.  → конкретное целевое действие этого портрета
fact pack        → список допустимых factual claims из CD3 + source note
source rigor     → standard / expert / market-critical
reference sources
```

Выбор регистра (из CD2) вносится в бриф явно. Например: `tone: Регистр 3 — аналитика с личной сценой`.

В брифе также явно фиксируется fact boundary: что можно утверждать как факт, что можно оставить как интерпретацию, а что требует human confirmation.

Правило source rigor:
- `standard` — достаточно source note + CD3.
- `expert` — перед черновиком нужно 3–5 citable sources.
- `market-critical` — обязательно 3–5 citable sources + дата + ссылка + явная проверка свежести.

**Выход:** Content Brief с портретом аудитории и выбранным регистром голоса

Если `platform_lane = LinkedIn B2B`, в брифе дополнительно фиксируется:
- `working_language = ru`
- `publish_language = en`
- `translation_required = true`

---

### Phase 5 — Draft Generation
#### Использует: Context Document 1 + Context Document 2 + Context Document 3

AI-агент генерирует черновик строго по брифу:

**Перед написанием:**
1. Загрузить портрет аудитории из CD1 (боли, триггеры, поведение)
2. Загрузить правила выбранного регистра из CD2
3. Загрузить fact pack из CD3 и source note
4. Проверить: какие факты реально разрешены к использованию? Нет факта — не выдумывать.
5. Если `source_rigor != standard`, собрать и прикрепить 3–5 citable sources до генерации текста.

Правило языка:
- сначала генерируется `ru master draft` как внутренняя каноническая версия;
- если `platform_lane = LinkedIn B2B`, после master draft создаётся отдельная `en publish version`.

**Правила черновика:**
- Platform-specific (LinkedIn = journey arc / Instagram = hook→tension→payoff / Telegram = direct thought piece)
- Audience-specific — написано под конкретный портрет, не под "всех"
- Aligned with brand voice — голос Джейн из CD2, не generic AI
- Emotionally alive — emotional trigger из insight card активирован
- Каждое factual claim должно быть размечено как `verified` или заменено на opinion / observation
- Открытие не пересказывает тему (правило CD2)
- Финал не резюмирует и не мотивирует (правило CD2)
- Нет запрещённых фраз из CD2

LinkedIn pattern: `goal → obstacle → process → lesson → reflection → invite community`
Instagram pattern: `hook → tension → story → aesthetic/emotional payoff → engagement prompt`

**Выход:** `first draft text (ru master)` и, для LinkedIn, `publish version (en)`

---

### Phase 6 — AI Editing Layer
#### Использует: Context Document 2 + Context Document 3

Специализированный AI-редактор прогоняет черновик через 7-балльный тест из CD2:

1. Это мог написать кто угодно? → добавить конкретику
2. Есть запрещённые фразы? → заменить или удалить
3. Открытие пересказывает тему? → переписать
4. Финал резюмирует или мотивирует? → вырезать
5. Каждое утверждение подкреплено фактом? → убрать или заменить
6. Узнает ли Джейн свой голос?
7. Сказала бы она это вслух другу?

Редактор также:
- Тайтенит текст, укорачивает
- Усиливает хук и вступительные строки
- Улучшает ритм (короткие + средние предложения вперемежку)
- Проверяет эмодзи: разрешены только в регистрах 1, 2, 7 — максимум 1–2
- Проставляет factual safety outcome: `clean` / `needs_human_confirmation` / `blocked`

После 7-балльного теста редактор прогоняет черновик через 7 editorial sweeps:
- Clarity — всё ли понятно с первого чтения
- Voice & Tone — нет ли дрейфа голоса
- So What — зачем читателю это знать
- Prove It — чем подтверждён claim
- Specificity — достаточно ли конкретики, цифр, сцен
- Heightened Emotion — чувствуется ли ставка, напряжение, желание
- Zero Risk — нет ли лишнего трения у CTA и next step

Редактор не меняет: факты / стратегию / аудиторию / core message

**Выход:** edited draft v1 — прошедший 7-балльный тест

Для LinkedIn editing layer проверяет обе версии:
- `ru master` — как канонический смысловой исходник
- `en publish version` — как publish-ready adaptation, а не машинный перевод

---

### Phase 7 — Human Review *(human step)*

Human checks:
- звучит ли как Джейн Левитан (не как AI)?
- верна ли core idea?
- подходит ли платформе?
- создаёт ли нужную эмоцию у портрета аудитории из CD1?
- приглашает ли к реакции?
- безопасно ли публиковать (табу по темам CD2)?

**Gate D — platform fit:** именно этой платформе подходит?
**Gate E — brand fit:** соответствует голосу Джейн и бренд-позиции?

**Выход:** final checked text → Notion Content Calendar

**Feedback loop:**
```
engagement data → mapped to audience portrait + topic + format
→ boost best-performing combinations in idea generation
→ signal back to Research Agent
```

---

### Phase 7 — Техническая реализация Approval Gate

#### Что видит Джейн в Notion

В Notion создаётся отфильтрованный **Review Queue** — галерея или таблица, где показываются только записи с `workflow_stage = awaiting_review` и `review_decision = pending`. Каждая карточка содержит всё необходимое для решения:

```
┌──────────────────────────────────────────────┐
│ "Почему дешёвая вилла — самая дорогая ошибка"│
│                                              │
│  Platform:   Instagram                       │
│  Audience:   Девелопер-инвестор              │
│  Register:   Регистр 3 (аналитика)           │
│                                              │
│  ──────────────────────────────────────────  │
│  [полный текст черновика]                    │
│  ──────────────────────────────────────────  │
│                                              │
│  [ ✓ Approve ]  [ ↩ Rewrite ]  [ ✗ Delete ] │
│                                              │
│  Review Notes: ____________________________  │
│  (заметки если нужен rewrite)                │
└──────────────────────────────────────────────┘
```

Джейн читает текст и нажимает одну кнопку. Больше ничего.

#### Кнопки в Notion (Button blocks — без кода)

Настраиваются прямо в Notion: `+ Button → on click: Edit property → Review decision → значение`

| Кнопка | Что делает | Review decision |
|---|---|---|
| ✓ Approve | Текст одобрен, идёт в Calendar | `approved` |
| ↩ Rewrite | Возвращается AI с замечаниями | `needs_rewrite` |
| ✗ Delete | Удаляется из потока | `deleted` |
| ↺ Re-brief | Возврат на этап брифа | `re_brief` |

Поле **Review Notes** — обычный text field. Джейн пишет туда: *"слишком официально, переделай открытие"* или *"убери третий абзац"* — только если выбрала Rewrite.

---

#### Что происходит автоматически (n8n / Make)

n8n следит за Notion Drafts DB через polling каждые 1–2 минуты или через Notion webhook.

**Сценарий 1 — Approved:**
```
Review decision → "approved"
  ↓
n8n читает: title, platform, audience, hook, final_text
  ↓
n8n создаёт запись в Notion Content Calendar:
  - копирует text, platform, audience, pillar, hook
  - status = "scheduled"
  - publish_date = пустое (Джейн ставит сама)
  ↓
Уведомление Джейн в Telegram:
  "✓ Готово к публикации: [title] — [platform]"
  ↓
Черновик обновляется:
  - workflow_stage = "moved_to_calendar"
  - linked_calendar != null
```

**Сценарий 2 — Needs Rewrite:**
```
Review decision → "needs_rewrite"
  ↓
n8n читает: original_draft + Review Notes
  ↓
n8n вызывает Claude API:
  system: CD2 + CD3
  user: "Вот черновик: [draft]. Замечания: [review_notes].
         Перепиши с учётом замечаний, сохрани голос Джейн."
  ↓
Новая версия создаётся в Drafts DB:
  - version = 2 (или 3, n+1)
  - workflow_stage = "awaiting_review"
  - review_decision = "pending"
  - linked_to = original draft
  ↓
Уведомление Джейн в Telegram:
  "↩ Новая версия готова: [title] — версия 2"
```

**Сценарий 3 — Re-brief:**
```
Review decision → "re_brief"
  ↓
n8n находит связанный Brief в Briefs DB
  ↓
Brief.workflow_stage → "revision_needed"
  ↓
Уведомление: "↺ Бриф требует доработки: [title]"
  ↓
Джейн или оператор редактируют бриф вручную
  ↓
После обновления брифа → Draft генерируется заново
```

**Сценарий 4 — Deleted:**
```
Review decision → "deleted"
  ↓
n8n помечает запись:
  - workflow_stage = "archived"
  - archived = true
  ↓
Запись скрывается из всех активных фильтров
  ↓
Причина поражения логируется в аналитику:
  "какие типы контента не проходят approval"
```

---

#### Notion: Drafts DB — поля для Review Gate

| Поле | Тип | Описание |
|---|---|---|
| Title | Title | Название черновика |
| Draft text | Text | Полный текст |
| Draft text RU | Text | каноническая рабочая версия |
| Draft text EN | Text | publish version для LinkedIn, если нужна |
| Platform | Select | Instagram / LinkedIn / Telegram |
| Audience portrait | Select | из CD1 |
| Voice register | Select | Регистр 1–9 из CD2 |
| Version | Number | 1, 2, 3... |
| Working language | Select | ru |
| Publish language | Select | ru / en |
| Workflow stage | Select | `draft_generated` / `ai_edited` / `awaiting_review` / `moved_to_calendar` / `archived` |
| Review decision | Select | `pending` / `approved` / `needs_rewrite` / `re_brief` / `deleted` |
| Review Notes | Text | Замечания Джейн при rewrite |
| AI edited | Checkbox | Прошёл Phase 6? |
| 7-point test passed | Checkbox | из CD2 |
| Factual safety | Select | `clean` / `needs_human_confirmation` / `blocked` |
| Linked brief | Relation | → Briefs DB |
| Linked calendar | Relation | → Content Calendar (после approve) |
| Archived | Checkbox | для deleted items |

---

#### Стек для реализации

| Компонент | Инструмент |
|---|---|
| База черновиков + Review Queue | Notion DB |
| Кнопки approve/rewrite/delete | Notion Button blocks (без кода) |
| Наблюдатель за изменениями | n8n (Notion trigger) или Make |
| Rewrite при needs_rewrite | Claude API через n8n HTTP node |
| Уведомления Джейн | n8n → Telegram Bot |
| Запись в Content Calendar | n8n → Notion Create Page |

---

#### Итоговый flow одним взглядом

```
AI создаёт черновик (Phase 6 done)
  → Notion Drafts: workflow_stage = "awaiting_review" + review_decision = "pending"
  → Уведомление Джейн в Telegram: "Новый черновик на проверке"

Джейн открывает Review Queue в Notion
  → Читает текст
  → Нажимает [ ✓ Approve ]

n8n ловит изменение (до 2 мин)
  → Создаёт запись в Content Calendar
  → Уведомление: "Готово к публикации: [title]"

Джейн ставит дату публикации
  → Публикует вручную когда удобно
```

Цикл rewrite:
```
[ ↩ Rewrite ] + Review Notes
  → Claude API переписывает
  → Draft v2 → workflow_stage = "awaiting_review" + review_decision = "pending"
  → Уведомление: "Версия 2 готова"
  → Джейн снова читает и решает
```

---

## Notion — Content Operating Hub

Весь результат обоих воркфлоу выгружается в Notion. Публикация — ручная.

---

### Section A — Video Workflow

#### Scripts Queue
| Поле | Тип | Описание |
|---|---|---|
| Title | Title | Рабочее название видео |
| Hook | Text | Хук из /video-hooks |
| Platform | Select | IG / TikTok / YT / LinkedIn |
| Script text | Text | Полный скрипт |
| Filming priority | Number | Ранг в очереди |
| Status | Select | scripted / filmed / published |

#### Filming Cards
| Поле | Тип | Описание |
|---|---|---|
| Linked script | Relation | → Scripts Queue |
| Shoot date | Date | — |
| Filmed | Checkbox | — |
| Raw file link | URL | — |

#### Video Publish Calendar
| Поле | Тип | Описание |
|---|---|---|
| Platform | Select | IG / TikTok / YT / LinkedIn |
| Publish date | Date | — |
| Caption | Text | — |
| Status | Select | ready / published |

#### Performance Analytics
| Поле | Тип | Описание |
|---|---|---|
| Linked video | Relation | → Publish Calendar |
| Views | Number | — |
| Saves | Number | — |
| Hook type | Select | — |
| Performance tier | Select | top / average / weak |
| Fed back to RA | Checkbox | — |

---

### Section B — Content Farm Workflow

#### Sources DB
| Поле | Тип | Описание |
|---|---|---|
| Title | Title | — |
| Platform | Select | Telegram / Instagram / LinkedIn / Internal |
| Raw text | Text | Исходный текст от Research Agent |
| External item ID | Text | нативный id платформы |
| Dedupe key | Text | для идемпотентного импорта |
| Content hash | Text | hash нормализованного payload |
| Ingestion status | Select | collected / normalized / partial / failed |

#### Insights DB
| Поле | Тип | Описание |
|---|---|---|
| Topic | Text | — |
| Angle | Text | — |
| Audience portrait | Select | Девелопер / Брокер / Архитектор / Lifestyle-экспат / Женщина-мечтательница |
| Narrative type | Select | — |
| Emotional trigger | Text | — |
| Reuse score | Number | 1–5 |

#### Ideas DB
| Поле | Тип | Описание |
|---|---|---|
| Title | Title | — |
| Platform | Select | — |
| Platform lane | Select | Instagram Lifestyle / Instagram Professional / LinkedIn B2B |
| Language mode | Select | ru / en |
| Funnel role | Select | attention / affinity / authority / conversion |
| Audience portrait | Select | из CD1 |
| Emotional hook | Text | привязан к боли портрета |
| Desired reaction | Text | специфично для портрета |
| Gate passed | Checkbox | Gate A·B·C·D |
| Status | Select | idea / brief-created / dead |

#### Briefs DB
| Поле | Тип | Описание |
|---|---|---|
| Audience portrait | Select | из CD1 |
| Voice register | Select | Регистр 1–9 из CD2 |
| Platform lane | Select | из platform strategy layer |
| Language mode | Select | ru / en |
| Funnel role | Select | attention / affinity / authority / conversion |
| Key points | Text | — |
| CTA type | Select | — |
| Tone | Text | Регистр + правила |
| Fact pack | Text / Relation | разрешённые claims из CD3 |
| Source rigor | Select | standard / expert / market-critical |
| Workflow stage | Select | brief-ready / revision_needed / draft-in-progress / done |

#### Drafts DB
| Поле | Тип | Описание |
|---|---|---|
| Title | Title | — |
| Platform | Select | Instagram / LinkedIn / Telegram |
| Audience portrait | Select | из CD1 |
| Voice register | Select | Регистр 1–9 из CD2 |
| Draft text | Text | — |
| Version | Number | — |
| AI edited | Checkbox | — |
| 7-point test passed | Checkbox | из CD2 |
| Platform lane | Select | из platform strategy layer |
| Language mode | Select | ru / en |
| Funnel role | Select | attention / affinity / authority / conversion |
| Workflow stage | Select | draft_generated / ai_edited / awaiting_review / moved_to_calendar / archived |
| Review decision | Select | pending / approved / needs_rewrite / re_brief / deleted |
| Factual safety | Select | clean / needs_human_confirmation / blocked |
| Linked brief | Relation | → Briefs DB |
| Linked calendar | Relation | → Content Calendar |
| Archived | Checkbox | для архивных версий |

#### Content Calendar
| Поле | Тип | Описание |
|---|---|---|
| Platform | Select | Instagram / LinkedIn / Telegram |
| Platform lane | Select | Instagram Lifestyle / Instagram Professional / LinkedIn B2B |
| Language mode | Select | ru / en |
| Working language | Select | ru |
| Publish language | Select | ru / en |
| Audience portrait | Select | из CD1 |
| Voice register used | Select | из CD2 |
| Pillar | Select | expertise / journey / struggle / proof / lifestyle / invitation |
| Funnel role | Select | attention / affinity / authority / conversion |
| Hook | Text | — |
| Final text RU | Text | каноническая русская версия |
| Final text EN | Text | publish version для LinkedIn |
| Publish date target | Date | — |
| Approval status | Select | approved / needs-revision |
| Repurpose status | Select | not-repurposed / repurposed-IG / repurposed-LI / repurposed-TG |

#### Content Performance DB
| Поле | Тип | Описание |
|---|---|---|
| Linked content item | Relation | → Content Calendar |
| Platform | Select | Instagram / LinkedIn / Telegram |
| Reach | Number | — |
| Impressions | Number | — |
| Saves | Number | — |
| Shares | Number | — |
| Comments | Number | — |
| Profile visits | Number | — |
| DMs received | Number | — |
| Inquiry type | Select | broker / developer / investor / lifestyle / ailla |
| Likes | Number | — |
| Engagement rate | Formula / Number | (likes + comments + shares + saves) / reach |
| CTR | Number | если есть link clicks |
| Attribution model | Select | first_touch / last_touch / time_decay |
| Deal influenced | Checkbox | повлиял ли контент на реальную сделку / звонок / интро |
| Performance tier | Select | top / average / weak |

---

## Automation Split

| Тип | Шаги |
|---|---|
| Автоматические | Сбор (RA) · дедупликация · нормализация · тегирование · маршрутизация · выбор портрета аудитории · сбор fact pack · генерация брифа с регистром · создание item в Notion · обновление стадий |
| Human-only | Съёмка · публикация · финальный approve · override AI-правок |
| Гибридные | AI пишет черновик по CD1 + CD2 + CD3 → human финализирует |

---

## Measurement Model — Decision First

Система измеряет не "много ли было лайков", а помогает принимать решения: какой lane работает, какой формат приводит к DM, какие экспертные темы реально влияют на сделки и партнёрства.

### Основные decision metrics

| Layer | Metrics |
|---|---|
| Attention | reach, impressions, hook stop-rate, profile visits |
| Engagement | comments, saves, shares, quality of replies |
| Trust / Authority | broker replies, developer replies, inbound partnership messages |
| Conversion | DMs, calls booked, land inquiries, AILLA inquiries, deal_influenced |

### Event naming convention

События называются в `lowercase_with_underscores` и описывают факт действия, а не интерфейс:

- `draft_reviewed`
- `rewrite_requested`
- `calendar_item_scheduled`
- `post_published`
- `dm_received`
- `broker_inquiry_received`
- `developer_inquiry_received`
- `call_booked`
- `deal_influenced`

### UTM discipline

Если в тексте или профиле используются ссылки, UTM naming должен быть единым:
- `utm_source`
- `utm_medium`
- `utm_campaign`
- `utm_content`

Правило: сначала определяется решение, которое должен поддержать трекинг, и только потом создаётся событие или UTM. Vanity metrics без решения не добавляются.

### Benchmarking и attribution

- Сначала сравниваем контент с **собственной исторической базой**, и только потом с внешними platform benchmarks.
- Для social-performance используются минимум: `engagement_rate`, `save_rate`, `share_rate`, `CTR`, `DM rate`.
- Для бизнес-результатов используем не один attribution view, а минимум два:
  - `last_touch` — что закрыло реакцию
  - `time_decay` — что реально подогревало контакт по пути к сделке
- В ROI/efficiency расчёты включаются не только media spend, но и production effort, если мы хотим принимать бюджетные решения, а не просто радоваться охватам.

---

## Event Flow (для разработчиков)

```
[Research Agent]
→ data_collected
→ routed_to_workflow_a / routed_to_workflow_b

[Workflow A]
hooks_developed → script_generated → filmed → published → measured

[Workflow B]
data_received
→ source_normalized
→ insight_created [audience_portrait tagged from CD1]
→ idea_created [gate A·B·C + audience_fit check]
→ brief_created [voice_register selected from CD2 + fact_pack attached from CD3]
→ draft_generated [CD1 + CD2 + CD3 loaded in context]
→ ai_edited [7-point test from CD2 + factual safety]
→ human_reviewed [gate D·E]
→ approved → push_to_notion → scheduled
```

Fail states:
```
rejected_at_idea           → no audience fit or no engagement value
rejected_at_draft          → failed 7-point test or wrong voice
blocked_factual_safety     → missing or unverified claims require human confirmation
failed_quality_gate        → human override required
```

---

## Summary

```
Research Agent    — собирает всё, маршрутизирует
Workflow A        — принимает → hooks → script → film → publish → measure
Workflow B        — принимает → structure → extract → ideate [CD1] → brief [CD1+CD2+CD3] → draft [CD1+CD2+CD3] → edit [CD2+CD3] → approve
Notion Hub        — хранит результат обоих воркфлоу
Feedback loops    — analytics → Research Agent → следующий цикл
```

**CD1 (Target Audience)** — определяет для кого. Загружается в Phase 3, 4, 5.
**CD2 (Voice & Tone)** — определяет как. Загружается в Phase 4, 5, 6.
**CD3 (Fact Dossier)** — определяет что именно можно утверждать как факт. Загружается в Phase 4, 5, 6.

**Language rule:** публикация в LinkedIn идёт на английском, но Notion остаётся русским рабочим контуром с обязательным хранением `ru master` + `en publish version`.

Если контент не звучит как Джейн Левитан и не адресован конкретному портрету — система работает неправильно.
