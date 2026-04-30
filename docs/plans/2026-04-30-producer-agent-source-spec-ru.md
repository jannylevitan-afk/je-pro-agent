# ТЗ: сущность «Продюсер» для workflow контент-сериала и встроенных продаж

> Agent-first status: historical/source spec for Producer Agent.
> Canonical Producer docs are
> `docs/architecture/2026-04-29-producer-agent-entity.md` and
> `.codex/agents/producer_entity.md`.
>
> If this file conflicts with the canonical Producer docs, `AGENTS.md`, or
> current ADRs, follow the canonical docs.

## 0. Назначение документа

Этот документ нужен для Codex как техническое и продуктово-методическое ТЗ.

Цель: создать в существующем workflow отдельную сущность `Producer` / `ProducerAgent`, которая превращает блог в сериал, связывает контент с продажами и управляет логикой прогрева, офферов, CTA, метрик и итераций.

Сущность не заменяет копирайтера, дизайнера, SMM-менеджера или sales-бота. Она управляет смыслом, структурой, драматургией и продажной логикой.

---

## 1. Ключевая идея

Блог должен работать не как набор случайных постов, а как сериал:

- **Сезон** — большая сюжетная дуга на 2–8 недель.
- **Эпизод** — смысловой этап внутри сезона: 1–7 дней.
- **Сцена** — единица контента: сторис, пост, рилс, эфир, письмо, Telegram-пост, short-video.
- **Продажная линия** — не отдельная «вставка рекламы», а встроенная часть сюжета.
- **Оффер** — инструмент решения конфликта/задачи, которая раскрывается в сезоне.
- **Аудитория** — не зритель на диване, а участник: отвечает, голосует, задаёт вопросы, проходит мини-действия, покупает.

Правильная логика: сначала продаётся идея и путь, потом продукт.

---

## 2. Что должна делать сущность «Продюсер»

`ProducerAgent` отвечает за 7 функций:

1. **Диагностика**
   - понять нишу, аудиторию, продукт, цель, текущий контекст автора;
   - выявить главный конфликт сезона;
   - определить, какую трансформацию должен прожить зритель.

2. **Архитектура сериала**
   - создать сезон;
   - разбить сезон на эпизоды;
   - разбить эпизоды на сцены;
   - расставить крючки, кульминации, развязки и мостики между сценами.

3. **Встраивание продаж**
   - связать продукт с сюжетной дугой;
   - разложить путь покупки на этапы;
   - встроить CTA, лид-магниты, диагностики, трипваеры, прямые офферы;
   - распределить интенсивность продаж.

4. **Постановка задач другим сущностям**
   - передать копирайтеру сцен-карты;
   - передать дизайнеру визуальные задачи;
   - передать automation/sales-модулю CTA, ссылки, ключевые слова, ботов;
   - передать publishing-модулю календарь.

5. **Контроль качества**
   - проверить, что контент не случайный;
   - проверить, что каждая сцена имеет сюжетную и бизнес-функцию;
   - проверить, что продажи не выглядят приклеенными скотчем.

6. **Работа с метриками**
   - принимать охваты, удержание, реакции, комментарии, DM, клики, заявки, оплаты;
   - понимать, где проблема: в истории, оффере, CTA, доверии или воронке;
   - корректировать следующие эпизоды.

7. **Сохранение контекста**
   - вести `SeriesMemory`: что уже было сказано, какие обещания даны, какие темы открыты, какие вопросы аудитории появились.

---

## 3. Граница ответственности

### Producer делает

- стратегию сезона;
- сериализацию контента;
- план продаж внутри контента;
- драматургическую структуру;
- контент-календарь;
- задачи для генераторов;
- проверку качества;
- анализ метрик.

### Producer не делает

- не пишет финальные тексты вместо копирайтера, если в workflow есть отдельный Copywriter;
- не публикует сам, если есть Publisher;
- не принимает оплату, если есть Sales/CRM;
- не придумывает фейковые кейсы;
- не усиливает продажи через ложь, фальшивую срочность, манипуляции или выдуманную уязвимость.

---

## 4. Основные сущности данных

### 4.1. ProducerContext

```ts
type ProducerContext = {
  creator: CreatorProfile;
  brand: BrandProfile;
  audience: AudienceSegment[];
  offers: ProductOffer[];
  currentWorkflowState: WorkflowState;
  channels: ChannelConfig[];
  constraints: ProducerConstraints;
  metrics?: MetricsSnapshot;
  memory?: SeriesMemory;
};
```

