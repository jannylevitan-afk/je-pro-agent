# Workflow Run With Analyst Layer — 2026-04-26

Engine mode: `local_search_agent_dry_run_with_real_anthropic`
Anthropic model: `claude-sonnet-4-6`
Notion mode: `local in-memory dry run` — no live Notion write

## Compliance + Evidence
| Source | Platform | Status | Risk | Collection mode | Evidence item | Evidence excerpt | Route confidence |
|---|---|---|---|---|---|---|---|
| @wellstate | telegram | allowed | low | public_page_or_feed | telegram_1001 | Bali boutique hotels are starting to win against generic villas because buyers compare management depth, legal structure, occupancy logic, and guest experience before they compare price. | 0.84 |
| @controlled_video_source | tiktok | review | medium | public_metadata_only | tiktok_polished-villa-trap | The polished villa trap. Cheap-looking risk usually hides in structure, management, and exit logic. A buyer who checks price first misses the part of the deal that decides whether the asset can actually perform. | 0.92 |

## Pipeline Routing
| Source item | Route | Source page | Insight page | Script page | Briefs | Drafts | KMD files |
|---|---|---|---|---|---:|---:|---|
| telegram_1001 | workflow_b | db_sources_page_1 | db_insights_page_1 |  | 2 | 2 | outputs/2026-04-26_analyst_layer_run_kmd/workflow_b/developer_investor/boutique_hotels/telegram_1001.kmd.md |
| tiktok_polished-villa-trap | both | db_sources_page_2 | db_insights_page_2 | db_scripts_page_1 | 2 | 2 | outputs/2026-04-26_analyst_layer_run_kmd/workflow_a/developer_investor/boutique_hotels/tiktok_polished-villa-trap.kmd.md<br>outputs/2026-04-26_analyst_layer_run_kmd/workflow_b/developer_investor/boutique_hotels/tiktok_polished-villa-trap.kmd.md |

## Analyst Layer Output
| Insight | Audience | Narrative | Emotional trigger | Reuse score | Analyst angle |
|---|---|---|---|---:|---|
| boutique_hotels | developer_investor | market_observation | Status anxiety — the fear of being positioned in a commoditized asset class while smarter capital moves into structurally superior products | 4 | Bali buyers are now evaluating investments on management depth, legal structure, occupancy logic, and guest experience before price enters the conversation. Developers who lead with operational intelligence win deals that villa-first competitors never see. |
| boutique_hotels | developer_investor | professional_lesson | Status anxiety and downside protection — the fear of being the sophisticated investor who got fooled by surface aesthetics | 4 | A visually polished villa can mask fatal weaknesses in structural integrity, operational management, and exit liquidity — the three factors that actually determine whether an asset performs or traps capital. Buyers who lead with price never reach the analysis that matters. |

## Workflow A — Video Output
| Script ID | Title | Platform | Priority | Script text |
|---|---|---|---:|---|
|  | The polished villa trap | tiktok |  | A boutique hotel does not win on beauty. It wins on the reason to return.<br><br>And that distinction is exactly what separates a performing asset from a polished trap.<br><br>Here is what most developer-investors get wrong. They open a deal with the price. But price is the last thing that tells you whether this asset can actually work. The real exposure is buried deeper — in how the legal structure is built, in whether the operations can hold under pressure, and in whether there is a credible exit when you need one.<br><br>A villa that photographs well is not a business. A business needs a reason guests come back, a management layer that does not collapse without the owner in the room, and a structure that a future buyer can actually step into.<br><br>The market logic has to come before the object. If you cannot explain why this location, this format, and this operator create repeat demand — the tile selection does not matter.<br><br>Cheap-looking risk rarely announces itself. It sits inside the documents, the management agreement, and the assumptions nobody challenged at the beginning.<br><br>That is the polished villa trap. Everything visible looks right. Everything invisible is where the deal breaks.<br><br>Save this before your next Bali property review. |

## Workflow B — Final Content Assets

### developer_investor — instagram_professional — instagram_professional

| Field | Value |
|---|---|
| Draft ID | draft_telegram_1001_instagram_professional |
| Platform | instagram |
| Platform lane | instagram_professional |
| Working language | ru |
| Publish language | ru |
| Writer selected idea | boutique hotels: hidden risk |
| Writer human review required | True |

```markdown
## Final Content Asset
**Content ID:** content_draft_telegram_1001_instagram_professional
**Title:** developer_investor — instagram_professional
**Platform:** instagram
**Pillar:** expertise_proof
**Format:** carousel_caption
**Approval Status:** pending

### Final Text
Дешёвый вход на Бали часто оказывается самым дорогим решением на выходе.

Покупатели больше не начинают разговор с цены. Они начинают с вопросов: как устроено управление, какова правовая структура, как работает логика загрузки, что получает гость. Цена появляется позже — если продукт вообще проходит этот фильтр.

Генерические виллы проигрывают не потому, что дороже. Они проигрывают потому, что не могут ответить на эти вопросы убедительно.

Бутик-отель с выстроенной операционной логикой закрывает сделки, которые вилла даже не видит. Не за счёт маркетинга — за счёт структуры.

Правовая конструкция меняет сделку сильнее, чем любой брошюрный текст. Глубина управления определяет, кто вообще сядет за стол переговоров.

Рынок уже сместился. Вопрос в том, на какой стороне этого сдвига находится ваш продукт.
```

