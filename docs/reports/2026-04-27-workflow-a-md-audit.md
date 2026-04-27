# Workflow A Markdown Audit Report

Date: 2026-04-27  
Scope: all project `.md` files, including hidden `.agents` / `.codex` markdown files.  
Focus: Workflow A — Video Pipeline requirements, criteria, structure, and expected output.

## 1. What Was Reviewed

I scanned the project markdown files with:

```bash
rg --files --hidden -g '*.md'
rg -n -i --hidden 'workflow a|workflow_a|video pipeline|video refs|hook mining|video intake|first 3 seconds|visual device|filming card|script_ready|video-native|publish queue|video hooks' -g '*.md'
```

### Most Relevant Files

| File | Relevance |
|---|---|
| `content_engine_architecture_v3.md` | Primary architecture for Research Agent routing and Workflow A steps. |
| `AGENTS.md` | Operating rules: evidence, routing, MCP stack, Workflow A handoff criteria. |
| `README.md` | Runtime notes for Workflow A video intake and script-ready payloads. |
| `.agents/skills/video-intake-skill/SKILL.md` | Workflow A video source intake contract. |
| `.agents/skills/hook-mining-skill/SKILL.md` | Hook mining fields and quality rules. |
| `.agents/skills/routing-skill/SKILL.md` | Routing decision rules into Workflow A / B / both / drop. |
| `.agents/skills/evidence-log-skill/SKILL.md` | Minimum evidence payload before handoff. |
| `writer_entity_combined_technical_spec.md` | Optional Video Top Hooks + Topics generator and quality gate. |
| `docs/superpowers/plans/2026-04-24-workflow-a-video-pipeline-implementation.md` | Implementation plan for deterministic Workflow A core. |
| `docs/handoffs/2026-04-27-client-results-interface-handoff.md` | Admin UI expectations for Workflow A. |
| `outputs/2026-04-26_analyst_layer_run_kmd/workflow_a/...kmd.md` | Example KMD source-note handoff for Workflow A. |
| `outputs/2026-04-27_workflow_a_only_video_run.md` | Latest Workflow A test run output. |

### Less Relevant / Boundary Files

| File | Why less relevant |
|---|---|
| `.codex/agents/analyst_entity.md` | Defines Workflow B Analyst boundaries and explicitly says video hooks/scripts belong to Workflow A. Useful for separation only. |
| `content_farm_workflow_spec.md` and duplicate `(1)` | Mostly Workflow B/content farm. Hook logic is general, but not the main Workflow A contract. |
| `Voice_Jane_Levitan_Agent.md` | Voice/register guidance; useful for tone and Reels style, not the Workflow A data model. |
| `target-audience-portraits.md` | Audience behavior for Reels/video consumption; useful for platform fit, not pipeline structure. |
| Workflow B output files | Not Workflow A except where they show boundaries or mixed-route examples. |

## 2. Core Workflow A Definition

The architecture defines Workflow A as the **Video Pipeline**.

Primary purpose:

```text
Produce ready-to-film short-form video scripts.
```

Supported platforms:

```text
Instagram Reels, TikTok, YouTube Shorts, LinkedIn Video
```

Source:

```text
Research Agent collects data.
Workflow A does not search.
Workflow A receives prepared video-native source items.
```

Reference:

- `content_engine_architecture_v3.md:3-5` — Research Agent searches; workflows only process; publishing is manual.
- `content_engine_architecture_v3.md:512-515` — Workflow A purpose and supported platforms.
- `README.md:24-28` — runtime notes for source tagging, Workflow A intake, and script-ready outputs.

## 3. Canonical Workflow A Flow

The strongest consolidated flow from the markdown files is:

```text
Research Agent
  -> compliance + evidence check
  -> video intake
  -> hook mining
  -> hook candidates
  -> best hook
  -> script
  -> filming card
  -> manual filming
  -> publish queue / calendar
  -> manual publishing
  -> performance measurement
  -> feedback loop to Research Agent
```

### Required Stages

