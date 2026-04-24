from dataclasses import dataclass, field
from typing import Literal

from content_engine.models.approval import FactualSafety
from content_engine.models.workflow_b import DraftBundle


BANNED_PHRASES = [
    "в современном мире",
    "в наше время",
    "как известно",
    "очевидно",
    "не секрет",
    "прорыв",
    "уникальный",
    "инновационный",
    "revolutionar",
    "game-changer",
    "in today's world",
]

OPENING_RESTATE_MARKERS = [
    "сегодня я хочу рассказать",
    "этот пост про",
    "сегодня поговорим о",
    "я хочу рассказать про",
]

ENDING_SUMMARY_MARKERS = [
    "в итоге",
    "подводя итог",
    "будущее принадлежит",
    "просто верить в мечту",
]


@dataclass(frozen=True)
class EditingResult:
    seven_point_passed: bool
    factual_safety: FactualSafety
    failed_checks: list[str]
    warnings: list[str] = field(default_factory=list)


def run_editorial_gate(
    draft: DraftBundle,
    fact_claims: list[str],
    verified_facts: set[str],
) -> EditingResult:
    failed_checks: list[str] = []
    warnings: list[str] = []

    text_lower = draft.draft_text_ru.lower()
    banned_found = [p for p in BANNED_PHRASES if p in text_lower]
    if banned_found:
        failed_checks.append(f"banned_phrases: {', '.join(banned_found)}")
    if _opening_restates_theme(text_lower):
        failed_checks.append("opening_restates_theme: opening sounds like a topic announcement")
    if _ending_summarizes_or_motivates(text_lower):
        failed_checks.append("summary_or_motivation_ending: closing summarizes or moralizes")

    factual_safety = _classify_factual_safety(fact_claims, verified_facts, warnings)
    if factual_safety == "blocked":
        failed_checks.append("factual_safety_blocked: no verified claims found")

    return EditingResult(
        seven_point_passed=len(failed_checks) == 0,
        factual_safety=factual_safety,
        failed_checks=failed_checks,
        warnings=warnings,
    )


def _classify_factual_safety(
    fact_claims: list[str],
    verified_facts: set[str],
    warnings: list[str],
) -> FactualSafety:
    if not fact_claims:
        return "clean"

    unverified = [c for c in fact_claims if c not in verified_facts]
    if not unverified:
        return "clean"

    verified_count = len(fact_claims) - len(unverified)
    if verified_count == 0:
        return "blocked"

    warnings.append(
        f"unverified_claims: {len(unverified)} of {len(fact_claims)} claim(s) need confirmation"
    )
    return "needs_human_confirmation"


def _opening_restates_theme(text_lower: str) -> bool:
    first_sentence = text_lower.split(".")[0].strip()
    return any(marker in first_sentence for marker in OPENING_RESTATE_MARKERS)


def _ending_summarizes_or_motivates(text_lower: str) -> bool:
    stripped = text_lower.strip()
    if not stripped:
        return False
    last_sentence = stripped.split(".")[-1].strip()
    if not last_sentence and "." in stripped:
        last_sentence = stripped.split(".")[-2].strip()
    return any(marker in last_sentence for marker in ENDING_SUMMARY_MARKERS)
