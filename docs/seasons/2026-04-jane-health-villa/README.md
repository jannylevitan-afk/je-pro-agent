# Season Workspace: Jane Health Villa

**Season ID:** `2026-04-jane-health-villa`  
**Status:** active current season seed  
**Owner Entity:** Producer Agent  
**Human-facing output:** `producer-output.md`  
**Search Agent input:** `research-directives.md`

## Role

This workspace promotes the approved Jane season ProducerOutput from generated
output into durable source-of-truth context.

The human-facing document is the exact style and section structure the future
site/admin view should expose to the user after Producer creates a season.

The research directives file is intentionally shorter. It converts the Producer
season into explicit search topics, platform targets, metric gates, compliance
boundaries, and Workflow A routing rules.

## Source Files

| File | Used By | Purpose |
|---|---|---|
| `producer-output.md` | Human, Admin UI, Producer review | Full readable season program |
| `research-directives.md` | Research Agent, Workflow A hook research | Machine-readable search contract |

## Season Thesis

Jane shows how personal recovery becomes a transition into a new founder role:
from broker to creator of a phygital ocean-view villa on Bali.

## Search Topics

The 50-video Workflow A research set is topic-balanced:

| Topic Key | Required Qualified Videos |
|---|---:|
| `recovery_energy` | 10 |
| `invisible_quality` | 10 |
| `bali_real_estate` | 10 |
| `phygital_villa_experience` | 10 |
| `founder_ceo_transition` | 10 |

`audience_participation` remains a CTA/feedback mechanic, not a separate search topic.

## Search Fill Rule

Research must fill the season topic quotas sequentially:

1. `recovery_energy`
2. `invisible_quality`
3. `bali_real_estate`
4. `phygital_villa_experience`
5. `founder_ceo_transition`

For each topic, Search Agent searches both Russian and English public videos and
fills:

- YouTube Shorts: 3 qualified videos;
- TikTok: 3 qualified videos;
- Instagram Reels: 4 qualified videos.

The total target remains 50 qualified videos: `25 ru`, `25 en`,
`15 YouTube`, `15 TikTok`, `20 Instagram`. Missing metrics, weak metrics,
off-format links, and discovery-only URLs do not count.
