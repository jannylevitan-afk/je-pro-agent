# Client Handoff — Content Engine Results + Admin Interface Plan

Date: 2026-04-27  
Project: Je Pro Agent / Content Engine  
Purpose: show the current workflow result and give a simple, practical plan for building the client-facing admin interface.

## 1. Executive Summary

We are building a content operating system that turns researched source material into ready-to-review content assets.

The system is structured around three main layers:

| Layer | What it does | Client value |
|---|---|---|
| Research Agent | Collects and structures source material | The system does not write from random ideas; every output starts from a source signal. |
| Analyst Entity | Converts source material into a clear writing assignment | The writer receives strategy, audience, proof limits, tone, and platform logic. |
| Writer Entity | Produces final content assets | The client receives draft-ready Instagram and LinkedIn posts in the required format. |

The old Notion destination is being removed. The new destination should be a dedicated **Admin Operating Hub** where the client can see, review, approve, edit, and track all results.

## 2. Current Result Snapshot

The latest Workflow B test run was completed successfully.

| Metric | Result |
|---|---|
| Workflow tested | Workflow B — Content Farm |
| Sources processed | 9 |
| Sources approved | 9 |
| Final content assets generated | 17 |
| Missing required themes | 0 |
| Platforms covered | Instagram Lifestyle, Instagram Professional, LinkedIn B2B |
| LinkedIn language policy | English final post + Russian internal master |
| Final status | Draft Ready — Human Review Required |

Full output file:

`outputs/2026-04-26_workflow_b_all_themes_final_assets.md`

Machine-readable JSON:

`outputs/2026-04-26_workflow_b_all_themes_final_assets.json`

## 3. What Was Produced

The system produced all required Workflow B content assets across the agreed content architecture.

| # | Theme | Platform lane | Status |
|---|---|---|---|
| 1 | Founder journey / personal life of entrepreneur | Instagram Lifestyle | Produced |
| 2 | Expert pain in Bali real estate | Instagram Professional | Produced |
| 3 | Expert pain in Bali real estate | LinkedIn B2B | Produced |
| 4 | Land and legal nuance | Instagram Professional | Produced |
| 5 | Land and legal nuance | LinkedIn B2B | Produced |
| 6 | Market reports / market signals | Instagram Professional | Produced |
| 7 | Market reports / market signals | LinkedIn B2B | Produced |
| 8 | Bali travel / lifestyle atmosphere | Instagram Lifestyle | Produced |
| 9 | Global travel and wellness trends | Instagram Professional | Produced |
| 10 | Global travel and wellness trends | LinkedIn B2B | Produced |
| 11 | Wellness architecture / AILLA | Instagram Lifestyle | Produced |
| 12 | Wellness architecture / AILLA | Instagram Professional | Produced |
| 13 | Wellness architecture / AILLA | LinkedIn B2B | Produced |
| 14 | Boutique hotels / hospitality logic | Instagram Professional | Produced |
| 15 | Boutique hotels / hospitality logic | LinkedIn B2B | Produced |
| 16 | Marketing cases / commercial signal | Instagram Professional | Produced |
| 17 | Marketing cases / commercial signal | LinkedIn B2B | Produced |

## 4. Example Output Quality

Each final asset follows the agreed structure:

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

The final Workflow B output intentionally does not include separate `Hook`, `CTA`, `Traceability`, or `QA` sections. The first sentence of `Final Text` acts as the opening line and is generated under strict quality rules:

| Rule | Status |
|---|---|
| Opening sentence is unique per post | Passed |
| Opening sentence is 5-14 words | Passed |
| No generic starts like "Сегодня поговорим..." | Passed |
| No repeated tautology like "дешевый/дешево" | Passed |
| No separate CTA block in final asset | Passed |
| No unsupported invented facts | Guarded by Analyst assignment |

Example opening lines from the completed run:

| Content ID | Platform | Opening sentence |
|---|---|---|
| `wfb-20260426-01` | Instagram Lifestyle | Утро началось раньше, чем закончились вчерашние мысли о проекте. |
| `wfb-20260426-02` | Instagram Professional | Рендер продаёт быстрее, чем инвестор проверяет доходность. |
| `wfb-20260426-03` | LinkedIn B2B | The most photogenic villa in Bali is not automatically an asset. |
| `wfb-20260426-08` | Instagram Lifestyle | Бали меняет расписание раньше, чем ты успеваешь это заметить. |
| `wfb-20260426-13` | LinkedIn B2B | A guest never remembers the material — they remember how their state of mind changed. |
| `wfb-20260426-17` | LinkedIn B2B | A project with a full content calendar can still have nothing to sell. |

## 5. Workflow B Logic In Plain English

Workflow B does not simply ask AI to "write a post."

It works in this order:

1. Research Agent gives the system source material.
2. Analyst Entity checks the source, audience, theme, platform, and evidence limits.
3. Analyst Entity creates a clear Writer Assignment.
4. Writer Entity writes the final content asset from that assignment.
5. Output goes to the Admin Operating Hub for human review.

This is important because it prevents generic AI content. The writer is not allowed to write from a raw topic alone.

## 6. Analyst Assignment Now Includes

Every generated writing task includes:

| Section | Why it matters |
|---|---|
| Writer Assignment ID | Makes each task traceable in the admin. |
| Source Note | Shows what the post is based on. |
| Insight Card | Defines the topic, angle, emotional trigger, audience fit, and useful lesson. |
| Marketing Research Adaptation | Adds JTBD, pain point, trigger event, desired outcome, and behavioral trigger. |
| Strategy Fit | Shows why this belongs to a platform and content lane. |
| Voice/Register Direction | Tells the writer which Jane voice register to use. |
| Fact & Privacy Boundaries | Prevents invented numbers, private details, unsupported claims, and client-name leaks. |
| Writer Constraints | Defines platform, format, language, key points, references, and output rules. |
| Opening Sentence Guardrails | Prevents weak, repeated, generic, or clickbait openings. |

## 7. Admin Interface Goal

The admin should be simple: one operating hub where the client can see what the system found, what it wrote, what needs review, and what is performing.

The admin should not try to be a full social media publishing platform at the beginning.

MVP principle:

```text
Research result -> content asset -> review decision -> calendar -> analytics feedback
```

## 8. Recommended Admin Structure

### 8.1 Dashboard

The dashboard should answer three questions immediately:

| Question | UI element |
|---|---|
| What happened today? | Daily run summary |
| What needs my review? | Review queue |
| What is ready to publish? | Ready assets list |

Recommended dashboard cards:

| Card | Shows |
|---|---|
| New sources collected | Count by platform and theme |
| Assets generated | Count by Workflow A and Workflow B |
| Awaiting review | Drafts needing approve / rewrite / delete / re-brief |
| Ready for publishing | Approved assets grouped by platform |
| Issues | Missing evidence, failed runs, low confidence items |
| Top content signals | Best topics, hooks, themes, and sources |

### 8.2 Source Library

This is where all collected input lives.

Fields to show:

| Field | Description |
|---|---|
| Source ID | Unique source item |
| Platform | Instagram, Telegram, LinkedIn, YouTube, TikTok, Web, Internal |
| Source name | Account, channel, website, or internal note |
| Source URL | Clickable link |
| Raw excerpt | Short source fragment |
| Transcript / caption | Full collected text if available |
| Audience segment | Developer, broker, architect, lifestyle, dreamer woman |
| Content theme | Canonical architecture theme |
| Confidence score | How strong the source is |
| Route | Workflow A, Workflow B, both, or dropped |
| Evidence status | Complete, weak, missing, review required |

Useful filters:

| Filter | Values |
|---|---|
| Platform | Instagram, Telegram, LinkedIn, YouTube, TikTok, Web |
| Workflow route | A, B, both, dropped |
| Theme | Founder, legal, market, wellness, boutique hotels, etc. |
| Evidence status | Complete, weak, missing |
| Date collected | Today, this week, custom |

### 8.3 Workflow B Content Farm

This is the main area for written content.

Recommended layout:

| Column | Meaning |
|---|---|
| Theme | Which architecture category this belongs to |
| Platform | Instagram Lifestyle, Instagram Professional, LinkedIn B2B |
| Title | Generated content title |
| Opening line | First line of final text |
| Status | Draft, needs review, approved, rewrite, deleted |
| Source | Source ID and link |
| Writer assignment | Expandable task spec |
| Final text | Full generated post |
| Reviewer action | Approve, rewrite, delete, re-brief |

Recommended content detail view:

1. Final Content Asset at the top.
2. Reviewer decision buttons.
3. Internal Russian master for LinkedIn.
4. Analyst Assignment collapsed below.
5. Source evidence collapsed below.
6. Version history.

### 8.4 Workflow A Video Pipeline

Workflow A should be separate from Workflow B.

It should show:

| Section | Shows |
|---|---|
| Video source | Link, title, caption, transcript, metrics |
| Hook mining | Extracted first 3 seconds, pattern, tension, promise, CTA, visual device |
| Script output | Selected hook, script, body points, filming notes |
| Filming card | Human filming task |
| Publishing calendar | Manual publication plan |
| Performance | Views, saves, comments, hook performance |

Important: Workflow A video hooks are not part of Workflow B final written posts.

### 8.5 Review Queue

This should be the easiest screen for the client.

Each item needs four actions:

| Action | Meaning |
|---|---|
| Approve | Mark ready for publishing |
| Rewrite | Ask Writer Entity to rewrite with same Analyst Assignment |
| Re-brief | Send back to Analyst Entity because the assignment is wrong |
| Delete | Remove from active queue |

Recommended statuses:

| Status | Meaning |
|---|---|
| Draft Ready | AI output exists and needs human review |
| Approved | Client accepted it |
| Needs Rewrite | Text style or angle needs rewriting |
| Re-brief Needed | Analyst assignment is wrong or incomplete |
| Deleted | Not useful |
| Published Manually | Posted outside the system |

### 8.6 Content Calendar

The calendar does not need automatic publishing in MVP.

It should show:

| Field | Description |
|---|---|
| Publish date | Planned manual date |
| Platform | Instagram, LinkedIn, TikTok, YouTube, Telegram |
| Asset | Linked final content or video script |
| Status | Planned, approved, published manually |
| Pillar | Lifestyle, expertise, market signal, hospitality, wellness |
| Notes | Manual instructions |

### 8.7 Analytics

Analytics can start simple.

Manual performance fields:

| Metric | Why |
|---|---|
| Views | Basic reach |
| Likes | Surface engagement |
| Comments | Conversation signal |
| Saves | Value signal |
| Shares | Resonance signal |
| DMs / leads | Commercial signal |
| Published URL | Link back to live post |

Feedback loop:

```text
Published performance -> best hooks/themes/sources -> Research Agent priorities
```

## 9. MVP Interface Plan

### Phase 1 — Read-Only Result Viewer

Goal: let the client see the system output clearly.

Build:

| Screen | Must include |
|---|---|
| Dashboard | Run summary, assets count, review queue count |
| Workflow B Results | Table of 17 generated assets |
| Asset Detail | Final text, source, analyst assignment, status |

Definition of done:

- Client can open the admin and see all generated Workflow B assets.
- Client can filter by platform and theme.
- Client can open an asset and read the full final text.
- LinkedIn assets show English final text and Russian internal master.

### Phase 2 — Human Review Actions

Goal: let the client make decisions on every asset.

Build:

| Feature | Must include |
|---|---|
| Approve button | Changes status to Approved |
| Rewrite button | Marks as Needs Rewrite |
| Re-brief button | Marks as Re-brief Needed |
| Delete button | Marks as Deleted |
| Review notes | Human can explain what to change |
| Version history | Store previous versions |

Definition of done:

- Every asset has a clear review status.
- Review decisions are saved.
- Client can see what is ready to publish.

### Phase 3 — Research Source Visibility

Goal: make the system trustworthy.

Build:

| Feature | Must include |
|---|---|
| Source Library | All collected source items |
| Evidence panel | URL, timestamp, raw excerpt, confidence |
| Route explanation | Why source went to Workflow A/B/both/drop |
| Risk flags | Missing evidence, compliance concerns, low confidence |

Definition of done:

- Client can click from final asset back to source evidence.
- Unsupported or weak sources are visible instead of hidden.

### Phase 4 — Workflow A Video View

Goal: add video workflow visibility after written content is clear.

Build:

| Feature | Must include |
|---|---|
| Video source table | Video refs, links, captions, transcripts, metrics |
| Hook candidates | Extracted hook patterns |
| Script cards | Ready-to-film scripts |
| Filming queue | Human filming tasks |

Definition of done:

- Workflow A is separated from Workflow B.
- Client can see video hooks/scripts without mixing them into written posts.

### Phase 5 — Calendar + Analytics

Goal: connect content output to performance.

Build:

| Feature | Must include |
|---|---|
| Calendar | Manual publish plan |
| Published URL | Link to live content |
| Performance input | Manual entry for views, saves, comments, shares, DMs |
| Top signals | Best themes, sources, hooks, platforms |

Definition of done:

- Client can see what was published.
- Client can see what performed.
- Research Agent can use performance feedback later.

## 10. Suggested MVP Screens

The first version should have five screens:

| Screen | Priority | Why |
|---|---|---|
| Dashboard | P0 | Gives immediate overview |
| Workflow B Assets | P0 | Shows the written content result |
| Asset Detail | P0 | Lets client review the full output |
| Source Library | P1 | Makes output trustworthy |
| Calendar / Analytics | P1 | Prepares performance loop |

Workflow A can be a sixth screen once Workflow B review is comfortable.

## 11. Data Objects Needed For Interface

### Source Item

| Field | Type |
|---|---|
| source_id | string |
| source_url | string |
| source_name | string |
| source_type | string |
| collected_at | datetime |
| raw_excerpt | text |
| transcript_text | text |
| engagement_signals | object |
| audience_segment | string |
| content_theme | string |
| routing_decision | enum |
| routing_confidence | number |
| evidence_status | enum |

