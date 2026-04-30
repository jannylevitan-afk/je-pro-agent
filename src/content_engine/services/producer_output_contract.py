from __future__ import annotations

from html import escape

from content_engine.models.producer import ProductOffer, ProducerContext, ProducerOutput, SeriesMemory
from content_engine.models.producer_output_contract import (
    ProducerDisplayTask,
    ProducerOutputSection,
    ReadableProducerOutput,
)


PRODUCER_OUTPUT_SECTION_ORDER = [
    "producer_brief",
    "audience",
    "product_map",
    "product_to_story_mapping",
    "season_bible",
    "content_lines",
    "emotional_arc",
    "sales_arc",
    "episodes",
    "scene_cards",
    "cta_library",
    "lead_magnets",
    "proof_plan",
    "objection_handling",
    "content_rhythm",
    "visual_system",
    "sales_automation_setup",
    "metrics_plan",
    "series_memory",
    "tasks_for_workflow_agents",
    "qa_report",
    "guardrails",
    "final_assembly",
    "first_actions",
]


def build_readable_producer_output(
    output: ProducerOutput,
    *,
    context: ProducerContext | None = None,
) -> ReadableProducerOutput:
    """Build the human-facing ProducerOutput contract without changing runtime routing."""

    offer = context.offers[0] if context and context.offers else None
    memory = output.memory or (context.memory if context else None)
    rubrics = context.season_seed.rubrics_to_emphasize if context else []

    return ReadableProducerOutput(
        output_id=f"producer_output_{output.season.season_id}",
        title=output.season.title,
        subtitle=output.season.season_thesis,
        section_order=list(PRODUCER_OUTPUT_SECTION_ORDER),
        producer_brief=output.brief,
        audience_segments=_audience_sections(context),
        product_map=_product_map_sections(context),
        product_to_story_mapping=_product_story_sections(output, context),
        season_bible=output.season,
        content_lines=_content_line_sections(rubrics),
        emotional_arc=[
            ProducerOutputSection(title="Emotional Arc", items=output.season.emotional_arc)
        ],
        sales_arc=[ProducerOutputSection(title="Sales Arc", items=output.season.sales_arc)],
        episodes=output.episodes,
        scene_cards=output.scenes,
        cta_library=_cta_sections(offer),
        lead_magnets=_lead_magnet_sections(offer),
        proof_plan=_proof_sections(offer),
        objection_handling=_objection_sections(offer),
        content_rhythm=_content_rhythm_sections(context),
        visual_system=_visual_system_sections(context),
        sales_automation_setup=_sales_automation_sections(offer),
        metrics_plan=_metrics_sections(context, output),
        series_memory=_series_memory_sections(memory),
        agent_tasks=_agent_tasks(output),
        qa_report=output.qa_report,
        guardrails=_guardrails(context),
        final_assembly=_final_assembly_sections(output),
        first_actions=_first_actions(context),
    )


