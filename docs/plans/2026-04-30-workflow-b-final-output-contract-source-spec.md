# Workflow B — Content Farm Final Output Contract for Codex

> Agent-first status: historical/source contract input.
> This file contains older Notion/Content Calendar language and may conflict
> with the current Admin Operating Hub direction.
>
> Canonical current rules live in `AGENTS.md`,
> `docs/architecture/2026-04-29-content-factory-producer-restructure.md`, and
> current Workflow B model/service tests. Use this file only to mine useful
> contract ideas, not as the active final-output schema.

**Version:** 1.0  
**Purpose:** define the exact final output structure for Workflow B so Codex can implement the Content Farm pipeline and the final Notion/DB table.

---

## 1. Context

Workflow B is the **Content Farm** branch. It receives raw text signals, market insights, founder angles, and source notes from the Research Agent. Its job is not to publish content automatically. Its job is to transform raw inputs into approved, platform-ready content assets and place them into the final **Content Calendar** table.

Publishing is **manual**. The system prepares, validates, versions, and queues the content.

```text
Research Agent
  ↓
Workflow B — Content Farm
  ↓
Phase 1 — Intake + Structure
  ↓
Phase 2 — Insight Extraction
  ↓
Phase 3 — Idea Generation
  ↓
Phase 4 — Content Brief
  ↓
Phase 5 — Draft Generation
  ↓
Phase 6 — AI Editing Layer
  ↓
Phase 7 — Human Review
  ↓
Final Output — Content Calendar table
```

---

## 2. Workflow B Phase Responsibilities

| Phase | Name | Main Function | Output Object | Gate |
|---|---|---|---|---|
| 1 | Intake + Structure | Receive raw data from Research Agent, deduplicate, normalize, and create source note | `source_note` | Source must be readable and non-duplicate |
| 2 | Insight Extraction | Extract topic, angle, emotional trigger, audience fit, hidden tension, promise, risk | `insight_card` | Insight must have clear value and emotional trigger |
| 3 | Idea Generation | Generate 3–5 ideas from one insight | `ideas[]` + `selected_idea` | Kill weak ideas with no value/emotion |
| 4 | Content Brief | Convert selected idea into a production-ready brief | `content_brief` | Brief must include platform, hook, CTA, structure, voice, facts |
| 5 | Draft Generation | Write first draft from the brief only | `draft` | Draft must follow platform logic and not invent facts |
| 6 | AI Editing Layer | Tighten, sharpen, remove generic AI language, preserve author voice | `edited_version` | Final text must pass QA checks |
| 7 | Human Review | Human approves, rewrites, deletes, or sends back to re-brief | `review_decision` | Only approved content enters publishing queue |

---

## 3. Final Output Database

Final output must be stored in one primary table:

```text
Content Calendar
```

This is the **final production table** for Workflow B.

One row = one final content asset prepared for one platform.

If the same idea is adapted for 4 platforms, the system must create **4 separate Content Calendar rows**, because each platform has its own hook, format, CTA, length, and publish status.

---

## 4. Final Output Table — Exact Schema

### 4.1. Required Display Columns

These are the columns that should be visible in the main Notion/DB view.

| Column | Type | Required | Example | Description |
|---|---:|---:|---|---|
| `content_id` | string | yes | `cnt_20260425_001` | Stable unique ID for this content asset |
| `title` | string | yes | `Why cheap Bali property becomes expensive later` | Internal title for quick scanning |
| `platform` | enum | yes | `LinkedIn` | Target platform |
| `content_pillar` | enum/string | yes | `market_insight` | Strategic content category |
| `format` | enum | yes | `post` | Output format |
| `final_text` | long_text | yes | full final post text | Approved or review-ready final text |
| `hook` | string | yes | `Cheap Bali property is usually expensive twice.` | First line / opening hook |
| `cta` | string | no | `DM me “BALI” for the checklist.` | Final call to action |
| `publish_date` | date | no | `2026-04-28` | Planned publishing date |
| `publish_time` | time | no | `10:30` | Planned local posting time |
| `approval_status` | enum | yes | `approved` | Human approval state |
| `publish_status` | enum | yes | `ready_to_publish` | Operational publishing state |
| `owner` | string | no | `content_manager` | Human responsible for final action |
| `human_review_required` | boolean | yes | `true` | Whether human review is mandatory |
| `qa_score` | number | yes | `8.7` | Final quality score from 0–10 |
| `risk_level` | enum | yes | `medium` | Brand/fact/legal risk level |
| `created_at` | datetime | yes | `2026-04-25T12:10:00+08:00` | Row creation time |
| `updated_at` | datetime | yes | `2026-04-25T12:32:00+08:00` | Last update time |

