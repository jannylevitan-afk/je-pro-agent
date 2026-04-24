from content_engine.collectors.native import NativeSourceTarget
from content_engine.runtime.search_dry_run import run_local_search_agent_dry_run


TELEGRAM_HTML = """
<html>
  <body>
    <div class="tgme_widget_message_wrap js-widget_message_wrap">
      <div class="tgme_widget_message" data-post="wellstate/729">
        <a class="tgme_widget_message_date" href="https://t.me/wellstate/729">
          <time datetime="2026-04-25T07:55:00+00:00"></time>
        </a>
        <div class="tgme_widget_message_text js-message_text" dir="auto">
          Webinar: Bali real estate yield and structuring for investors who want cleaner decision logic.
        </div>
        <span class="tgme_widget_message_views">74</span>
      </div>
    </div>
  </body>
</html>
"""


INSTAGRAM_HTML = """
<html>
  <head>
    <meta property="og:title" content="What smart buyers check first" />
    <meta property="og:description" content="Good buyers check structure before price and avoid the polished-risk trap." />
    <meta property="og:url" content="https://www.instagram.com/reel/C777/" />
    <meta property="og:video" content="https://cdn.example.com/reel.mp4" />
    <meta property="og:image" content="https://cdn.example.com/reel.jpg" />
    <meta property="article:published_time" content="2026-04-25T07:40:00Z" />
  </head>
</html>
"""


class FakeWriter:
    def write_video_script(self, *, item, title: str, hook: str, body_points: list[str], cta: str) -> str:
        return "Anthropic video script"

    def write_workflow_b_draft(self, *, item, insight, decision, brief):
        class Draft:
            draft_text_ru = "Anthropic Russian draft"
            draft_text_en = "Anthropic English draft" if decision.platform_lane == "linkedin_b2b" else None

        return Draft()


def test_run_local_search_agent_dry_run_returns_search_report_and_snapshots() -> None:
    report = run_local_search_agent_dry_run(
        search_targets=[
            NativeSourceTarget(
                platform="telegram",
                handle="@wellstate",
                audience_segment="developer_investor",
                content_theme="boutique_hotels",
            ),
            NativeSourceTarget(
                platform="instagram",
                handle="@jepro",
                source_url="https://www.instagram.com/reel/C777/",
                audience_segment="developer_investor",
                content_theme="boutique_hotels",
            ),
        ],
        fetcher=lambda url, _timeout: {
            "https://t.me/s/wellstate": TELEGRAM_HTML,
            "https://www.instagram.com/reel/C777/": INSTAGRAM_HTML,
        }[url],
        writer=FakeWriter(),
        verified_facts={"Good buyers check structure before price."},
        submitted_at="2026-04-25T10:00:00Z",
        collected_at="2026-04-25T08:00:00Z",
    )

    assert [result.route for result in report.search_report.pipeline_results] == ["workflow_b", "both"]
    assert len(report.search_report.evidence_logs) == 2
    assert len(report.database_snapshots["sources"]) == 2
    assert len(report.database_snapshots["scripts"]) == 1
    assert len(report.database_snapshots["drafts"]) == 4