### 4.2. CreatorProfile

```ts
type CreatorProfile = {
  name: string;
  role: string;
  niche: string;
  positioning: string;
  values: string[];
  tone: string;
  personalBoundaries: string[];
  allowedPersonalThemes: string[];
  forbiddenThemes: string[];
  currentLifeContext?: string;
};
```

### 4.3. ProductOffer

```ts
type ProductOffer = {
  id: string;
  name: string;
  type: "service" | "course" | "consultation" | "digital_product" | "community" | "physical_product" | "brand_deal";
  targetAudience: string;
  coreProblem: string;
  promisedTransformation: string;
  price?: number;
  currency?: string;
  proofAssets: ProofAsset[];
  mainObjections: Objection[];
  funnelSteps: FunnelStep[];
  ctaOptions: CTA[];
  availability: "evergreen" | "launch" | "waitlist" | "limited";
};
```

### 4.4. Season

```ts
type Season = {
  id: string;
  title: string;
  durationDays: number;
  startDate?: string;
  endDate?: string;
  seasonThesis: string;
  narrativeQuestion: string;
  protagonistGoal: string;
  audienceGoal: string;
  mainConflict: string;
  productRole: string;
  emotionalArc: EmotionalBeat[];
  salesArc: SalesArc;
  episodes: Episode[];
  successMetrics: SeasonMetricTarget[];
};
```

### 4.5. Episode

```ts
type Episode = {
  id: string;
  seasonId: string;
  title: string;
  dayRange: string;
  episodeQuestion: string;
  conflict: string;
  insight: string;
  salesFunction: SalesFunction;
  scenes: SceneCard[];
  hookToNextEpisode: string;
};
```

### 4.6. SceneCard

```ts
type SceneCard = {
  id: string;
  episodeId: string;
  channel: "instagram_stories" | "instagram_reels" | "telegram" | "youtube_shorts" | "youtube" | "email" | "blog" | "podcast";
  format: "story" | "post" | "reel" | "carousel" | "live" | "short" | "long_video" | "email";
  sceneType: SceneType;
  plotFunction: PlotFunction;
  salesIntensity: 0 | 1 | 2 | 3;
  hook: string;
  context: string;
  conflictOrQuestion: string;
  valuePoint: string;
  proofPoint?: string;
  offerBridge?: string;
  cta?: CTA;
  nextHook?: string;
  requiredAssets?: string[];
  qaStatus?: "draft" | "passed" | "failed";
};
```

### 4.7. SeriesMemory

```ts
type SeriesMemory = {
  openLoops: OpenLoop[];
  answeredQuestions: string[];
  repeatedObjections: Objection[];
  audienceSignals: AudienceSignal[];
  publishedScenes: PublishedScene[];
  promisesMade: string[];
  proofUsed: string[];
  topicsToAvoidRepeating: string[];
};
```

---

## 5. Типы сцен

```ts
type SceneType =
  | "context"
  | "personal_story"
  | "problem_reveal"
  | "behind_the_scenes"
  | "experiment"
  | "mistake"
  | "lesson"
  | "client_case"
  | "social_proof"
  | "myth_busting"
  | "objection_handling"
  | "product_creation"
  | "offer_intro"
  | "direct_offer"
  | "faq"
  | "decision_point"
  | "community_interaction"
  | "recap"
  | "cliffhanger";
```

---

## 6. Сюжетная функция сцены

```ts
type PlotFunction =
  | "introduce_context"
  | "raise_stakes"
  | "show_conflict"
  | "build_trust"
  | "teach"
  | "show_process"
  | "show_proof"
  | "shift_belief"
  | "answer_objection"
  | "create_desire"
  | "invite_action"
  | "close_loop"
  | "open_next_loop";
```

---

## 7. Интенсивность продаж

Продажи не должны быть бинарными: «продаём / не продаём». Нужна шкала.

### `salesIntensity = 0`

Функция: контекст, доверие, жизнь, наблюдение, человеческое присутствие.

Пример:
- личный фрагмент;
- инсайт;
- закулисье;
- наблюдение из работы;
- вопрос аудитории.

CTA:
- «узнали себя?»
- «что у вас так же?»
- «хотите продолжение?»

### `salesIntensity = 1`

Функция: продать идею, мировоззрение, проблему, критерий выбора.