---

### 4.2. Required Backend Columns

These columns are needed for traceability, debugging, analytics, and safe automation.

| Column | Type | Required | Source Phase | Description |
|---|---:|---:|---|---|
| `source_ids` | string[] | yes | Phase 1 | Linked IDs from Sources DB / Research Agent |
| `insight_id` | string | yes | Phase 2 | Linked Insight Card ID |
| `idea_id` | string | yes | Phase 3 | Linked selected Idea ID |
| `brief_id` | string | yes | Phase 4 | Linked Content Brief ID |
| `draft_id` | string | yes | Phase 5 | Linked Draft ID |
| `edit_version_id` | string | yes | Phase 6 | Linked edited version ID |
| `review_id` | string | no | Phase 7 | Human review record ID |
| `source_summary` | text | yes | Phase 1 | Short summary of original source material |
| `topic` | string | yes | Phase 2 | Extracted topic |
| `angle` | string | yes | Phase 2 | Specific framing of the topic |
| `emotional_trigger` | string | yes | Phase 2 | Main emotion that makes audience care |
| `audience_fit` | text | yes | Phase 2 | Why this matters to the audience |
| `hidden_tension` | text | yes | Phase 2 | Conflict / pain / contradiction behind the idea |
| `promise` | text | yes | Phase 2 | What reader will gain or understand |
| `target_audience` | string | yes | Phase 4 | Audience segment |
| `goal` | enum | yes | Phase 4 | `authority`, `sales`, `engagement`, `nurture`, `education`, `leads` |
| `voice_register` | string | yes | Phase 4 | Selected author/content voice register |
| `tone_of_voice` | string | yes | Phase 4 | Practical tone instructions |
| `language` | enum | yes | Phase 4 | `ru`, `en`, `id`, etc. |
| `length` | enum | yes | Phase 4 | `short`, `medium`, `long` |
| `structure` | string[] | yes | Phase 4 | Planned content structure |
| `required_facts` | string[] | no | Phase 4 | Facts that must be used |
| `forbidden_facts` | string[] | no | Phase 4 | Facts that must not be used |
| `avoid` | string[] | yes | Phase 4 | Forbidden phrases, clichés, weak patterns |
| `draft_text` | long_text | yes | Phase 5 | First draft before editing |
| `edited_text` | long_text | yes | Phase 6 | AI-edited text before human decision |
| `final_text` | long_text | yes | Phase 7 | Final approved/review-ready text |
| `hook_options` | string[] | no | Phase 6 | Alternative hooks |
| `cta_options` | string[] | no | Phase 6 | Alternative CTAs |
| `qa_passed` | boolean | yes | Phase 6/7 | Whether QA passed |
| `qa_issues` | string[] | no | Phase 6/7 | Remaining issues |
| `fixes_applied` | string[] | no | Phase 6 | What editor changed |
| `fact_risks` | string[] | no | Phase 6/7 | Unsupported facts, numbers, client mentions, legal risk |
| `do_not_publish_reason` | text | no | Phase 7 | Required if status is killed/blocked |
| `reuse_score` | number | no | Analytics | How reusable this angle is from 0–10 |
| `performance_feedback` | text | no | Analytics | Manual or automated post-performance notes |

---

## 5. Enums

### 5.1. `platform`

```ts
type Platform =
  | "Instagram"
  | "LinkedIn"
  | "Telegram"
  | "TikTok"
  | "YouTube"
  | "YouTube Shorts";
```

### 5.2. `format`

```ts
type ContentFormat =
  | "post"
  | "caption"
  | "carousel"
  | "short_video_script"
  | "thread"
  | "newsletter_snippet"
  | "story"
  | "reel_caption";
```

### 5.3. `approval_status`

```ts
type ApprovalStatus =
  | "draft"
  | "needs_review"
  | "approved"
  | "rewrite_requested"
  | "rebrief_requested"
  | "deleted"
  | "blocked";
```

### 5.4. `publish_status`

```ts
type PublishStatus =
  | "not_ready"
  | "ready_to_publish"
  | "scheduled_manually"
  | "published"
  | "skipped";
```

### 5.5. `risk_level`

```ts
type RiskLevel = "low" | "medium" | "high";
```

### 5.6. `goal`

```ts
type ContentGoal =
  | "authority"
  | "sales"
  | "engagement"
  | "nurture"
  | "education"
  | "leads"
  | "personal_brand";
```