def format_producer_output_markdown(document: ReadableProducerOutput) -> str:
    lines: list[str] = [
        "# ProducerOutput",
        "",
        f"## Сезон: **{document.title}**",
        "",
        document.subtitle,
        "",
        "## Producer Brief",
        "",
        f"**Автор:** {document.producer_brief.creator_name}",
        f"**Аудитория:** {document.producer_brief.audience_summary}",
        f"**Продукт:** {document.producer_brief.product_summary}",
        f"**Цель сезона:** {document.producer_brief.season_goal}",
        _bullet_block("Ограничения", document.producer_brief.constraints),
        _bullet_block("Каналы", document.producer_brief.channels),
        "",
        "## Audience",
        "",
        *_format_sections(document.audience_segments),
        "## Product Map",
        "",
        *_format_sections(document.product_map),
        "## Product-to-Story Mapping",
        "",
        *_format_sections(document.product_to_story_mapping),
        "## Season Bible",
        "",
        f"**Duration:** {document.season_bible.duration_days} days",
        f"**Main question:** {document.season_bible.narrative_question}",
        f"**Main conflict:** {document.season_bible.main_conflict}",
        f"**Audience goal:** {document.season_bible.audience_goal}",
        f"**Product role:** {document.season_bible.product_role}",
        "",
        "## Content Lines",
        "",
        *_format_sections(document.content_lines),
        "## Emotional Arc",
        "",
        *_format_sections(document.emotional_arc),
        "## Sales Arc",
        "",
        *_format_sections(document.sales_arc),
        "## Episodes",
        "",
    ]

    for episode in document.episodes:
        lines.extend(
            [
                f"### {episode.title}",
                f"**Days:** {episode.day_range}",
                f"**Question:** {episode.episode_question}",
                f"**Conflict:** {episode.conflict}",
                f"**Insight:** {episode.insight}",
                f"**Sales Function:** {episode.sales_function}",
                f"**Next Hook:** {episode.hook_to_next_episode}",
                "",
            ]
        )

    lines.extend(["## Scene Cards", ""])
    for scene in document.scene_cards:
        lines.extend(
            [
                f"### {scene.scene_id} · {scene.channel} / {scene.format}",
                f"**Type / Function / Intensity:** {scene.scene_type} / {scene.plot_function} / {scene.sales_intensity}",
                f"**Hook:** {scene.hook}",
                f"**Context + tension:** {scene.context} {scene.conflict_or_question}",
                f"**Value / bridge:** {scene.value_point}",
                f"**CTA / Next Hook:** {scene.cta or scene.next_hook}",
                "",
            ]
        )

    lines.extend(
        [
            "## CTA Library",
            "",
            *_format_sections(document.cta_library),
            "## Lead Magnets",
            "",
            *_format_sections(document.lead_magnets),
            "## Proof Plan",
            "",
            *_format_sections(document.proof_plan),
            "## Objection Handling",
            "",
            *_format_sections(document.objection_handling),
            "## Content Rhythm",
            "",
            *_format_sections(document.content_rhythm),
            "## Visual System",
            "",
            *_format_sections(document.visual_system),
            "## Sales / Automation Setup",
            "",
            *_format_sections(document.sales_automation_setup),
            "## Metrics Plan",
            "",
            *_format_sections(document.metrics_plan),
            "## SeriesMemory",
            "",
            *_format_sections(document.series_memory),
            "## Tasks for Workflow Agents",
            "",
        ]
    )

    for task in document.agent_tasks:
        lines.extend(
            [
                f"### {task.display_name} · {task.priority}",
                f"**Workflow:** {task.workflow}",
                _bullet_block("Задачи", task.responsibilities),
                _bullet_block("Ограничения", task.constraints),
                "",
            ]
        )

    lines.extend(
        [
            "## QA Report",
            "",
            f"**Score:** {document.qa_report.total_score}/100",
            f"**Status:** {'passed' if not document.qa_report.issues else 'needs revision'}",
            _bullet_block("Issues", document.qa_report.issues or ["-"]),
            "",
            "## Guardrails",
            "",
            _bullet_block("Guardrails", document.guardrails),
            "",
            "## Final Producer Assembly",
            "",
            *_format_sections(document.final_assembly),
            "## What To Do First",
            "",
            _bullet_block("First actions", document.first_actions),
            "",
        ]
    )
    return "\n".join(line for line in lines if line is not None)