Пример:
- почему старый способ не работает;
- как отличить симптом от причины;
- что аудитория обычно недооценивает.

CTA:
- «сохраните»;
- «напишите слово»;
- «пройдите мини-диагностику».

### `salesIntensity = 2`

Функция: мягко связать контент с продуктом.

Пример:
- кейс;
- разбор;
- кусок методологии;
- «внутри продукта мы это решаем так».

CTA:
- «получить разбор»;
- «забрать гайд»;
- «встать в лист ожидания»;
- «написать в DM кодовое слово».

### `salesIntensity = 3`

Функция: прямой оффер.

Пример:
- условия;
- цена;
- даты;
- бонусы;
- кому подходит / не подходит;
- дедлайн;
- ссылка на оплату или запись.

CTA:
- «купить»;
- «записаться»;
- «оставить заявку»;
- «забронировать место».

---

## 8. Логика сезона

### 8.1. Формула сезона

```text
Сезон = Контекст автора + цель аудитории + конфликт + путь решения + продукт как инструмент + доказательства + приглашение к действию
```

### 8.2. Обязательные поля сезона

- `title` — название сезона.
- `seasonThesis` — главная мысль сезона.
- `narrativeQuestion` — вопрос, который держит внимание.
- `mainConflict` — что мешает герою/аудитории.
- `audienceGoal` — что хочет зритель.
- `productRole` — зачем продукт в этой истории.
- `salesArc` — как продажа развивается по неделям.
- `episodes` — список эпизодов.
- `metrics` — как понять, что сезон работает.

### 8.3. Пример seasonThesis

Плохо:
```text
Нужно продавать курс.
```

Хорошо:
```text
Показываем, как эксперт перестаёт вести блог хаотично и за 30 дней собирает систему, где контент, продажи и личный стиль работают как один сериал.
```

---

## 9. Архитектура эпизода

Каждый эпизод должен отвечать на один вопрос.

Формула:

```text
Эпизод = вопрос + конфликт + действие + инсайт + мостик к продукту + крючок к следующему эпизоду
```

### Обязательные поля эпизода

- `episodeQuestion`
- `conflict`
- `insight`
- `salesFunction`
- `scenes`
- `hookToNextEpisode`

### Типовые salesFunction

```ts
type SalesFunction =
  | "awareness"
  | "problem_recognition"
  | "belief_shift"
  | "trust_building"
  | "desire_creation"
  | "objection_handling"
  | "offer_reveal"
  | "conversion"
  | "retention"
  | "upsell";
```

---

## 10. Архитектура сцены

Каждая сцена должна иметь 5 частей.

```text
Hook → Context → Tension/Question → Value/Proof → CTA/Next Hook
```

### Правило

Если сцена не имеет ни сюжетной функции, ни бизнес-функции, она удаляется.

### Минимальная SceneCard

```json
{
  "channel": "instagram_stories",
  "format": "story",
  "sceneType": "behind_the_scenes",
  "plotFunction": "show_process",
  "salesIntensity": 1,
  "hook": "Сегодня покажу, почему контент-план обычно разваливается на 3-й день.",
  "context": "Автор пытается собрать неделю контента под запуск.",
  "conflictOrQuestion": "Почему полезные посты не двигают людей к покупке?",
  "valuePoint": "Потому что нет связки между проблемой, личной историей и оффером.",
  "offerBridge": "В системе Продюсера это решается через карту сезона.",
  "cta": {
    "type": "micro",
    "text": "Напишите «сериал», если хотите пример карты сезона."
  },
  "nextHook": "Завтра покажу, как одну продажу разложить на 7 сцен."
}
```

---

## 11. Встраивание продаж в контент

### 11.1. Product-to-Story Mapping

Перед созданием сезона Producer должен разложить продукт.

```text
Продукт → проблема → боль → желание → страх → старая модель → новая модель → доказательство → оффер → CTA
```

### 11.2. Для каждого продукта определить

- Что человек хочет получить?
- Почему он не получил это раньше?
- Какие ошибочные убеждения мешают?
- Какой новый взгляд должен принять?
- Какие доказательства ему нужны?
- Какие возражения возникнут?
- Какой первый безопасный шаг он может сделать?
- Какой прямой CTA нужен на финальной стадии?

### 11.3. Sales Arc

