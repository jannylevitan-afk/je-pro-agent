# Workflow B Only — Analyst TZ + Final Content Assets

Engine mode: `workflow_b_only_local_dry_run_with_real_anthropic`
Anthropic model: `claude-sonnet-4-6`
Notion mode: `local in-memory dry run` — no live Notion write

## Workflow B Routing Check
| Source item | Route | Insight page | Briefs | Drafts | Workflow A script |
|---|---|---|---:|---:|---|
| workflow_b_boutique_signal_001 | workflow_b | db_insights_page_1 | 2 | 2 | not created |
| workflow_b_market_signal_001 | workflow_b | db_insights_page_2 | 2 | 2 | not created |

## Analyst TZ To Writer

### workflow_b_boutique_signal_001 — instagram_professional

````markdown
## Writer Entity TZ

### Phase 1 Source Note
- Source ID: workflow_b_boutique_signal_001
- Source URL: https://t.me/wellstate/2001
- Platform: instagram_professional
- Audience: developer_investor
- Content theme: boutique_hotels
- Raw excerpt: Bali boutique hotel buyers increasingly evaluate management depth, legal structure, occupancy logic, and guest experience before discussing price. Generic villas lose trust when they cannot explain how demand, operations, and exit logic work together.

### Phase 2 Insight Card
- Topic: What Bali boutique hotel buyers actually evaluate before discussing price
- Angle: Sophisticated investors are raising the bar — generic villa pitches are losing deals to operators who can explain the full system
- Emotional Trigger: Status anxiety — fear of being exposed as an unsophisticated operator or seller in a market where buyers are becoming more rigorous
- Audience Fit: Developer-investors in Bali's boutique hotel segment need to know that the competitive threshold has shifted; positioning a project without a coherent operational and exit narrative now signals weakness, not just incompleteness
- Useful Lesson: Boutique hotel buyers in Bali now scrutinize management depth, legal structure, occupancy logic, and guest experience as a unified system before price enters the conversation. Sellers who cannot articulate how demand, operations, and exit strategy connect are losing credibility before negotiations begin.
- Narrative Type: market_observation
- Reuse Score: 4/5
- Confidence: 0.87

### Marketing Research Adaptation
- JTBD / Customer Job: Decide whether their current project or pitch is positioned to survive scrutiny from increasingly sophisticated buyers, and avoid losing deals to better-prepared competitors
- Pain Point: Generic villa or hotel pitches that lead with price or aesthetics but cannot explain the operational logic, legal structure, or exit pathway are being dismissed early in buyer conversations
- Trigger Event: A developer or investor is preparing to bring a boutique hotel asset to market and realizes their pitch deck or broker materials do not address the systemic questions buyers are now asking
- Desired Outcome: Understand exactly what due-diligence questions serious buyers are asking so they can build a credible, system-level narrative around their asset before going to market
- Behavioral Trigger: loss_aversion

### Writer Constraints
- Purpose: Build market trust through concrete insight.
- Tone/Register: register_3
- Format: carousel_caption
- Opening guide: What looks cheap first is often the most expensive later.
- Key points: Boutique hotel buyers in Bali now scrutinize management depth, legal structure, occupancy logic, and guest experience as a unified system before price enters the conversation. Sellers who cannot articulate how demand, operations, and exit strategy connect are losing credibility before negotiations begin; Sophisticated investors are raising the bar — generic villa pitches are losing deals to operators who can explain the full system; Developer-investors in Bali's boutique hotel segment need to know that the competitive threshold has shifted; positioning a project without a coherent operational and exit narrative now signals weakness, not just incompleteness; Legal structure changes the deal far more than brochure language suggests.
- Facts allowed: Bali hospitality buyers evaluate management depth, legal structure, occupancy logic, and guest experience before price.; Bali hospitality demand is shifting toward longer stays, wellness-led experiences, and credible operator discipline.
- Reference sources: https://t.me/wellstate/2001#source; https://t.me/wellstate/2001#context; https://t.me/wellstate/2001#ops
- Do not write from raw topic alone; write from this insight and source note.

### Opening Sentence Guardrails
- The first line of Final Text is the opening_sentence; do not output a separate Hook block.
- Keep it 5-14 words, concrete, source-specific, and understandable without context.
- It must create tension, recognition, a useful problem, or a precise conflict for the stated audience.
- Do not use tautological openings: no repeated same-root adjective/noun loops such as cheap/cheap, risk/risky, or дешёвый/дешево.
- Banned weak examples: Дешёвый вход на Бали..., Дешёвый риск почти никогда не выглядит дешево, Cheap risk rarely looks cheap.
- If an opening can fit any post, merely restates the topic, or repeats the same semantic hit twice, regenerate it.
- Do not end Final Text with a standalone CTA question; keep review-facing output as final text only.

