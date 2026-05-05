from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read_skill(name: str) -> str:
    return (ROOT / ".agents" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def test_video_intake_skill_requires_workflow_a_audit_fields() -> None:
    skill = _read_skill("video-intake-skill")

    required_fields = [
        "`raw_payload.first_3_seconds`",
        "`raw_payload.source_hook`",
        "`raw_payload.visual_device`",
        "`raw_payload.hook_pattern`",
        "`raw_payload.hook_tension`",
        "`raw_payload.hook_promise`",
        "`raw_payload.hook_cta`",
        "`raw_payload.repeatable_formula`",
        "`raw_payload.comments_sample`",
        "immutable raw payload",
    ]

    for field in required_fields:
        assert field in skill


def test_hook_mining_skill_requires_quality_gate_contract() -> None:
    skill = _read_skill("hook-mining-skill")

    required_phrases = [
        "hook_quality_gate",
        "clarity",
        "specificity",
        "tension",
        "relevance",
        "continuation_pull",
        "verdict",
        "minimum pass score",
    ]

    for phrase in required_phrases:
        assert phrase in skill


def test_research_agent_runner_documents_admin_hub_handoff_not_notion() -> None:
    skill = _read_skill("research-agent-runner")

    assert "Admin Operating Hub-ready artifacts" in skill
    assert "Notion" not in skill


def test_research_agent_runner_requires_best_performing_post_scan_contract() -> None:
    skill = _read_skill("research-agent-runner")

    required_phrases = [
        "scan recent public posts",
        "best-performing post",
        "views, likes, comments, saves, shares",
        "engagement score",
        "post URL",
        "caption or description text",
        "carousel/image OCR text when available",
        "source post payload snapshot",
    ]

    for phrase in required_phrases:
        assert phrase in skill


def test_research_agent_runner_requires_topic_balanced_hook_research() -> None:
    skill = _read_skill("research-agent-runner")

    required_phrases = [
        "topic_source_targets",
        "topic-balanced",
        "10 videos per topic",
        "qualified_topic_counts",
        "audience participation is a CTA/feedback mechanic",
    ]

    for phrase in required_phrases:
        assert phrase in skill