```ts
type SalesArc = {
  funnelStageSequence: FunnelStage[];
  weeklySalesIntensity: WeeklySalesIntensity[];
  beliefShifts: BeliefShift[];
  objectionsToHandle: Objection[];
  proofPlan: ProofPlan[];
  ctaPlan: CTAPlan[];
};
```

### 11.4. Этапы воронки

```ts
type FunnelStage =
  | "attention"
  | "recognition"
  | "trust"
  | "desire"
  | "consideration"
  | "decision"
  | "purchase"
  | "post_purchase";
```

### 11.5. Правильная продажная интеграция

Плохо:
```text
История про день автора. В конце: «Кстати, покупайте курс».
```

Хорошо:
```text
История показывает проблему, которую аудитория узнаёт в себе. Автор показывает, как решал её сам/с клиентом. Затем объясняет принцип. Затем продукт появляется как структурированный способ пройти тот же путь быстрее и безопаснее.
```

---

## 12. Контентные линии сезона

В каждом сезоне должно быть 5–7 линий.

### 12.1. Главная линия

Трансформация автора/бренда/проекта.

Пример:
```text
Собираю блог как сериал и показываю, как из хаоса сделать систему продаж.
```

### 12.2. Линия аудитории

Зритель узнаёт себя.

Пример:
```text
Почему вы постите много, но покупок мало.
```

### 12.3. Линия продукта

Продукт постепенно раскрывается.

Пример:
```text
Как устроена система Producer внутри workflow.
```

### 12.4. Линия доказательств

Кейсы, цифры, процесс, отзывы, демонстрации.

### 12.5. Линия возражений

Цена, время, страх, «мне рано», «я не умею», «у меня нет аудитории», «я не хочу продавать агрессивно».

### 12.6. Линия личности

Ценности, характер, вкус, выборы, ошибки, энергия автора.

### 12.7. Линия участия аудитории

Опросы, вопросы, голосования, DM, мини-задания, разборы.

---

## 13. Ритм публикаций

### Базовый ритм на 7 дней

| День | Сюжетная функция | Продажная функция | Интенсивность |
|---|---|---|---|
| 1 | Контекст и вопрос недели | Awareness | 0–1 |
| 2 | Проблема и узнавание | Problem recognition | 1 |
| 3 | Личный/клиентский конфликт | Trust | 1 |
| 4 | Метод/инсайт | Belief shift | 1–2 |
| 5 | Доказательство/разбор | Desire | 2 |
| 6 | Возражения/FAQ | Consideration | 2 |
| 7 | Оффер/приглашение/рекап | Decision | 2–3 |

### Правило

Даже в день прямой продажи должна быть история, а не только объявление условий.

---

## 14. Шаблон Producer Brief

```md
# Producer Brief

## 1. Автор / бренд
- Имя:
- Роль:
- Ниша:
- Позиционирование:
- Тон:
- Что можно показывать из личного:
- Что нельзя показывать:

## 2. Аудитория
- Кто:
- Что хочет:
- Боли:
- Страхи:
- Возражения:
- Что уже пробовал:
- Какой язык использует:

## 3. Продукт
- Название:
- Тип:
- Цена:
- Главная трансформация:
- Кому подходит:
- Кому не подходит:
- Доказательства:
- CTA:
- Воронка:

## 4. Сезон
- Название:
- Длина:
- Главный вопрос:
- Конфликт:
- Финальная точка:
- Роль продукта:
- Метрики успеха:

## 5. Ограничения
- Каналы:
- Частота:
- Запреты:
- Юридические требования:
- Дедлайны:
```

---

## 15. Шаблон Season Bible

```md
# Season Bible

## Название сезона

## Главная мысль

## Вопрос, который держит внимание

## Главный конфликт

## Почему сейчас

## Что зритель должен понять к финалу

## Как продукт встроен в историю

## Эпизоды
1. Эпизод 1:
2. Эпизод 2:
3. Эпизод 3:
4. Эпизод 4:

## Продажная карта
- Неделя 1:
- Неделя 2:
- Неделя 3:
- Неделя 4:

## Возражения
- Возражение:
- Где раскрываем:
- Чем отвечаем:

## Доказательства
- Доказательство:
- Формат:
- Где показываем:

## CTA
- Micro CTA:
- Lead CTA:
- Sales CTA:
```

---

## 16. Шаблон Episode Plan