---

## 6. Final Output JSON Contract

Codex should use this object as the canonical final output contract.

```ts
export interface WorkflowBFinalOutput {
  // Identity
  content_id: string;
  title: string;

  // Relations
  source_ids: string[];
  insight_id: string;
  idea_id: string;
  brief_id: string;
  draft_id: string;
  edit_version_id: string;
  review_id?: string;

  // Final publishing table fields
  platform: Platform;
  content_pillar: string;
  format: ContentFormat;
  language: string;
  target_audience: string;
  goal: ContentGoal;

  // Strategic fields
  source_summary: string;
  topic: string;
  angle: string;
  emotional_trigger: string;
  audience_fit: string;
  hidden_tension: string;
  promise: string;

  // Voice and structure
  voice_register: string;
  tone_of_voice: string;
  length: "short" | "medium" | "long";
  structure: string[];
  required_facts: string[];
  forbidden_facts: string[];
  avoid: string[];

  // Text outputs
  hook: string;
  draft_text: string;
  edited_text: string;
  final_text: string;
  cta?: string;
  hook_options?: string[];
  cta_options?: string[];

  // Review and QA
  approval_status: ApprovalStatus;
  publish_status: PublishStatus;
  human_review_required: boolean;
  qa_passed: boolean;
  qa_score: number;
  risk_level: RiskLevel;
  qa_issues?: string[];
  fixes_applied?: string[];
  fact_risks?: string[];
  do_not_publish_reason?: string;

  // Scheduling
  publish_date?: string;
  publish_time?: string;
  owner?: string;

  // Analytics / feedback loop
  reuse_score?: number;
  performance_feedback?: string;

  // System metadata
  created_at: string;
  updated_at: string;
}
```

---

## 7. Minimal Final Output Object

If the UI needs a compact version, use this minimum contract.

```json
{
  "content_id": "cnt_20260425_001",
  "title": "",
  "platform": "LinkedIn",
  "content_pillar": "",
  "format": "post",
  "final_text": "",
  "hook": "",
  "cta": "",
  "publish_date": "",
  "publish_time": "",
  "approval_status": "needs_review",
  "publish_status": "not_ready",
  "human_review_required": true,
  "qa_score": 0,
  "risk_level": "medium",
  "source_ids": [],
  "insight_id": "",
  "idea_id": "",
  "brief_id": "",
  "draft_id": "",
  "edit_version_id": "",
  "created_at": "",
  "updated_at": ""
}
```

---

## 8. Final Table Example

| content_id | title | platform | content_pillar | format | hook | final_text | cta | publish_date | approval_status | publish_status | qa_score | risk_level |
|---|---|---|---|---|---|---|---|---|---|---:|---:|---|
| `cnt_20260425_001` | `Cheap Bali property becomes expensive twice` | `LinkedIn` | `market_insight` | `post` | `Cheap Bali property is usually expensive twice.` | `Full final text goes here...` | `DM me “BALI” for the checklist.` | `2026-04-28` | `approved` | `ready_to_publish` | `8.7` | `medium` |

---

## 9. Gate Rules Before Creating Final Row

The system may create a final Content Calendar row only if all conditions are true:

```text
1. source_note exists
2. insight_card exists
3. selected_idea exists
4. content_brief exists
5. draft exists
6. edited_version exists
7. QA has run
8. final_text is not empty
9. platform is defined
10. approval_status is defined
11. publish_status is defined
12. no unsupported facts were introduced
13. no forbidden phrases are present
14. human_review_required is true for risky content
```

If any condition fails, route the item back to the correct phase:

| Failure | Route Back To |
|---|---|
| Source is unclear | Phase 1 — Intake + Structure |
| Insight is generic | Phase 2 — Insight Extraction |
| Idea has no emotional trigger | Phase 3 — Idea Generation |
| Brief lacks platform/CTA/structure | Phase 4 — Content Brief |
| Draft ignores brief | Phase 5 — Draft Generation |
| Text sounds generic or off-voice | Phase 6 — AI Editing Layer |
| Risky or questionable content | Phase 7 — Human Review |

---

## 10. Human Review Logic

Human review is mandatory when:

```text
- content references money, investment, deals, clients, medical/legal/financial claims
- content is written from a specific founder voice
- content uses personal biography
- risk_level is medium or high
- qa_score is below 8
- fact_risks is not empty
- final content will affect brand positioning
```

Human reviewer can choose:

```ts
type HumanDecision =
  | "approve"
  | "rewrite"
  | "delete"
  | "rebrief";
```