### Writer Assignment

| Field | Type |
|---|---|
| writer_assignment_id | string |
| source_id | string |
| canonical_theme | string |
| platform_lane | enum |
| publish_language | enum |
| internal_language | enum |
| primary_audience | string |
| secondary_audience | string |
| funnel_role | enum |
| strategy_fit | text |
| voice_register | string |
| fact_boundaries | text |
| opening_guardrails | text |

### Final Content Asset

| Field | Type |
|---|---|
| content_id | string |
| title | string |
| platform | string |
| platform_lane | enum |
| pillar | string |
| format | string |
| approval_status | enum |
| final_text | text |
| internal_ru_master | text, optional |
| source_id | string |
| writer_assignment_id | string |
| version | number |
| created_at | datetime |
| updated_at | datetime |

### Review Decision

| Field | Type |
|---|---|
| review_id | string |
| content_id | string |
| decision | approve / rewrite / re-brief / delete |
| review_notes | text |
| reviewer | string |
| reviewed_at | datetime |

### Performance Record

| Field | Type |
|---|---|
| performance_id | string |
| content_id | string |
| platform | string |
| published_url | string |
| published_at | datetime |
| views | number |
| likes | number |
| comments | number |
| saves | number |
| shares | number |
| dms_or_leads | number |

## 12. Recommended UI Style

The interface should feel like an operating room for content, not like a social media feed.

Recommended direction:

| Area | Recommendation |
|---|---|
| Visual style | Clean editorial dashboard, premium, calm, not playful |
| Information density | Medium; enough detail for decisions, not clutter |
| Primary colors | Neutral base with one accent for statuses |
| Tables | Clear filters, sticky headers, quick status badges |
| Detail pages | Final output first, evidence second, technical details collapsed |
| Tone | Professional and simple |

Avoid:

- overcomplicated automation screens;
- social-network clone UI;
- showing every internal model detail by default;
- mixing Workflow A video hooks into Workflow B written posts;
- making the client search through JSON or technical logs.

## 13. Client Review Flow

Recommended daily flow:

1. Client opens Dashboard.
2. Client checks "Awaiting Review."
3. Client opens one asset.
4. Client reads Final Text first.
5. Client expands Analyst Assignment only if they want to inspect logic.
6. Client expands Source Evidence only if they want to verify source.
7. Client chooses Approve, Rewrite, Re-brief, or Delete.
8. Approved items move to Calendar.
9. After manual publishing, performance is entered.
10. Analytics informs the next Research Agent run.

## 14. What The Interface Should Not Do In MVP

Do not build these first:

| Feature | Why not first |
|---|---|
| Automatic publishing | Adds platform risk and complexity too early |
| Full CRM | Not required to validate content workflow |
| Complex role permissions | One admin/reviewer role is enough initially |
| Prompt marketplace | Internal system can manage prompts for now |
| Notion sync | Deprecated destination |
| AI chat over everything | Nice later, not needed for first usable admin |

## 15. Acceptance Criteria For First Client Demo

The first demo is successful if the client can:

1. See that the system generated 17 Workflow B content assets.
2. Filter assets by platform and theme.
3. Open one asset and read the final post.
4. See LinkedIn English final text and Russian internal master.
5. Understand which source and Analyst Assignment created the asset.
6. Approve, request rewrite, re-brief, or delete the asset.
7. See what is ready for manual publishing.

## 16. Current Files To Use

| File | Purpose |
|---|---|
| `outputs/2026-04-26_workflow_b_all_themes_final_assets.md` | Human-readable final Workflow B results |
| `outputs/2026-04-26_workflow_b_all_themes_final_assets.json` | Structured data for interface prototyping |
| `.codex/agents/analyst_entity.md` | Analyst Entity behavior and required output contract |
| `src/content_engine/services/analyst.py` | Code that builds Writer Assignments |
| `docs/handoffs/2026-04-26-admin-panel-gpt-handoff.md` | Detailed technical admin-panel handoff |

## 17. Recommended Next Step

Build a clickable admin prototype around the existing JSON result first.

The first prototype should not need live integrations. It can load:

```text
outputs/2026-04-26_workflow_b_all_themes_final_assets.json
```

Then display:

1. Dashboard summary.
2. Workflow B asset table.
3. Asset detail view.
4. Review actions.
5. Source/Analyst panels.

Once this is approved visually and functionally, connect it to live backend data.

## 18. Plain Client Explanation

The system is already able to take structured source material, analyze it, and produce platform-specific draft content across the full content architecture.

The next product step is not to add more AI complexity. The next step is to create a clean admin interface where the client can control the workflow:

```text
See source -> see insight -> see final content -> approve or request changes -> track publishing -> feed performance back into research
```

That is the simplest professional version of the product.