```md
# Episode Plan

## Эпизод

## Вопрос эпизода

## Конфликт

## Что происходит

## Инсайт

## Какой этап воронки закрываем

## Какие возражения трогаем

## Сцены

| Сцена | Канал | Формат | Hook | Plot Function | Sales Intensity | CTA |
|---|---|---|---|---|---|---|

## Крючок к следующему эпизоду
```

---

## 17. Шаблон SceneCard

```md
# SceneCard

## ID

## Канал

## Формат

## Тип сцены

## Сюжетная функция

## Продажная интенсивность

## Hook

## Контекст

## Напряжение / вопрос

## Ценность / инсайт

## Доказательство

## Мостик к продукту

## CTA

## Крючок к следующей сцене

## Материалы
- Фото:
- Видео:
- Скрин:
- Отзыв:
- Ссылка:

## Проверка
- Есть сюжетная функция: да/нет
- Есть бизнес-функция: да/нет
- Есть связь с сезоном: да/нет
- Есть CTA или next hook: да/нет
```

---

## 18. Алгоритм работы ProducerAgent

```ts
async function runProducerWorkflow(input: ProducerContext): Promise<ProducerOutput> {
  const brief = createProducerBrief(input);

  validateBrief(brief);

  const productStoryMap = mapProductToStory(brief.offers, brief.audience);

  const season = designSeason({
    brief,
    productStoryMap,
    memory: input.memory,
    metrics: input.metrics
  });

  const episodes = planEpisodes(season, productStoryMap);

  const scenes = createSceneCards({
    season,
    episodes,
    channels: input.channels,
    constraints: input.constraints
  });

  const salesPlan = embedSales({
    scenes,
    offers: input.offers,
    funnel: productStoryMap.funnel,
    constraints: input.constraints
  });

  const qaReport = qaProducerOutput({
    brief,
    season,
    episodes,
    scenes,
    salesPlan
  });

  if (qaReport.status === "failed") {
    return reviseUntilPass({
      brief,
      season,
      episodes,
      scenes,
      salesPlan,
      qaReport
    });
  }

  return {
    brief,
    season,
    episodes,
    scenes,
    salesPlan,
    qaReport,
    nextActions: createWorkflowTasks({ scenes, salesPlan })
  };
}
```

---

## 19. Workflow-интеграция

### 19.1. Место в общем процессе

```text
User / Strategy Input
        ↓
ProducerAgent
        ↓
ContentPlanner
        ↓
CopywriterAgent
        ↓
Designer / Video / AssetAgent
        ↓
Publisher
        ↓
Analytics
        ↓
ProducerAgent updates next episode
```

### 19.2. Producer должен запускаться

1. Перед созданием контент-плана.
2. Перед запуском продаж.
3. После получения метрик.
4. При смене продукта.
5. При падении охватов/реакций/заявок.
6. При создании нового сезона.

---

## 20. Events для workflow

```ts
type ProducerEvent =
  | "producer.brief.created"
  | "producer.season.created"
  | "producer.episode.planned"
  | "producer.scenes.created"
  | "producer.sales_embedded"
  | "producer.qa.passed"
  | "producer.qa.failed"
  | "producer.tasks.dispatched"
  | "producer.metrics.ingested"
  | "producer.plan.updated";
```

---

## 21. Output ProducerAgent

```ts
type ProducerOutput = {
  brief: ProducerBrief;
  season: Season;
  episodes: Episode[];
  scenes: SceneCard[];
  salesPlan: SalesPlan;
  qaReport: ProducerQAReport;
  nextActions: WorkflowTask[];
};
```

---

## 22. Workflow tasks

Producer создаёт задачи для других модулей.

```ts
type WorkflowTask = {
  id: string;
  targetAgent: "copywriter" | "designer" | "publisher" | "sales" | "analytics" | "automation";
  priority: "low" | "medium" | "high";
  dueDate?: string;
  payload: Record<string, unknown>;
};
```

Пример:

```json
{
  "targetAgent": "copywriter",
  "priority": "high",
  "payload": {
    "sceneId": "scene_042",
    "format": "instagram_reels",
    "hook": "Почему полезный контент не продаёт?",
    "plotFunction": "shift_belief",
    "salesIntensity": 2,
    "cta": "Напишите «сериал», чтобы получить карту сезона"
  }
}
```

---

## 23. QA: проверка качества

### 23.1. Проверка Brief

- Есть продукт.
- Есть аудитория.
- Есть трансформация.
- Есть ограничения.
- Есть каналы.
- Есть цель сезона.
- Есть метрики.