### Required Output Format
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
- Do not output Hook, CTA, Traceability, or QA sections in the final asset.
````

### workflow_b_boutique_signal_001 — linkedin_b2b

````markdown
## Writer Entity TZ

### Phase 1 Source Note
- Source ID: workflow_b_boutique_signal_001
- Source URL: https://t.me/wellstate/2001
- Platform: linkedin_b2b
- Audience: developer_investor
- Content theme: boutique_hotels
- Raw excerpt: Bali boutique hotel buyers increasingly evaluate management depth, legal structure, occupancy logic, and guest experience before discussing price. Generic villas lose trust when they cannot explain how demand, operations, and exit logic work together.

### Phase 2 Insight Card
- Topic: What Bali boutique hotel buyers actually evaluate before discussing price
- Angle: Sophisticated investors are raising the bar — generic villa pitches are losing deals to operators who can explain the full system
- Emotional Trigger: Status anxiety — fear of being exposed as an unsophisticated operator or seller in a market where buyers are becoming more rigorous
- Audience Fit: Developer-investors in Bali's boutique hotel segment need to know that the competitive threshold has shifted; positioning a project without a coherent operational and exit narrative now signals weakness, not just incompleteness
- Useful Lesson: Boutique hotel buyers in Bali now scrutinize management depth, legal structure, occupancy logic, and guest experience as a unified system before price enters the conversation. Sellers who cannot articulate how demand, operations, and exit strategy connect are losing credibility before negotiations begin.
- Narrative Type: market_observation
- Reuse Score: 4/5
- Confidence: 0.87

### Marketing Research Adaptation
- JTBD / Customer Job: Decide whether their current project or pitch is positioned to survive scrutiny from increasingly sophisticated buyers, and avoid losing deals to better-prepared competitors
- Pain Point: Generic villa or hotel pitches that lead with price or aesthetics but cannot explain the operational logic, legal structure, or exit pathway are being dismissed early in buyer conversations
- Trigger Event: A developer or investor is preparing to bring a boutique hotel asset to market and realizes their pitch deck or broker materials do not address the systemic questions buyers are now asking
- Desired Outcome: Understand exactly what due-diligence questions serious buyers are asking so they can build a credible, system-level narrative around their asset before going to market
- Behavioral Trigger: loss_aversion

### Writer Constraints
- Purpose: Build market trust through concrete insight.
- Tone/Register: register_3
- Format: thought_leadership_post
- Opening guide: The cheapest line item in Bali is often the most expensive strategic mistake.
- Key points: Boutique hotel buyers in Bali now scrutinize management depth, legal structure, occupancy logic, and guest experience as a unified system before price enters the conversation. Sellers who cannot articulate how demand, operations, and exit strategy connect are losing credibility before negotiations begin; Sophisticated investors are raising the bar — generic villa pitches are losing deals to operators who can explain the full system; Developer-investors in Bali's boutique hotel segment need to know that the competitive threshold has shifted; positioning a project without a coherent operational and exit narrative now signals weakness, not just incompleteness; Legal structure changes the deal far more than brochure language suggests.
- Facts allowed: Bali hospitality buyers evaluate management depth, legal structure, occupancy logic, and guest experience before price.; Bali hospitality demand is shifting toward longer stays, wellness-led experiences, and credible operator discipline.
- Reference sources: https://t.me/wellstate/2001#source; https://t.me/wellstate/2001#context; https://t.me/wellstate/2001#ops
- Do not write from raw topic alone; write from this insight and source note.

### Opening Sentence Guardrails
- The first line of Final Text is the opening_sentence; do not output a separate Hook block.
- Keep it 5-14 words, concrete, source-specific, and understandable without context.
- It must create tension, recognition, a useful problem, or a precise conflict for the stated audience.
- Do not use tautological openings: no repeated same-root adjective/noun loops such as cheap/cheap, risk/risky, or дешёвый/дешево.
- Banned weak examples: Дешёвый вход на Бали..., Дешёвый риск почти никогда не выглядит дешево, Cheap risk rarely looks cheap.
- If an opening can fit any post, merely restates the topic, or repeats the same semantic hit twice, regenerate it.
- Do not end Final Text with a standalone CTA question; keep review-facing output as final text only.

### Required Output Format
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
- Do not output Hook, CTA, Traceability, or QA sections in the final asset.
````