| Stage | Source in docs | What it should do |
|---|---|---|
| Research Agent collection | `content_engine_architecture_v3.md:38-42`, `AGENTS.md:10-23` | Collect, verify, route. Workflows do not search. |
| Evidence gate | `AGENTS.md:14-18`, `.agents/skills/evidence-log-skill/SKILL.md:12-24` | Require URL, timestamp, raw excerpt, confidence score. |
| Routing | `content_engine_architecture_v3.md:499-508`, `.agents/skills/routing-skill/SKILL.md:10-22` | Video refs go to Workflow A; strong video + text goes to both; weak drops. |
| Video intake | `.agents/skills/video-intake-skill/SKILL.md:8-42` | Normalize video refs, title, caption/transcript, media URLs, metrics, raw payload. |
| Hook mining | `.agents/skills/hook-mining-skill/SKILL.md:8-26` | Extract first 3 seconds, pattern, tension, promise, CTA, visual device, repeatable formula. |
| Develop hooks | `content_engine_architecture_v3.md:517-519` | 1 topic -> 5 angles -> best hook. |
| Script | `content_engine_architecture_v3.md:521-523` | Script with proven pattern: hook -> body -> CTA; fact-check before filming. |
| Filming card | `content_engine_architecture_v3.md:525-526` | Ranked card for human filming. |
| Publish | `content_engine_architecture_v3.md:528-529` | Human publishes manually; system does not publish. |
| Measure | `content_engine_architecture_v3.md:531-536` | Daily stats; top hooks/topics feed back to Research Agent. |

## 4. Input Criteria Before Workflow A

Workflow A should only receive prepared items that pass minimum evidence and routing checks.

### Required Evidence

Every source-derived item needs:

| Field | Required by |
|---|---|
| source URL | `AGENTS.md:14-18`, `.agents/skills/evidence-log-skill/SKILL.md:12-17` |
| timestamp / collection date | `AGENTS.md:14-18`, `.agents/skills/evidence-log-skill/SKILL.md:12-17` |
| raw excerpt | `AGENTS.md:14-18`, `.agents/skills/evidence-log-skill/SKILL.md:12-17` |
| confidence score | `AGENTS.md:14-18`, `.agents/skills/evidence-log-skill/SKILL.md:12-17` |
| canonical upstream item | `.agents/skills/evidence-log-skill/SKILL.md:21-24` |

If evidence is missing, the item should be dropped or held for review.

### Required SourceItem Shape

The architecture defines a canonical collected item with:

| Field group | Required fields |
|---|---|
| Identity | `item_id`, `external_item_id`, `dedupe_key`, `content_hash` |
| Source | `source_type`, `source_name`, `source_url`, `raw_payload` |
| Timing | `collected_at`, `published_at` |
| Content | `transcript_text`, `media_urls` |
| Context | `audience_segment`, `content_theme` |
| Engagement | `engagement_signals` |
| Routing | `routing_decision`, `routing_reason`, `routing_confidence` |
| State | `processing_state` |

Reference: `content_engine_architecture_v3.md:84-120`.

### Video Intake-Specific Fields

Workflow A needs the video-specific fields from `video-intake-skill`:

| Field | Meaning |
|---|---|
| video refs | Original video URL + media URLs |
| source links | URL back to the public source |
| video title | Native or extracted title |
| caption text | Platform caption or description |
| spoken transcript | Public transcript if available |
| transcript source | Where transcript came from |
| metadata | Platform/source metadata |
| comments | Public comments when available and safe |
| visual hints | What is visible / filming pattern |
| hook signals | Source hook, first 3 seconds, opening |
| public metrics | views, likes, comments, saves, shares |

Reference: `.agents/skills/video-intake-skill/SKILL.md:12-36`.

## 5. Routing Criteria

Workflow A receives:

| Signal | Route |
|---|---|
| Video refs | Workflow A |
| Trending video formats | Workflow A |
| Hooks for video | Workflow A |
| Strong video + strong text depth | Both Workflow A and Workflow B |
| Weak / unsupported signal | Drop |

References:

- `content_engine_architecture_v3.md:499-508`
- `.agents/skills/routing-skill/SKILL.md:10-22`
- `AGENTS.md:19-23`

Important: if one upstream item supports both workflows, it stays one canonical source item, but downstream packaging is separate. Reference: `content_engine_architecture_v3.md:116-120`.

## 6. Workflow A Must Stay Separate From Workflow B

This is repeated in multiple docs and is important.

Workflow A:

```text
video-native source -> hook mining -> video script -> filming card
```

Workflow B:

```text
text insight -> analyst assignment -> final written content asset
```

Boundary rules:

| Rule | Source |
|---|---|
| Workflow B Writer Entity does not write video hooks/scripts | `content_engine_architecture_v3.md:702-708` |
| Analyst Entity should note that video hooks/scripts belong to Workflow A | `.codex/agents/analyst_entity.md:72-76` |
| Do not merge Workflow A video hooks into Workflow B writing tasks | `.codex/agents/analyst_entity.md:141-145` |
| Admin must not mix Workflow A video hooks into Workflow B written posts | `docs/handoffs/2026-04-27-client-results-interface-handoff.md:229-244`, `docs/handoffs/2026-04-27-client-results-interface-handoff.md:517-523` |

## 7. Hook Mining Requirements

Workflow A hook mining is not just "write a hook." It should extract reusable hook structure from video-native material.

Required extraction:

| Field | Meaning |
|---|---|
| first 3 seconds | What viewer sees/hears immediately |
| pattern | Repeatable hook structure |
| tension | What conflict/problem pulls attention |
| promise | What the viewer expects to get |
| CTA | Action logic or closing direction |
| visual device | What visual mechanism makes it watchable |
| repeatable formula | How this hook can be reused safely |

Reference: `.agents/skills/hook-mining-skill/SKILL.md:12-20`.

Hook rules:

| Rule | Source |
|---|---|
| Reusable pattern, not theft | `.agents/skills/hook-mining-skill/SKILL.md:22-26` |
| Preserve why hook works: contrast, curiosity, proof, authority, identity, tension | `.agents/skills/hook-mining-skill/SKILL.md:22-26` |
| Flag visual-first, text-first, or hybrid | `.agents/skills/hook-mining-skill/SKILL.md:22-26` |
| First 1-2 seconds should create tension/curiosity | `writer_entity_combined_technical_spec.md:1215-1222` |
| Hook must be concrete and deliverable | `writer_entity_combined_technical_spec.md:1215-1222` |

## 8. Hook Types Found Across Docs

### Architecture / Current Service Style

The current Workflow A service uses these hook families:

| Hook type | Purpose |
|---|---|
| market_warning | Warning / market reality check |
| story_moment | Human or narrative moment |
| tactical_tip | Practical advice |
| data_stat_callout | Data/proof-style callout |
| bts_fragment | Behind-the-scenes signal |

These align with architecture content atoms:

| Atom type | Workflow A fit |
|---|---|
| Story moment | Reel hook |
| Tactical tip | Educational Reel |
| BTS fragment | Instagram lifestyle lane / Workflow A |

Reference: `content_engine_architecture_v3.md:1030-1047`.

### Writer Entity Video Module Hook Types

The broader Writer Entity spec lists more hook types:

| Hook type |
|---|
| Contrarian |
| Pain-point |
| Curiosity gap |
| Mistake-based |
| Identity-based |
| Data/Proof-based |
| Transformation |
| Warning |
| Myth-busting |
| Direct benefit |
| Status/aspiration |
| Story opening |
| Founder confession |
| Market reality check |
| Insider recommendation |

Reference: `writer_entity_combined_technical_spec.md:1198-1214`.

## 9. Script Requirements

The canonical script pattern is:

```text
hook -> body -> CTA
```

Requirements:

| Requirement | Source |
|---|---|
| Use proven pattern: hook -> body -> CTA | `content_engine_architecture_v3.md:521-523` |
| Fact-check before filming | `content_engine_architecture_v3.md:521-523` |
| TikTok / YouTube Shorts should be spoken scripts | `writer_entity_combined_technical_spec.md:880-884` |
| First 2 seconds create curiosity | `writer_entity_combined_technical_spec.md:880-884` |
| One idea only | `writer_entity_combined_technical_spec.md:880-884` |
| Retention turn every 2-3 sentences | `writer_entity_combined_technical_spec.md:880-884` |
| For Instagram, use hook -> tension -> payoff | `writer_entity_combined_technical_spec.md:867-873` |

The script should be ready for filming, not just a text draft. That means it should include:

| Script component | Why |
|---|---|
| selected hook | starts the video |
| spoken body | what the person says |
| visual/filming cue | what should be shown |
| CTA | save/share/comment/DM/manual next step |
| fact boundary | no unsupported claims |
| platform | Instagram / TikTok / YouTube Shorts / LinkedIn Video |

## 10. Filming Card Requirements

A filming card is a human production task.

Required fields from architecture:

| Field | Source |
|---|---|
| linked script | `content_engine_architecture_v3.md:1620-1626` |
| shoot date | `content_engine_architecture_v3.md:1620-1626` |
| filmed checkbox/status | `content_engine_architecture_v3.md:1620-1626` |
| raw file link | `content_engine_architecture_v3.md:1620-1626` |
| filming priority | `content_engine_architecture_v3.md:1610-1618` |

Admin UI should expose this as a human filming task. Reference: `docs/handoffs/2026-04-27-client-results-interface-handoff.md:237-241`.

## 11. Publish Queue / Calendar Requirements

Workflow A does not publish automatically.

Publishing requirement:

```text
Human publishes manually.
System prepares publish-ready asset and calendar item.
```

Required publish-calendar fields:

| Field | Source |
|---|---|
| platform | `content_engine_architecture_v3.md:1628-1634` |
| publish date | `content_engine_architecture_v3.md:1628-1634` |
| caption | `content_engine_architecture_v3.md:1628-1634` |
| status ready/published | `content_engine_architecture_v3.md:1628-1634` |

References:

- `content_engine_architecture_v3.md:528-529`
- `docs/handoffs/2026-04-27-client-results-interface-handoff.md:237-242`

## 12. Measurement + Feedback Loop

Workflow A must measure published video performance and send the strongest learnings back to Research Agent.

Required loop:

```text
published performance -> top hooks/topics -> Research Agent search priorities
```

References:

- `content_engine_architecture_v3.md:531-536`
- `docs/handoffs/2026-04-27-client-results-interface-handoff.md:304`

Metrics to collect:

| Metric |
|---|
| views |
| likes |
| comments |
| saves |
| shares |
| DMs / leads |
| published URL |
| hook performance |
| topic performance |

The current run correctly has a `not_published_yet` measurement placeholder, but full measurement starts after manual publishing.

## 13. Expected Final Workflow A Output

The expected output should be structured as one **Workflow A Video Asset** per routed source.

### Recommended Output Contract

```markdown
## Workflow A Video Asset
**Video Asset ID:**
**Source ID:**
**Source URL:**
**Platform:**
**Audience:**
**Theme:**
**Status:** script_ready | filmed | ready | published

### Video Intake
- Title:
- Caption:
- Spoken transcript:
- Transcript source:
- Video refs:
- Metrics:
- Visual hints:
- Public comments / reactions:

### Hook Mining
| Hook ID | Hook type | Hook text | Pattern | Tension | Promise | Visual device | Score | Verdict |
|---|---|---|---|---|---|---|---:|---|

### Selected Hook
- Hook ID:
- Hook text:
- Why selected:
- Risk:

### Script
```text
hook
body
[filming cue]
CTA
```

### Filming Card
- Card ID:
- Linked script:
- Filming priority:
- Shoot date:
- Filmed:
- Raw file link:

### Publish Queue
- Publish item ID:
- Platform:
- Caption:
- Publish date:
- Status:

### Measurement
- Published URL:
- Views:
- Likes:
- Comments:
- Saves:
- Shares:
- DMs/leads:
- Top hook signal:
- Feedback to Research Agent:
```

## 14. Current Workflow A Test Run Status

Latest output file:

```text
outputs/2026-04-27_workflow_a_only_video_run.md
```

Run summary:

| Metric | Result |
|---|---|
| Sources received | 6 |
| Sources routed to Workflow A | 6 |
| Hook candidates generated | 30 |
| Scripts generated | 6 |
| Filming cards created | 6 |
| Publish items ready | 6 |

Reference: `outputs/2026-04-27_workflow_a_only_video_run.md:3-13`.

Current output includes:

| Output block | Present? | Evidence |
|---|---|---|
| Video intake | Yes | `outputs/2026-04-27_workflow_a_only_video_run.md:29-38` |
| Hook candidates | Yes | `outputs/2026-04-27_workflow_a_only_video_run.md:40-47` |
| Selected hook | Yes | `outputs/2026-04-27_workflow_a_only_video_run.md:49-52` |
| Script | Yes | `outputs/2026-04-27_workflow_a_only_video_run.md:54-70` |
| Filming card | Yes | `outputs/2026-04-27_workflow_a_only_video_run.md:72-76` |
| Publish queue | Yes | `outputs/2026-04-27_workflow_a_only_video_run.md:78-84` |
| Measurement placeholder | Yes | `outputs/2026-04-27_workflow_a_only_video_run.md:86` |

## 15. Current Compliance Check

### What Matches The MD Requirements

| Requirement | Status |
|---|---|
| Workflow A is separate from Workflow B | Matches |
| Receives video-native source material | Matches |
| Preserves video refs, transcript, metrics | Matches |
| Generates multiple hook candidates | Matches |
| Selects best hook | Matches |
| Generates filming-ready script | Matches |
| Creates filming card | Matches |
| Creates publish-ready item | Matches |
| Publishing remains manual | Matches |
| Measurement placeholder exists | Matches |

### Gaps / Needs Tightening

| Gap | Why it matters | Recommended fix |
|---|---|---|
| Hook mining output does not yet expose `pattern`, `tension`, `promise`, `visual_device`, `repeatable_formula` as first-class fields | The skill requires these fields, but current output mostly has `hook_type`, `hook`, `angle`, `score` | Extend `VideoHook` or add `HookMiningCard` with these fields |
| No explicit hook quality gate object | Writer spec expects specificity, curiosity/tension, audience clarity, real payoff, deliverability, emotional sharpness, voice fit, verdict | Add `VideoHookQualityGate` for each hook candidate |
| No `topics` / `best_topic` output in Workflow A run | Writer Entity video module includes hooks + topics | Add optional `VideoTopicCandidate` when source has enough depth |
| Comments/reactions are collected in possible raw payload but not displayed in current Workflow A output | Comments can reveal audience pain and hook resonance | Add comments/reactions to `Video Intake` section when available |
| Measurement is placeholder only | Correct before publishing, but final loop requires real performance | Add `VideoPerformanceRecord` after manual publish |
| Language policy for Workflow A is not clearly defined in MD | Current scripts are English because source hooks/test sources are English; real production may need Russian IG/TikTok scripts | Decide per platform: Russian for IG/TikTok/YouTube by default, English only for LinkedIn Video or source-specific cases |
| Some docs still mention Notion as output layer | Current product direction is Admin Operating Hub, not Notion | Treat Notion references as legacy storage wording; Admin Hub should be output surface |

## 16. Recommended Canonical Workflow A Product Spec

For the next iteration, define Workflow A as:

```text
Workflow A — Video Production Pipeline

Input:
  canonical SourceItem from Research Agent
  evidence payload
  video refs / captions / transcript / metrics / visual hints

Phase 1 — Video Intake:
  normalize title, caption, transcript, refs, metrics, comments, visual hints

Phase 2 — Hook Mining:
  extract first 3 seconds, pattern, tension, promise, CTA, visual device, repeatable formula

Phase 3 — Hook Candidates:
  generate 5-10 candidates
  score each candidate
  run hook quality gate
  select best hook

Phase 4 — Script:
  write filming-ready short script
  structure: hook -> body -> filming cue -> CTA
  fact-check before filming

Phase 5 — Filming Card:
  create human task with priority, linked script, shoot date, raw file link

Phase 6 — Publish Queue:
  prepare caption/calendar item
  publishing remains manual

Phase 7 — Measurement:
  collect performance after manual publish
  identify top hooks/topics
  feed back to Research Agent
```

## 17. Final Conclusion

Workflow A is clearly defined across the markdown docs as a separate short-form video production pipeline. It should not be treated as a general writer flow and should not be merged with Workflow B.

The expected result is not just "a hook" or "a script." The full expected result is:

```text
Video Intake
→ Hook Mining
→ Hook Candidates
→ Selected Hook
→ Script
→ Filming Card
→ Publish Queue / Calendar
→ Measurement / Feedback Loop
```

The current run already covers the main skeleton well. The next improvement should be to make hook mining more structured by adding explicit `pattern`, `tension`, `promise`, `visual_device`, `repeatable_formula`, and `hook_quality_gate` outputs.