### 23.2. Проверка Season

- Есть главный вопрос.
- Есть конфликт.
- Есть финальная точка.
- Продукт встроен логически.
- Есть эмоциональная дуга.
- Есть продажная дуга.
- Есть минимум 3 эпизода.
- Есть критерии успеха.

### 23.3. Проверка Episode

- Один эпизод = один вопрос.
- Есть конфликт.
- Есть инсайт.
- Есть salesFunction.
- Есть hookToNextEpisode.
- Сцены не повторяют друг друга.

### 23.4. Проверка Scene

- Есть hook.
- Есть context.
- Есть tension/question.
- Есть value/proof.
- Есть CTA или nextHook.
- `salesIntensity` соответствует этапу воронки.
- Сцена связана с сезоном.
- Сцена не выглядит как случайный пост.

### 23.5. Проверка продаж

- CTA соответствует стадии воронки.
- Не все сцены продают напрямую.
- Оффер не появляется внезапно.
- Возражения обработаны до прямого оффера.
- Доказательства распределены по сезону.
- Нет ложной срочности.
- Нет неподтверждённых обещаний.

---

## 24. Scoring

Каждый план оценивается по 10-балльной шкале.

```ts
type ProducerScore = {
  narrativeClarity: number;
  audienceRelevance: number;
  salesIntegration: number;
  contentVariety: number;
  proofStrength: number;
  ctaClarity: number;
  operationalReadiness: number;
  ethicalSafety: number;
  total: number;
};
```

### Правило прохождения

```text
Plan passes only if:
- total >= 80/100
- narrativeClarity >= 8
- salesIntegration >= 8
- ctaClarity >= 7
- ethicalSafety >= 9
```

---

## 25. Metrics feedback loop

### 25.1. Входные метрики

```ts
type MetricsSnapshot = {
  reach?: number;
  impressions?: number;
  storyCompletionRate?: number;
  watchTime?: number;
  saves?: number;
  shares?: number;
  comments?: number;
  dmCount?: number;
  linkClicks?: number;
  leads?: number;
  purchases?: number;
  revenue?: number;
  conversionRate?: number;
  topQuestions?: string[];
  topObjections?: string[];
};
```

### 25.2. Диагностика по метрикам

| Симптом | Вероятная причина | Что Producer меняет |
|---|---|---|
| Низкое удержание | слабый hook / нет конфликта | усилить первые 2 секунды, добавить вопрос |
| Много реакций, мало кликов | CTA слабый или неуместный | заменить CTA, добавить bridge к офферу |
| Много кликов, мало заявок | проблема в лендинге/оффере/цене | передать задачу Sales/OfferAgent |
| Много вопросов в DM | тема горячая | сделать episode вокруг вопросов |
| Высокие охваты, мало доверия | мало доказательств | добавить кейсы, процесс, отзывы |
| Низкие охваты во время продаж | слишком резкий переход к офферу | вернуть личную/сюжетную линию и снизить интенсивность |
| Высокая вовлечённость, нет оплат | не закрыты возражения | добавить objection-handling scenes |

---

## 26. Guardrails

Producer должен соблюдать ограничения.

### Запрещено

- выдумывать кейсы;
- выдумывать цифры;
- обещать гарантированный доход/результат без оснований;
- делать фейковую срочность;
- копировать чужие закрытые материалы;
- подменять историю манипуляцией;
- использовать личные травмы как дешёвый крючок;
- игнорировать маркировку рекламы и юридические требования;
- публиковать личные данные клиентов без согласия.

### Обязательно

- отделять факт от гипотезы;
- обозначать, где нужен proof asset;
- требовать подтверждение для кейсов и цифр;
- маркировать рекламу там, где это нужно;
- уважать границы автора;
- сохранять тон бренда.

---

## 27. Конфиг ProducerAgent

```yaml
producer:
  defaultSeasonLengthDays: 28
  minEpisodesPerSeason: 3
  maxEpisodesPerSeason: 8
  defaultSalesIntensityRatio:
    intensity_0: 0.30
    intensity_1: 0.35
    intensity_2: 0.25
    intensity_3: 0.10
  directSalesMaxRatioEvergreen: 0.15
  directSalesMaxRatioLaunch: 0.30
  requireCTAOrNextHook: true
  requireProofBeforeDirectOffer: true
  requireObjectionHandlingBeforeDirectOffer: true
  qaMinimumScore: 80
  ethicalSafetyMinimumScore: 9
```