### workflow_b_market_signal_001 — instagram_professional

````markdown
## Writer Entity TZ

### Phase 1 Source Note
- Source ID: workflow_b_market_signal_001
- Source URL: https://www.realinfo.id/market-reports/controlled-bali-demand-shift
- Platform: instagram_professional
- Audience: developer_investor
- Content theme: market_reports
- Raw excerpt: Bali hospitality demand is shifting toward longer stays, wellness-led experiences, and properties with credible operator discipline. Developers need evidence of repeat demand and clear management logic before turning a trend into new inventory.

### Phase 2 Insight Card
- Topic: Bali hospitality demand shift toward longer stays, wellness experiences, and operator-disciplined properties
- Angle: Why chasing hospitality trends without demand evidence is the most expensive mistake a Bali developer can make right now
- Emotional Trigger: Status anxiety around being caught holding the wrong asset in a market that has quietly moved on
- Audience Fit: Developer-investors in Bali are actively allocating capital into hospitality product and need a clear framework to separate durable demand signals from trend noise before locking in development decisions
- Useful Lesson: Bali's hospitality market is rewarding developers who can demonstrate repeat demand and credible management systems — not those who simply follow trend cycles into new inventory. Before committing capital, the discipline question must come before the design question.
- Narrative Type: market_observation
- Reuse Score: 4/5
- Confidence: 0.85

### Marketing Research Adaptation
- JTBD / Customer Job: Decide whether to build, hold, or reposition a hospitality asset in Bali based on current demand intelligence
- Pain Point: Fear of developing inventory that looks right on paper but misses the actual demand profile — resulting in underperforming occupancy and weak returns
- Trigger Event: Bali hospitality demand is visibly shifting toward longer-stay and wellness-led profiles, creating pressure to act while also raising the risk of misreading the trend
- Desired Outcome: A clear decision filter that lets them validate demand evidence and operator capability before committing to new hospitality inventory
- Behavioral Trigger: loss_aversion

### Writer Constraints
- Purpose: Build market trust through concrete insight.
- Tone/Register: register_3
- Format: carousel_caption
- Opening guide: What looks cheap first is often the most expensive later.
- Key points: Bali's hospitality market is rewarding developers who can demonstrate repeat demand and credible management systems — not those who simply follow trend cycles into new inventory. Before committing capital, the discipline question must come before the design question; Why chasing hospitality trends without demand evidence is the most expensive mistake a Bali developer can make right now; Developer-investors in Bali are actively allocating capital into hospitality product and need a clear framework to separate durable demand signals from trend noise before locking in development decisions; Legal structure changes the deal far more than brochure language suggests.
- Facts allowed: Bali hospitality buyers evaluate management depth, legal structure, occupancy logic, and guest experience before price.; Bali hospitality demand is shifting toward longer stays, wellness-led experiences, and credible operator discipline.
- Reference sources: https://www.realinfo.id/market-reports/controlled-bali-demand-shift#source; https://www.realinfo.id/market-reports/controlled-bali-demand-shift#context; https://www.realinfo.id/market-reports/controlled-bali-demand-shift#ops; https://www.realinfo.id/market-reports/controlled-bali-demand-shift#market
- Do not write from raw topic alone; write from this insight and source note.

### Opening Sentence Guardrails
- The first line of Final Text is the opening_sentence; do not output a separate Hook block.
- Keep it 5-14 words, concrete, source-specific, and understandable without context.
- It must create tension, recognition, a useful problem, or a precise conflict for the stated audience.
- Do not use tautological openings: no repeated same-root adjective/noun loops such as cheap/cheap, risk/risky, or дешёвый/дешево.
- Banned weak examples: Дешёвый вход на Бали..., Дешёвый риск почти никогда не выглядит дешево, Cheap risk rarely looks cheap.
- If an opening can fit any post, merely restates the topic, or repeats the same semantic hit twice, regenerate it.
- Do not end Final Text with a standalone CTA question; keep review-facing output as final text only.

### Required Output Format
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
- Do not output Hook, CTA, Traceability, or QA sections in the final asset.
````

### workflow_b_market_signal_001 — linkedin_b2b

````markdown
## Writer Entity TZ

### Phase 1 Source Note
- Source ID: workflow_b_market_signal_001
- Source URL: https://www.realinfo.id/market-reports/controlled-bali-demand-shift
- Platform: linkedin_b2b
- Audience: developer_investor
- Content theme: market_reports
- Raw excerpt: Bali hospitality demand is shifting toward longer stays, wellness-led experiences, and properties with credible operator discipline. Developers need evidence of repeat demand and clear management logic before turning a trend into new inventory.

