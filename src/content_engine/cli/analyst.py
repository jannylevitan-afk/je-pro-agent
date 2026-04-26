from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

from content_engine.llm.analyst import AnthropicPipelineAnalyst
from content_engine.llm.anthropic import AnthropicClient, AnthropicClientConfig
from content_engine.models.source_item import SourceItem
from content_engine.services.analyst import (
    AnalystReport,
    WorkflowAnalyst,
    run_analyst_batch,
)


JsonObject = dict[str, Any]
AnalystFactory = Callable[["AnalystCliConfig"], WorkflowAnalyst]


@dataclass(frozen=True, slots=True)
class AnalystCliConfig:
    model: str = "claude-sonnet-4-20250514"
    api_key: str = ""
    base_url: str = "https://api.anthropic.com/v1"
    anthropic_version: str = "2023-06-01"
    timeout_seconds: float = 30.0


@dataclass(frozen=True, slots=True)
class AnalystCliInput:
    source_items: list[SourceItem]
    verified_facts: set[str]


@dataclass(frozen=True, slots=True)
class AnalystCliOutput:
    model: str
    input_count: int
    reports: list[AnalystReport]


def load_analyst_cli_input(path: Path) -> AnalystCliInput:
    """Load SourceItem records from a JSON file."""
    raw = json.loads(path.read_text(encoding="utf-8"))

    verified_facts: set[str] = set()
    raw_items: object
    if isinstance(raw, list):
        raw_items = raw
    elif isinstance(raw, dict):
        raw_items = raw.get("source_items", raw.get("items"))
        verified_facts = _string_set(raw.get("verified_facts", []))
    else:
        raise ValueError("Analyst CLI input must be a JSON list or object")

    if not isinstance(raw_items, list):
        raise ValueError("Analyst CLI input must contain a list of source items")

    return AnalystCliInput(
        source_items=[SourceItem.model_validate(item) for item in raw_items],
        verified_facts=verified_facts,
    )


def run_analyst_entity(
    *,
    source_items: list[SourceItem],
    analyst: WorkflowAnalyst,
    verified_facts: set[str],
    config: AnalystCliConfig,
) -> AnalystCliOutput:
    reports = run_analyst_batch(
        source_items,
        analyst,
        verified_facts=verified_facts,
    )
    return AnalystCliOutput(
        model=config.model,
        input_count=len(source_items),
        reports=reports,
    )


def build_json_report(output: AnalystCliOutput) -> JsonObject:
    return {
        "entity": "analyst",
        "destination": "admin_operating_hub",
        "notion_enabled": False,
        "model": output.model,
        "input_count": output.input_count,
        "report_count": len(output.reports),
        "reports": [_report_to_dict(report) for report in output.reports],
    }