---

## 28. Команды / API

### 28.1. createBrief

```ts
createBrief(context: ProducerContext): ProducerBrief
```

Создаёт стратегический бриф.

### 28.2. createSeason

```ts
createSeason(brief: ProducerBrief): Season
```

Создаёт сезон.

### 28.3. planEpisode

```ts
planEpisode(season: Season, episodeIndex: number): Episode
```

Создаёт эпизод.

### 28.4. createSceneCards

```ts
createSceneCards(episode: Episode, channelConfig: ChannelConfig[]): SceneCard[]
```

Создаёт сцен-карты.

### 28.5. embedSales

```ts
embedSales(scenes: SceneCard[], offer: ProductOffer): SalesPlan
```

Встраивает продажи.

### 28.6. qa

```ts
qa(output: ProducerOutput): ProducerQAReport
```

Проверяет результат.

### 28.7. updateFromMetrics

```ts
updateFromMetrics(season: Season, metrics: MetricsSnapshot): ProducerRevision
```

Обновляет план по метрикам.

---

## 29. Prompt для сущности ProducerAgent

```md
Ты — ProducerAgent.

Твоя задача — превращать блог в сериал и встраивать продажи в контент так, чтобы контент был связным, живым, полезным и коммерчески работающим.

Ты не пишешь случайный контент. Ты строишь сезон, эпизоды и сцены.

Всегда работай по структуре:

1. Диагностика:
   - автор;
   - аудитория;
   - продукт;
   - контекст;
   - цель;
   - ограничения.

2. Сезон:
   - название;
   - главный вопрос;
   - конфликт;
   - трансформация;
   - роль продукта;
   - эмоциональная дуга;
   - продажная дуга.

3. Эпизоды:
   - один эпизод = один вопрос;
   - каждый эпизод закрывает этап воронки;
   - каждый эпизод заканчивается крючком.

4. Сцены:
   - Hook;
   - Context;
   - Tension/Question;
   - Value/Proof;
   - CTA или Next Hook.

5. Продажи:
   - сначала идея;
   - затем проблема;
   - затем доверие;
   - затем желание;
   - затем оффер;
   - затем действие.

6. Проверка:
   - нет случайных сцен;
   - нет приклеенных продаж;
   - нет фейковых кейсов;
   - нет неподтверждённых обещаний;
   - есть CTA;
   - есть связь с сезоном.

Возвращай результат в структурированном JSON или Markdown, в зависимости от запроса workflow.
```

---

## 30. Минимальный JSON-результат

```json
{
  "season": {
    "title": "Блог как сериал: 30 дней сборки системы",
    "seasonThesis": "Показываем, как блог перестаёт быть хаосом и становится сериалом, где контент ведёт к продажам.",
    "narrativeQuestion": "Можно ли продавать регулярно без ощущения навязчивости?",
    "mainConflict": "Контент есть, но он не связан с оффером и не ведёт аудиторию к покупке.",
    "productRole": "Producer workflow — система, которая связывает контент, сюжет и продажи."
  },
  "episodes": [
    {
      "title": "Почему полезный контент не продаёт",
      "salesFunction": "problem_recognition",
      "scenes": [
        {
          "format": "reel",
          "hook": "Вы можете делать полезный контент каждый день и всё равно не продавать.",
          "plotFunction": "show_conflict",
          "salesIntensity": 1,
          "cta": "Напишите «карта», если хотите увидеть структуру сезона."
        }
      ]
    }
  ]
}
```

---

## 31. Acceptance Criteria для Codex

Codex должен реализовать модуль так, чтобы:

1. Можно было создать `ProducerAgent`.
2. `ProducerAgent` принимал `ProducerContext`.
3. На выходе создавались:
   - `ProducerBrief`;
   - `Season`;
   - `Episode[]`;
   - `SceneCard[]`;
   - `SalesPlan`;
   - `ProducerQAReport`;
   - `WorkflowTask[]`.
4. Каждая сцена имела:
   - hook;
   - context;
   - tension/question;
   - value/proof;
   - CTA или nextHook;
   - plotFunction;
   - salesIntensity.
5. Прямой оффер не появлялся без:
   - продуктовой связки;
   - доказательства;
   - обработки ключевых возражений.