### Phase 2 Insight Card
- Topic: Bali hospitality demand shift toward longer stays, wellness experiences, and operator-disciplined properties
- Angle: Why chasing hospitality trends without demand evidence is the most expensive mistake a Bali developer can make right now
- Emotional Trigger: Status anxiety around being caught holding the wrong asset in a market that has quietly moved on
- Audience Fit: Developer-investors in Bali are actively allocating capital into hospitality product and need a clear framework to separate durable demand signals from trend noise before locking in development decisions
- Useful Lesson: Bali's hospitality market is rewarding developers who can demonstrate repeat demand and credible management systems — not those who simply follow trend cycles into new inventory. Before committing capital, the discipline question must come before the design question.
- Narrative Type: market_observation
- Reuse Score: 4/5
- Confidence: 0.85

### Marketing Research Adaptation
- JTBD / Customer Job: Decide whether to build, hold, or reposition a hospitality asset in Bali based on current demand intelligence
- Pain Point: Fear of developing inventory that looks right on paper but misses the actual demand profile — resulting in underperforming occupancy and weak returns
- Trigger Event: Bali hospitality demand is visibly shifting toward longer-stay and wellness-led profiles, creating pressure to act while also raising the risk of misreading the trend
- Desired Outcome: A clear decision filter that lets them validate demand evidence and operator capability before committing to new hospitality inventory
- Behavioral Trigger: loss_aversion

### Writer Constraints
- Purpose: Build market trust through concrete insight.
- Tone/Register: register_4
- Format: thought_leadership_post
- Opening guide: The cheapest line item in Bali is often the most expensive strategic mistake.
- Key points: Bali's hospitality market is rewarding developers who can demonstrate repeat demand and credible management systems — not those who simply follow trend cycles into new inventory. Before committing capital, the discipline question must come before the design question; Why chasing hospitality trends without demand evidence is the most expensive mistake a Bali developer can make right now; Developer-investors in Bali are actively allocating capital into hospitality product and need a clear framework to separate durable demand signals from trend noise before locking in development decisions; Legal structure changes the deal far more than brochure language suggests.
- Facts allowed: Bali hospitality buyers evaluate management depth, legal structure, occupancy logic, and guest experience before price.; Bali hospitality demand is shifting toward longer stays, wellness-led experiences, and credible operator discipline.
- Reference sources: https://www.realinfo.id/market-reports/controlled-bali-demand-shift#source; https://www.realinfo.id/market-reports/controlled-bali-demand-shift#context; https://www.realinfo.id/market-reports/controlled-bali-demand-shift#ops; https://www.realinfo.id/market-reports/controlled-bali-demand-shift#market
- Do not write from raw topic alone; write from this insight and source note.

### Opening Sentence Guardrails
- The first line of Final Text is the opening_sentence; do not output a separate Hook block.
- Keep it 5-14 words, concrete, source-specific, and understandable without context.
- It must create tension, recognition, a useful problem, or a precise conflict for the stated audience.
- Do not use tautological openings: no repeated same-root adjective/noun loops such as cheap/cheap, risk/risky, or дешёвый/дешево.
- Banned weak examples: Дешёвый вход на Бали..., Дешёвый риск почти никогда не выглядит дешево, Cheap risk rarely looks cheap.
- If an opening can fit any post, merely restates the topic, or repeats the same semantic hit twice, regenerate it.
- Do not end Final Text with a standalone CTA question; keep review-facing output as final text only.

### Required Output Format
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
- Do not output Hook, CTA, Traceability, or QA sections in the final asset.
````

## Workflow B Final Output

### draft_workflow_b_boutique_signal_001_instagram_professional — instagram_professional

```markdown
## Final Content Asset
**Content ID:** content_draft_workflow_b_boutique_signal_001_instagram_professional
**Title:** developer_investor — instagram_professional
**Platform:** instagram
**Pillar:** expertise_proof
**Format:** carousel_caption
**Approval Status:** pending

### Final Text
Серьёзные покупатели на Бали давно перестали начинать разговор с цены.

Прежде чем обсуждать стоимость, они разбирают проект по четырём осям: глубина управления, правовая структура, логика загрузки, качество гостевого опыта. Не по отдельности — как единую систему.

Если продавец или девелопер не может объяснить, как спрос, операционка и стратегия выхода работают вместе, доверие теряется до начала переговоров. Не после. До.

Это не придирки. Это новый порог входа в сегмент.

Рынок бутик-отелей на Бали смещается в сторону длительных stays, wellness-форматов и операторов с дисциплиной. Питч без операционной и exit-логики сегодня читается как слабость, а не как незавершённость.

Правовая структура меняет сделку сильнее, чем любой брошюрный текст.

Проверьте свой проект по этим четырём осям — до того, как это сделает покупатель.
```