Decision mapping:

| Human Decision | `approval_status` | `publish_status` | Next Step |
|---|---|---|---|
| `approve` | `approved` | `ready_to_publish` | Manual publishing |
| `rewrite` | `rewrite_requested` | `not_ready` | Back to Phase 6 |
| `delete` | `deleted` | `skipped` | Stop |
| `rebrief` | `rebrief_requested` | `not_ready` | Back to Phase 4 |

---

## 11. Final Formatter Rules

The Final Formatter must output both:

1. Human-readable Markdown summary.
2. Machine-readable JSON object.

### 11.1. Markdown Summary

```markdown
## Final Content Asset

**Content ID:**  
**Title:**  
**Platform:**  
**Pillar:**  
**Format:**  
**Approval Status:**  
**Publish Status:**  
**Risk Level:**  
**QA Score:**  

### Hook

...

### Final Text

...

### CTA

...

### Traceability

- Source IDs:
- Insight ID:
- Idea ID:
- Brief ID:
- Draft ID:
- Edit Version ID:

### QA

- Passed:
- Issues:
- Human Review Required:
```

### 11.2. JSON Output

```json
{
  "content_id": "",
  "title": "",
  "source_ids": [],
  "insight_id": "",
  "idea_id": "",
  "brief_id": "",
  "draft_id": "",
  "edit_version_id": "",
  "platform": "",
  "content_pillar": "",
  "format": "",
  "language": "",
  "target_audience": "",
  "goal": "",
  "source_summary": "",
  "topic": "",
  "angle": "",
  "emotional_trigger": "",
  "audience_fit": "",
  "hidden_tension": "",
  "promise": "",
  "voice_register": "",
  "tone_of_voice": "",
  "length": "",
  "structure": [],
  "required_facts": [],
  "forbidden_facts": [],
  "avoid": [],
  "hook": "",
  "draft_text": "",
  "edited_text": "",
  "final_text": "",
  "cta": "",
  "hook_options": [],
  "cta_options": [],
  "approval_status": "needs_review",
  "publish_status": "not_ready",
  "human_review_required": true,
  "qa_passed": false,
  "qa_score": 0,
  "risk_level": "medium",
  "qa_issues": [],
  "fixes_applied": [],
  "fact_risks": [],
  "do_not_publish_reason": "",
  "publish_date": "",
  "publish_time": "",
  "owner": "",
  "reuse_score": 0,
  "performance_feedback": "",
  "created_at": "",
  "updated_at": ""
}
```

---

## 12. Notion Database Views

Recommended views for the final Content Calendar table:

| View Name | Filter | Sort | Purpose |
|---|---|---|---|
| `Needs Review` | `approval_status = needs_review` | `updated_at desc` | Human checks final texts |
| `Ready To Publish` | `approval_status = approved` + `publish_status = ready_to_publish` | `publish_date asc` | Manual publishing queue |
| `Platform Calendar` | grouped by `platform` | `publish_date asc` | See content by platform |
| `High Risk` | `risk_level = high` OR `fact_risks is not empty` | `updated_at desc` | Safety check |
| `Rewrite Queue` | `approval_status = rewrite_requested` | `updated_at desc` | Send back to editor |
| `Rebrief Queue` | `approval_status = rebrief_requested` | `updated_at desc` | Send back to brief builder |
| `Published` | `publish_status = published` | `publish_date desc` | Archive and analytics |

---

## 13. Implementation Notes for Codex

1. Treat every phase output as a separate object with a stable ID.
2. Never overwrite previous drafts. Create versions.
3. Do not create a final Content Calendar row directly from raw source material.
4. Final row must always contain traceability fields.
5. `final_text` must come from Phase 6 or Phase 7 only.
6. If `approval_status !== "approved"`, keep `publish_status = "not_ready"` unless manually overridden.
7. Publishing remains manual. Do not auto-post from this workflow.
8. For each platform adaptation, create a separate final row.
9. If QA fails, do not mark as `ready_to_publish`.
10. If facts are unsupported, either remove them or set `approval_status = blocked`.

---

## 14. Acceptance Criteria

Codex implementation is correct if:

```text
- Workflow B creates structured phase outputs from source → insight → idea → brief → draft → edit → review.
- Final Content Calendar row is created only after QA.
- Final row includes final_text, platform, pillar, publish date, approval status, QA, and traceability IDs.
- The UI can show a clean table for humans.
- The backend can reconstruct how each final text was produced.
- Risky content cannot silently enter ready_to_publish.
- Manual publishing remains the last step.
```