### developer_investor — linkedin_b2b — linkedin_b2b

| Field | Value |
|---|---|
| Draft ID | draft_telegram_1001_linkedin_b2b |
| Platform | linkedin |
| Platform lane | linkedin_b2b |
| Working language | ru |
| Publish language | en |
| Writer selected idea | boutique hotels: hidden risk |
| Writer human review required | True |

```markdown
## Final Content Asset
**Content ID:** content_draft_telegram_1001_linkedin_b2b
**Title:** developer_investor — linkedin_b2b
**Platform:** linkedin
**Pillar:** expertise_proof
**Format:** thought_leadership_post
**Approval Status:** pending

### Final Text
Boutique hospitality wins when beauty becomes an operator reality.

The cheapest line item in a Bali project is often the most expensive strategic mistake.

Buyer behavior in Bali has shifted in a way that most developers have not yet priced into their positioning. Serious capital no longer opens with price. It opens with questions: How deep is the management structure? How is ownership legally held? What drives occupancy, and how is the guest experience controlled? Price enters the conversation later — if it leads at all.

Developers still leading with surface differentiation — renderings, location, projected yield — are losing deals before the conversation starts. Not because the product is weak. Because the evaluation is happening on a different level entirely.

Boutique hotels are winning in this environment not because of format, but because they carry an operational logic that can be explained and defended: ownership structure, management model, occupancy mechanics, guest experience design. These are the criteria a qualified buyer stress-tests before signing. Generic villas rarely have coherent answers.

Legal structure changes the deal far more than brochure language suggests. Developers who understand this compete differently — they answer questions that villa-first competitors have not heard yet.

The Bali market has not become more complex. It has become more precise. That distinction matters when the next positioning decision is on the table.
```

### developer_investor — instagram_professional — instagram_professional

| Field | Value |
|---|---|
| Draft ID | draft_tiktok_polished-villa-trap_instagram_professional |
| Platform | instagram |
| Platform lane | instagram_professional |
| Working language | ru |
| Publish language | ru |
| Writer selected idea | boutique hotels: hidden risk |
| Writer human review required | True |

```markdown
## Final Content Asset
**Content ID:** content_draft_tiktok_polished-villa-trap_instagram_professional
**Title:** developer_investor — instagram_professional
**Platform:** instagram
**Pillar:** expertise_proof
**Format:** carousel_caption
**Approval Status:** pending

### Final Text
Дешёвый риск почти никогда не выглядит дёшево.

Полированная вилла с правильным светом и хорошим рендером — не гарантия актива. Это гарантия того, что покупатель задаст не те вопросы.

Три слоя, которые решают судьбу сделки:

**Структура.** Юридическая конструкция меняет экономику объекта сильнее, чем любой брокерский меморандум. Форма владения, разрешения, земельный статус — это не детали, это фундамент.

**Управление.** Без операционной глубины даже хорошо расположенный объект не выходит на целевую загрузку. Гостевой опыт не строится на красивом лобби.

**Логика выхода.** Если актив нельзя продать по понятной цене в понятные сроки — это не инвестиция. Это заморозка капитала с красивым фасадом.

Покупатель, который начинает с цены, никогда не добирается до анализа, который имеет значение.

Сохраните перед следующим разбором сделки.
```

### developer_investor — linkedin_b2b — linkedin_b2b

| Field | Value |
|---|---|
| Draft ID | draft_tiktok_polished-villa-trap_linkedin_b2b |
| Platform | linkedin |
| Platform lane | linkedin_b2b |
| Working language | ru |
| Publish language | en |
| Writer selected idea | boutique hotels: hidden risk |
| Writer human review required | True |

```markdown
## Final Content Asset
**Content ID:** content_draft_tiktok_polished-villa-trap_linkedin_b2b
**Title:** developer_investor — linkedin_b2b
**Platform:** linkedin
**Pillar:** expertise_proof
**Format:** thought_leadership_post
**Approval Status:** pending

### Final Text
Boutique hospitality wins when beauty becomes an operator reality.

The cheapest line item in a Bali deal is often the most expensive strategic mistake.

A polished villa is not evidence of a sound asset. It is a filter — one that removes buyers who stop at aesthetics and never reach the analysis that actually determines performance. In Bali's boutique hotel segment, risk rarely announces itself. It hides in three places.

Structure. The legal ownership framework reshapes the economics of an asset more than any brochure language ever will. The same property under different legal constructions carries different risk profiles, different liquidity, and a different exit horizon.

Management. Operational depth drives real occupancy, guest experience quality, and cash flow stability. A compelling render does not manage bookings or retain staff.

Exit logic. An asset that cannot be sold at a fair price when the moment demands it is not an investment — it is capital locked behind a beautiful facade.

Buyers who lead with price never reach the layer of analysis that decides the outcome. They evaluate the surface and miss everything underneath.

The gap between presentation quality and structural reality is particularly wide in Bali's boutique segment. Entry price looks attractive. Structural weaknesses stay invisible — until the exit window has already closed.

Which of these three layers receives the least scrutiny in early-stage deal evaluation in your market?
```