### draft_workflow_b_boutique_signal_001_linkedin_b2b — linkedin_b2b

```markdown
## Final Content Asset
**Content ID:** content_draft_workflow_b_boutique_signal_001_linkedin_b2b
**Title:** developer_investor — linkedin_b2b
**Platform:** linkedin
**Pillar:** expertise_proof
**Format:** thought_leadership_post
**Approval Status:** pending

### Final Text
Legal structure reshapes the deal long before price enters the room.

Boutique hotel buyers in Bali have reordered the conversation. Price no longer opens the negotiation — it arrives only after an asset has been tested across four dimensions: management depth, legal structure, occupancy logic, and guest experience. Not as separate checkboxes. As a connected system.

This shift is costly for sellers who prepared a different pitch. A project that leads with aesthetics and closes with yield projections fails the first filter with a rigorous buyer — not because the numbers are wrong, but because there is no coherent answer to one question: how do demand, operations, and exit strategy work together?

Demand in Bali is moving toward longer stays, wellness-led formats, and operators who demonstrate discipline. Sophisticated buyers see this. They ask questions a generic villa cannot answer: who manages, under what legal basis, with what occupancy logic, and what does the exit pathway look like?

If a seller cannot connect those elements into a single narrative before negotiations begin, credibility is gone before the price is named. The competitive threshold has moved. Positioning a project without an operational and exit narrative no longer signals incompleteness — it signals a weak hand.

The market has not become more complex. It has become more precise.
```

### draft_workflow_b_market_signal_001_instagram_professional — instagram_professional

```markdown
## Final Content Asset
**Content ID:** content_draft_workflow_b_market_signal_001_instagram_professional
**Title:** developer_investor — instagram_professional
**Platform:** instagram
**Pillar:** expertise_proof
**Format:** carousel_caption
**Approval Status:** pending

### Final Text
Тренд на Бали не становится активом без доказательства спроса.

Рынок гостеприимства на Бали сместился: гости выбирают длительное проживание, велнес-форматы и объекты с понятной операционной логикой. Девелоперы, которые заходят в новый продукт без подтверждённого повторного спроса, строят под тренд — не под рынок.

Прежде чем фиксировать капитал, стоит ответить на несколько вопросов:

— Есть ли доказательства повторного спроса на этот формат в этой локации?
— Кто управляет объектом и какова глубина их операционной системы?
— Как юридическая структура влияет на доходность — не на бумаге, а в реальной сделке?

Покупатели на Бали оценивают глубину управления, юридическую структуру и логику заполняемости раньше, чем цену.

Дисциплинарный вопрос должен предшествовать дизайнерскому. Иначе красивый проект решает не ту задачу.
```

### draft_workflow_b_market_signal_001_linkedin_b2b — linkedin_b2b

```markdown
## Final Content Asset
**Content ID:** content_draft_workflow_b_market_signal_001_linkedin_b2b
**Title:** developer_investor — linkedin_b2b
**Platform:** linkedin
**Pillar:** expertise_proof
**Format:** thought_leadership_post
**Approval Status:** pending

### Final Text
A Bali trend does not become an asset without evidence of demand.

The hospitality market here has shifted. Guests are staying longer, gravitating toward wellness-led properties, and moving away from short-term inventory that lacks credible operator discipline. This is not a cyclical spike — it is a structural change in the demand profile.

The problem is that most development decisions still run in reverse: concept and design first, management logic and repeat demand evidence second. That is where capital erodes — not in a single moment, but gradually, through weak occupancy, heavy operational load, and assets that read correctly on paper but underperform in practice.

Buyers in this market do not lead with entry price. They evaluate management depth, legal structure, occupancy logic, and guest experience. Legal structure, in particular, reshapes a deal far beyond what any brochure language implies.

The discipline question must come before the design question. Before committing capital to new hospitality inventory, a developer needs clear answers to three things: is there confirmed repeat demand, is there an operating system with proven logic, and will the legal structure hold under a real market cycle.

Bali's hospitality market is rewarding developers who can demonstrate all three — not those who convert trend momentum directly into new inventory.
```

## QA
- workflow_b_only: True
- final_asset_contract_passed: True
- no_tautological_openings: True
- no_duplicate_openings: True
- no_final_cta_questions: True
