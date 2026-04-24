from content_engine.collectors.native import NativeSourceTarget
from content_engine.orchestration.search_agent import run_search_agent
from content_engine.orchestration.targets import LivePipelineTargets
from content_engine.runtime.dry_run import InMemoryNotionClient


TELEGRAM_HTML = """
<html>
  <body>
    <div class="tgme_widget_message_wrap js-widget_message_wrap">
      <div class="tgme_widget_message" data-post="bali_expert/501">
        <a class="tgme_widget_message_date" href="https://t.me/bali_expert/501">
          <time datetime="2026-04-25T07:55:00+00:00"></time>
        </a>
        <div class="tgme_widget_message_text js-message_text" dir="auto">
          Boutique hotel ADR on Bali is rising while generic inventory becomes harder to position.
        </div>
        <span class="tgme_widget_message_views">1.6K</span>
      </div>
    </div>
  </body>
</html>
"""


WEB_HTML = """
<html>
  <head>
    <meta property="og:title" content="Bali Hotel Outlook 2026" />
    <meta property="og:description" content="Boutique hotel inventory is outperforming generic stock because occupancy, ADR, and positioning are moving together." />
    <meta property="og:url" content="https://www.realinfo.id/market-reports/bali-hotel-outlook-2026" />
    <meta property="article:published_time" content="2026-04-25T07:35:00Z" />
  </head>
</html>
"""


TARGETS = LivePipelineTargets(
    sources_database_id="db_sources",
    insights_database_id="db_insights",
    ideas_database_id="db_ideas",
    briefs_database_id="db_briefs",
    drafts_database_id="db_drafts",
    events_database_id="db_events",
    scripts_database_id="db_scripts",
    filming_cards_database_id="db_filming",
)


class FakeWriter:
    def write_video_script(self, *, item, title: str, hook: str, body_points: list[str], cta: str) -> str:
        return "Anthropic video script"

    def write_workflow_b_draft(self, *, item, insight, decision, brief):
        class Draft:
            draft_text_ru = "Anthropic Russian draft"
            draft_text_en = "Anthropic English draft" if decision.platform_lane == "linkedin_b2b" else None

        return Draft()


def test_run_search_agent_applies_compliance_gate_and_logs_evidence() -> None:
    client = InMemoryNotionClient()

    report = run_search_agent(
        client=client,
        targets=TARGETS,
        search_targets=[
            NativeSourceTarget(
                platform="instagram",
                handle="@unsafe_profile",
                source_url="http://www.instagram.com/unsafe_profile/",
                audience_segment="lifestyle_expat",
                content_theme="marketing_cases",
            ),
            NativeSourceTarget(
                platform="web",
                handle="realinfo-bali-2026",
                source_url="https://www.realinfo.id/market-reports/bali-hotel-outlook-2026",
                audience_segment="developer_investor",
                content_theme="boutique_hotels",
            ),
        ],
        fetcher=lambda url, _timeout: {
            "https://www.realinfo.id/market-reports/bali-hotel-outlook-2026": WEB_HTML,
        }[url],
        verified_facts={"Boutique hotel inventory is outperforming generic stock."},
        submitted_at="2026-04-25T10:00:00Z",
        writer=FakeWriter(),
        collected_at="2026-04-25T08:00:00Z",
    )

    assert [check.status for check in report.compliance_checks] == ["blocked", "allowed"]
    assert report.skipped_target_handles == ["@unsafe_profile"]
    assert len(report.evidence_logs) == 1
    assert report.evidence_logs[0].source_url == "https://www.realinfo.id/market-reports/bali-hotel-outlook-2026"
    assert report.pipeline_results[0].route == "workflow_b"
    assert len(client.snapshot()["sources"]) == 1
    assert len(client.snapshot()["drafts"]) == 2


def test_run_search_agent_routes_native_sources_into_both_workflows() -> None:
    client = InMemoryNotionClient()

    report = run_search_agent(
        client=client,
        targets=TARGETS,
        search_targets=[
            NativeSourceTarget(
                platform="telegram",
                handle="@bali_expert",
                audience_segment="developer_investor",
                content_theme="boutique_hotels",
            ),
            NativeSourceTarget(
                platform="web",
                handle="realinfo-bali-2026",
                source_url="https://www.realinfo.id/market-reports/bali-hotel-outlook-2026",
                audience_segment="developer_investor",
                content_theme="boutique_hotels",
            ),
        ],
        fetcher=lambda url, _timeout: {
            "https://t.me/s/bali_expert": TELEGRAM_HTML,
            "https://www.realinfo.id/market-reports/bali-hotel-outlook-2026": WEB_HTML,
        }[url],
        verified_facts={"Boutique hotel ADR on Bali is rising."},
        submitted_at="2026-04-25T10:00:00Z",
        writer=FakeWriter(),
        collected_at="2026-04-25T08:00:00Z",
    )

    assert [result.route for result in report.pipeline_results] == ["workflow_b", "workflow_b"]
    assert len(report.evidence_logs) == 2
    assert len(client.snapshot()["sources"]) == 2
    assert len(client.snapshot()["drafts"]) == 4