def render_markdown_report(output: AnalystCliOutput) -> str:
    lines = [
        "# Analyst Entity Report",
        "",
        f"- Entity: Analyst",
        f"- Destination: Admin Operating Hub",
        f"- Model: {output.model}",
        f"- Input source items: {output.input_count}",
        f"- Analyst reports: {len(output.reports)}",
    ]

    for report in output.reports:
        note = report.source_note
        insight = report.insight
        lines.extend(
            [
                "",
                "---",
                "",
                f"## Source: {report.source_item_id}",
                "",
                "### Source Note",
                f"- Source Name: {note.source_name}",
                f"- Source URL: {note.source_url}",
                f"- Source Type: {note.source_type}",
                f"- Platform: {note.platform}",
                f"- Date Collected: {note.date_collected}",
                f"- Audience Guess: {note.audience_guess}",
                f"- Topic Guess: {note.topic_guess}",
                f"- Content Type Guess: {note.content_type_guess}",
                f"- Preflight Passed: {report.preflight_passed}",
                f"- Risk Flags: {'; '.join(report.risk_flags) if report.risk_flags else '-'}",
                f"- Raw Excerpt: {_excerpt(note.raw_text)}",
                "",
                "### Insight Card",
                f"- Topic: {insight.topic}",
                f"- Angle: {insight.angle}",
                f"- Audience: {insight.audience}",
                f"- Audience Fit: {insight.audience_fit}",
                f"- Content Theme: {insight.content_theme}",
                f"- Content Pillar: {insight.content_pillar}",
                f"- Emotional Trigger: {insight.emotional_trigger}",
                f"- Narrative Type: {insight.narrative_type}",
                f"- Reuse Score: {insight.reuse_score}/5",
                f"- Useful Lesson: {insight.useful_lesson}",
            ]
        )
        for index, spec in enumerate(report.writer_specs, start=1):
            lines.extend(
                [
                    "",
                    f"### Writer Spec {index}: {spec.decision.platform_lane}",
                    f"- Platform: {spec.decision.platform}",
                    f"- Funnel Role: {spec.decision.funnel_role}",
                    f"- Source Rigor: {spec.decision.source_rigor}",
                    "",
                    "### Writer Entity TZ",
                    "",
                    _strip_first_heading(spec.writer_tz, "## Writer Entity TZ"),
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def load_analyst_cli_config(
    *,
    env_file: Path,
    model_override: str | None,
    require_api_key: bool,
) -> AnalystCliConfig:
    file_values = _read_env_file(env_file)

    def get_env(name: str, default: str = "") -> str:
        return os.environ.get(name, file_values.get(name, default)).strip()

    api_key = get_env("ANTHROPIC_API_KEY")
    if require_api_key and not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is required to run the Analyst Entity with Anthropic"
        )

    raw_timeout = get_env("CONTENT_ENGINE_REQUEST_TIMEOUT_SECONDS", "30")
    try:
        timeout_seconds = float(raw_timeout)
    except ValueError as error:
        raise ValueError("CONTENT_ENGINE_REQUEST_TIMEOUT_SECONDS must be a number") from error

    return AnalystCliConfig(
        model=(model_override or get_env("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")),
        api_key=api_key,
        base_url=get_env("ANTHROPIC_API_BASE", "https://api.anthropic.com/v1"),
        anthropic_version=get_env("ANTHROPIC_VERSION", "2023-06-01"),
        timeout_seconds=timeout_seconds,
    )


def build_anthropic_analyst(config: AnalystCliConfig) -> WorkflowAnalyst:
    client = AnthropicClient(
        AnthropicClientConfig(
            api_key=config.api_key,
            base_url=config.base_url,
            anthropic_version=config.anthropic_version,
            model=config.model,
            timeout_seconds=config.timeout_seconds,
        )
    )
    return AnthropicPipelineAnalyst(client, model=config.model)


def main(
    argv: Sequence[str] | None = None,
    *,
    analyst_factory: AnalystFactory | None = None,
) -> int:
    args = _build_parser().parse_args(argv)
    cli_input = load_analyst_cli_input(args.input)
    verified_facts = cli_input.verified_facts | set(args.verified_fact)
    config = load_analyst_cli_config(
        env_file=args.env_file,
        model_override=args.model,
        require_api_key=analyst_factory is None,
    )
    analyst = (analyst_factory or build_anthropic_analyst)(config)
    output = run_analyst_entity(
        source_items=cli_input.source_items,
        analyst=analyst,
        verified_facts=verified_facts,
        config=config,
    )

    markdown = render_markdown_report(output)
    if args.output:
        _write_text(args.output, markdown)
    else:
        print(markdown, end="")

    if args.json_output:
        _write_text(
            args.json_output,
            json.dumps(build_json_report(output), ensure_ascii=False, indent=2) + "\n",
        )

    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="content-engine-analyst",
        description=(
            "Run the Content Engine Analyst Entity: SourceItems -> Source Notes, "
            "Insight Cards, and Writer Entity TZ handoffs."
        ),
    )
    parser.add_argument("--input", required=True, type=Path, help="JSON SourceItem list or {source_items: [...]} object")
    parser.add_argument("--output", type=Path, help="Write Markdown Analyst Entity report")
    parser.add_argument("--json-output", type=Path, help="Write admin-ready JSON Analyst Entity report")
    parser.add_argument("--env-file", type=Path, default=Path(".env.local"), help="Optional env file with ANTHROPIC_API_KEY")
    parser.add_argument("--model", help="Anthropic model override")
    parser.add_argument(
        "--verified-fact",
        action="append",
        default=[],
        help="Source-backed fact allowed in Writer TZ. Can be provided more than once.",
    )
    return parser


def _report_to_dict(report: AnalystReport) -> JsonObject:
    return {
        "source_item_id": report.source_item_id,
        "source_note": report.source_note.model_dump(mode="json"),
        "insight": report.insight.model_dump(mode="json"),
        "preflight_passed": report.preflight_passed,
        "risk_flags": report.risk_flags,
        "writer_specs": [
            {
                "decision": asdict(spec.decision),
                "idea": spec.idea.model_dump(mode="json"),
                "brief": spec.brief.model_dump(mode="json"),
                "writer_tz": spec.writer_tz,
            }
            for spec in report.writer_specs
        ],
    }


def _string_set(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {str(item).strip() for item in value if str(item).strip()}


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, raw_value = stripped.split("=", 1)
        key = key.removeprefix("export ").strip()
        if not key:
            continue
        values[key] = raw_value.strip().strip('"').strip("'")
    return values


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _strip_first_heading(text: str, heading: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == heading:
        return "\n".join(lines[1:]).lstrip()
    return text


def _excerpt(text: str, limit: int = 260) -> str:
    normalized = " ".join(text.split()).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "..."


if __name__ == "__main__":
    raise SystemExit(main())