6. QA блокировал план, если:
   - нет сюжетной дуги;
   - нет связи продукта с историей;
   - больше допустимой доли прямых продаж;
   - нет CTA;
   - есть фейковые/неподтверждённые обещания.
7. Producer умел принимать метрики и менять следующий эпизод.
8. Producer не ломал существующий workflow, а подключался как orchestration layer.

---

## 32. Рекомендуемая структура файлов

```text
/src/entities/producer/
  ProducerAgent.ts
  ProducerTypes.ts
  ProducerConfig.ts
  ProducerPrompts.ts
  ProducerQA.ts
  SeasonDesigner.ts
  EpisodePlanner.ts
  SceneCardFactory.ts
  SalesEmbedder.ts
  MetricsInterpreter.ts
  SeriesMemory.ts

/src/workflows/
  contentSeriesWorkflow.ts
  salesIntegratedContentWorkflow.ts

/src/templates/producer/
  producerBrief.md
  seasonBible.md
  episodePlan.md
  sceneCard.md
  qaReport.md

/src/tests/producer/
  producerAgent.test.ts
  seasonDesigner.test.ts
  salesEmbedder.test.ts
  producerQA.test.ts
```

---

## 33. Тесты

### Test 1: season creation

```ts
it("creates a season with narrative and sales arcs", async () => {
  const output = await ProducerAgent.run(validContext);
  expect(output.season.narrativeQuestion).toBeDefined();
  expect(output.season.salesArc).toBeDefined();
  expect(output.episodes.length).toBeGreaterThanOrEqual(3);
});
```

### Test 2: scene validation

```ts
it("rejects scenes without hook or CTA/nextHook", () => {
  const scene = createInvalidScene();
  const result = validateScene(scene);
  expect(result.status).toBe("failed");
});
```

### Test 3: direct offer safety

```ts
it("does not allow direct offer before proof and objections", () => {
  const plan = createPlanWithEarlyDirectOffer();
  const qa = qaProducerOutput(plan);
  expect(qa.status).toBe("failed");
});
```

### Test 4: sales intensity balance

```ts
it("keeps direct sales ratio within configured limits", () => {
  const plan = createContentPlan();
  const ratio = calculateDirectSalesRatio(plan.scenes);
  expect(ratio).toBeLessThanOrEqual(config.directSalesMaxRatioEvergreen);
});
```

### Test 5: metrics revision

```ts
it("updates next episode when retention is low", () => {
  const revision = updateFromMetrics(season, { storyCompletionRate: 0.21 });
  expect(revision.actions).toContain("strengthen_hooks");
});
```

---

## 34. Готовая инструкция для Codex

```md
Создай сущность ProducerAgent и встрои её в существующий workflow как orchestration layer перед генерацией контента и после аналитики.

ProducerAgent должен:
1. Принимать ProducerContext.
2. Создавать ProducerBrief.
3. Проектировать сезон блога как сериал.
4. Разбивать сезон на эпизоды.
5. Создавать SceneCard для каждой единицы контента.
6. Встраивать продажи через SalesArc, FunnelStage, CTA и SalesIntensity.
7. Создавать задачи для Copywriter, Designer, Publisher, Sales/Automation и Analytics.
8. Проверять план через ProducerQA.
9. Блокировать результат, если продажи приклеены, сцены случайны или есть неподтверждённые обещания.
10. Принимать MetricsSnapshot и корректировать следующий эпизод.

Используй структуры:
- ProducerContext
- ProductOffer
- Season
- Episode
- SceneCard
- SalesArc
- SalesPlan
- ProducerQAReport
- WorkflowTask
- SeriesMemory

Добавь:
- TypeScript types
- QA validators
- config YAML/TS
- prompt templates
- unit tests
- workflow integration hooks

Главное правило:
контент должен быть сериалом, где каждая сцена имеет сюжетную функцию и бизнес-функцию, а продажа появляется как логичное продолжение истории, а не как случайная рекламная вставка.
```

---

## 35. Финальная проверка документа

- Сущность `ProducerAgent` определена.
- Роль в workflow определена.
- Входы и выходы определены.
- Данные описаны.
- Алгоритм описан.
- Сериализация блога описана.
- Продажи встроены.
- QA правила есть.
- Метрики и обратная связь есть.
- Guardrails есть.
- Acceptance criteria есть.
- Codex-инструкция есть.

Документ готов к передаче в Codex.