def format_producer_output_html(document: ReadableProducerOutput) -> str:
    markdown = format_producer_output_markdown(document)
    body = _markdownish_to_html(markdown)
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ProducerOutput · {escape(document.title)}</title>
<style>
:root {{
  --bg: #faf8f3;
  --surface: #ffffff;
  --ink: #191714;
  --muted: #625c52;
  --border: #e7dfd1;
  --accent: #9a6a2f;
  --accent-soft: #f2e8d8;
  --shadow: 0 18px 44px rgba(55, 42, 27, 0.08);
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 17px;
  line-height: 1.68;
  color: var(--ink);
  background: radial-gradient(circle at top left, #fff9ed 0, var(--bg) 34%, #f6f3ee 100%);
}}
main {{
  max-width: 1040px;
  margin: 0 auto;
  padding: 56px 28px 96px;
}}
article {{
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid var(--border);
  border-radius: 28px;
  box-shadow: var(--shadow);
  padding: 44px;
}}
h1 {{
  font-size: clamp(34px, 5vw, 56px);
  line-height: 1.05;
  margin: 0 0 18px;
  letter-spacing: -0.04em;
}}
h2 {{
  margin: 52px 0 18px;
  padding-top: 22px;
  border-top: 1px solid var(--border);
  font-size: clamp(25px, 3vw, 36px);
  line-height: 1.15;
  letter-spacing: -0.03em;
}}
h3 {{
  margin: 28px 0 10px;
  font-size: 21px;
  color: var(--accent);
}}
p, li {{ color: var(--muted); }}
strong {{ color: var(--ink); }}
ul {{ padding-left: 24px; }}
.label {{
  display: inline-block;
  margin-bottom: 18px;
  padding: 6px 11px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 13px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}}
@media (max-width: 720px) {{
  main {{ padding: 24px 14px 60px; }}
  article {{ padding: 26px 20px; border-radius: 20px; }}
}}
</style>
</head>
<body>
<main>
<article>
<span class="label">ProducerOutput</span>
{body}
</article>
</main>
</body>
</html>
"""


def _agent_tasks(output: ProducerOutput) -> list[ProducerDisplayTask]:
    scene_ids = ", ".join(scene.scene_id for scene in output.scenes)
    return [
        ProducerDisplayTask(
            task_id=f"copywriter_{output.season.season_id}",
            display_name="CopywriterAgent",
            target_agent="copywriter_agent",
            priority="high",
            workflow="workflow_b",
            responsibilities=[
                f"Write Workflow B final text assets from approved ContentBriefs for scenes: {scene_ids}.",
                "Use the Producer scene question, conflict, sales function, and CTA direction as the writing brief.",
                "Do not write Workflow A video hooks, scripts, or filming cards.",
            ],
            constraints=["source-backed only", "one final asset per approved opportunity", "manual review before publishing"],
        ),
        ProducerDisplayTask(
            task_id=f"designer_{output.season.season_id}",
            display_name="DesignerAgent",
            target_agent="designer_agent",
            priority="medium",
            workflow="cross_workflow",
            responsibilities=[
                "Prepare visual direction, carousel structure, and NDA-safe reference notes for approved scenes.",
                "Support Workflow A and Workflow B assets without becoming a separate publishing pipeline.",
            ],
            constraints=["no generated proof", "NDA-safe visuals only", "human approval for project materials"],
        ),
        ProducerDisplayTask(
            task_id=f"video_asset_{output.season.season_id}",
            display_name="Video / AssetAgent",
            target_agent="video_asset_agent",
            priority="high",
            workflow="workflow_a",
            responsibilities=[
                f"Turn Workflow A briefs into video assets for scenes: {scene_ids}.",
                "Prepare selected hook, short-form script, source-backed video angle, and filming card.",
                "Keep Workflow A separate from Workflow B text writing.",
            ],
            constraints=["no publish queue", "no auto-publishing", "human filming step required"],
        ),
        ProducerDisplayTask(
            task_id=f"sales_automation_{output.season.season_id}",
            display_name="Sales / AutomationAgent",
            target_agent="sales_automation_agent",
            priority="high",
            workflow="manual_ops",
            responsibilities=[
                "Prepare DM keywords, segmentation questions, lead magnet delivery copy, and manual follow-up prompts.",
                "Check legal/NDA wording before any project, price, timeline, or private presentation claim.",
            ],
            constraints=["no fake urgency", "no guaranteed ROI", "manual sales follow-up"],
        ),
        ProducerDisplayTask(
            task_id=f"manual_calendar_{output.season.season_id}",
            display_name="Manual Publishing / Calendar",
            target_agent="manual_publishing_calendar",
            priority="medium",
            workflow="manual_ops",
            responsibilities=[
                "Arrange approved scenes into a manual review calendar.",
                "Keep direct CTA scenes after proof and objection-handling scenes.",
            ],
            constraints=["no auto-publishing", "no scheduler in active pipeline", "human review controls release"],
        ),
        ProducerDisplayTask(
            task_id=f"analytics_{output.season.season_id}",
            display_name="AnalyticsAgent",
            target_agent="analytics_agent",
            priority="medium",
            workflow="cross_workflow",
            responsibilities=[
                "Track weekly audience signals, saves, replies, qualified DMs, and objections by scene.",
                "Return metrics to Producer so the next episode can be corrected without breaking the season arc.",
            ],
            constraints=["use public/business metrics only", "do not infer private user data"],
        ),
    ]


def _audience_sections(context: ProducerContext | None) -> list[ProducerOutputSection]:
    if context is None:
        return [ProducerOutputSection(title="Audience", items=["Use ProducerBrief audience summary."])]
    focus = context.season_seed.audience_focus or ["selected season audience"]
    return [
        ProducerOutputSection(title=audience, items=[f"Primary season audience segment: {audience}"])
        for audience in context.audience
    ] or [ProducerOutputSection(title="Audience", items=[focus[0]])]


def _product_map_sections(context: ProducerContext | None) -> list[ProducerOutputSection]:
    if context is None or not context.offers:
        return [ProducerOutputSection(title="Core Product", items=["Use ProducerBrief product summary."])]
    return [
        ProducerOutputSection(
            title=offer.name,
            items=[
                f"Type: {offer.offer_type}",
                f"Problem: {offer.core_problem}",
                f"Transformation: {offer.promised_transformation}",
                f"Audience: {offer.target_audience}",
            ],
        )
        for offer in context.offers
    ]


def _product_story_sections(
    output: ProducerOutput,
    context: ProducerContext | None,
) -> list[ProducerOutputSection]:
    offer_name = context.offers[0].name if context and context.offers else output.brief.product_summary
    return [
        ProducerOutputSection(
            title="Product-to-Story Mapping",
            items=[
                f"Product: {offer_name}",
                f"Problem: {output.season.main_conflict}",
                f"New belief: {output.season.product_role}",
                f"Proof before pitch: {output.season.audience_goal}",
            ],
        )
    ]


def _content_line_sections(rubrics: list[str]) -> list[ProducerOutputSection]:
    return [
        ProducerOutputSection(title=rubric, items=[f"Use this rubric as a recurring season line: {rubric}"])
        for rubric in rubrics
    ] or [ProducerOutputSection(title="Season line", items=["Use the selected season rubric."])]


def _cta_sections(offer: ProductOffer | None) -> list[ProducerOutputSection]:
    ctas = offer.cta_options if offer else ["Save", "Reply", "DM keyword"]
    return [ProducerOutputSection(title="CTA Library", items=list(ctas))]


def _lead_magnet_sections(offer: ProductOffer | None) -> list[ProducerOutputSection]:
    ctas = offer.cta_options if offer else []
    return [
        ProducerOutputSection(title=f"Lead magnet: {cta}", items=[f"Use keyword {cta} only when it matches the scene function."])
        for cta in ctas
    ] or [ProducerOutputSection(title="Lead magnet", items=["Define only after proof asset is available."])]


def _proof_sections(offer: ProductOffer | None) -> list[ProducerOutputSection]:
    proof_assets = offer.proof_assets if offer else []
    return [
        ProducerOutputSection(title="Proof Plan", items=list(proof_assets) or ["Collect proof assets before direct offer scenes."])
    ]


def _objection_sections(offer: ProductOffer | None) -> list[ProducerOutputSection]:
    objections = offer.main_objections if offer else []
    return [
        ProducerOutputSection(title=objection, items=[f"Close this objection before direct CTA: {objection}"])
        for objection in objections
    ] or [ProducerOutputSection(title="Objection Handling", items=["Use audience questions and research evidence."])]


def _content_rhythm_sections(context: ProducerContext | None) -> list[ProducerOutputSection]:
    channels = context.season_seed.channels if context else []
    return [
        ProducerOutputSection(title="Content Rhythm", items=[f"Use channels: {', '.join(channels) or 'selected season channels'}"])
    ]


def _visual_system_sections(context: ProducerContext | None) -> list[ProducerOutputSection]:
    niche = context.creator.niche if context else "Jane Superstar"
    return [
        ProducerOutputSection(
            title="Visual System",
            items=[f"Visual direction must support the season niche and proof boundaries: {niche}"],
        )
    ]


def _sales_automation_sections(offer: ProductOffer | None) -> list[ProducerOutputSection]:
    ctas = offer.cta_options if offer else []
    return [
        ProducerOutputSection(
            title="DM Keywords",
            items=[f"Keyword: {cta}" for cta in ctas] or ["No keyword until offer is confirmed."],
        )
    ]


def _metrics_sections(
    context: ProducerContext | None,
    output: ProducerOutput,
) -> list[ProducerOutputSection]:
    metrics = context.season_seed.success_metrics if context else output.season.success_metrics
    return [ProducerOutputSection(title="Metrics Plan", items=metrics or ["Track scene-level audience signals."])]


def _series_memory_sections(memory: SeriesMemory | None) -> list[ProducerOutputSection]:
    if memory is None:
        return [ProducerOutputSection(title="SeriesMemory", items=["Start memory from open loops, promises, and topics to avoid."])]
    return [
        ProducerOutputSection(title="Open Loops", items=list(memory.open_loops)),
        ProducerOutputSection(title="Promises Made", items=list(memory.promises_made)),
        ProducerOutputSection(title="Topics To Avoid Repeating", items=list(memory.topics_to_avoid_repeating)),
    ]


def _guardrails(context: ProducerContext | None) -> list[str]:
    base = [
        "Producer does not search, write final posts, publish, or invent proof.",
        "Workflow A and Workflow B stay separate.",
        "Sales must grow from context, proof, and objections; no glued-on pitch.",
    ]
    if context:
        base.extend(context.constraints)
        base.extend(context.season_seed.constraints)
    return _unique(base)


def _final_assembly_sections(output: ProducerOutput) -> list[ProducerOutputSection]:
    return [
        ProducerOutputSection(
            title="Final Producer Assembly",
            items=[
                f"Main message: {output.season.season_thesis}",
                f"Main conflict: {output.season.main_conflict}",
                f"Product bridge: {output.season.product_role}",
                f"Primary invitation: {output.scenes[-1].cta if output.scenes else 'manual review'}",
            ],
        )
    ]


def _first_actions(context: ProducerContext | None) -> list[str]:
    if context is None:
        return ["Approve the season title.", "Collect proof assets.", "Run Research Agent directives."]
    return [
        "Approve the season title and offer boundaries.",
        "Collect proof assets and NDA-safe visuals before direct offer scenes.",
        "Run Research Agent from Producer ResearchDirective objects.",
        "Build Workflow A and Workflow B briefs only from approved opportunities.",
    ]


def _format_sections(sections: list[ProducerOutputSection]) -> list[str]:
    lines: list[str] = []
    for section in sections:
        lines.append(f"### {section.title}")
        lines.append(_bullet_block("Items", section.items))
        lines.append("")
    return lines


def _bullet_block(title: str, items: list[str]) -> str:
    if not items:
        return f"**{title}:** -"
    bullets = "\n".join(f"- {item}" for item in items)
    return f"**{title}:**\n{bullets}"


def _markdownish_to_html(markdown: str) -> str:
    html_lines: list[str] = []
    in_list = False
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue
        if line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{_inline_html(line[2:])}</li>")
            continue
        if in_list:
            html_lines.append("</ul>")
            in_list = False
        if line.startswith("### "):
            html_lines.append(f"<h3>{_inline_html(line[4:])}</h3>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{_inline_html(line[3:])}</h2>")
        elif line.startswith("# "):
            html_lines.append(f"<h1>{_inline_html(line[2:])}</h1>")
        else:
            html_lines.append(f"<p>{_inline_html(line)}</p>")
    if in_list:
        html_lines.append("</ul>")
    return "\n".join(html_lines)


def _inline_html(value: str) -> str:
    escaped = escape(value)
    while "**" in escaped:
        escaped = escaped.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
    return escaped


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


__all__ = [
    "PRODUCER_OUTPUT_SECTION_ORDER",
    "build_readable_producer_output",
    "format_producer_output_html",
    "format_producer_output_markdown",
]
