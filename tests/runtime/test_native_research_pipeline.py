from content_engine.collectors.native import NativeSourceCollector, NativeSourceTarget
from content_engine.runtime.dry_run import run_local_pipeline_dry_run


TELEGRAM_HTML = """
<html>
  <body>
    <div class="tgme_widget_message_wrap js-widget_message_wrap">
      <div class="tgme_widget_message" data-post="clearvisionary/101">
        <a class="tgme_widget_message_date" href="https://t.me/clearvisionary/101">
          <time datetime="2026-04-24T07:55:00+00:00"></time>
        </a>
        <div class="tgme_widget_message_text js-message_text" dir="auto">
          Boutique hotel ROI beats mass-market in Bali.<br/>Legal structure matters most.
        </div>
        <span class="tgme_widget_message_views">1.8K</span>
      </div>
    </div>
  </body>
</html>
"""


INSTAGRAM_HTML = """
<html>
  <head>
    <meta property="og:title" content="Deal logic in Bali" />
    <meta property="og:description" content="Cheap villas are never actually cheap when legal, design, and management costs arrive." />
    <meta property="og:url" content="https://www.instagram.com/reel/C123/" />
    <meta property="og:video" content="https://cdn.example.com/video.mp4" />
    <meta property="og:image" content="https://cdn.example.com/cover.jpg" />
    <meta property="article:published_time" content="2026-04-24T07:45:00Z" />
    <script type="application/ld+json">
      {"interactionStatistic":[{"userInteractionCount":5200}]}
    </script>
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


def test_native_collectors_feed_both_workflows_into_local_pipeline() -> None:
    collector = NativeSourceCollector(
        targets=[
            NativeSourceTarget(
                platform="telegram",
                handle="@clearvisionary",
                audience_segment="developer_investor",
                content_theme="boutique_hotels",
            ),
            NativeSourceTarget(
                platform="instagram",
                handle="@jepro",
                source_url="https://www.instagram.com/reel/C123/",
                audience_segment="developer_investor",
                content_theme="boutique_hotels",
            ),
        ],
        fetcher=lambda url, _timeout: {
            "https://t.me/s/clearvisionary": TELEGRAM_HTML,
            "https://www.instagram.com/reel/C123/": INSTAGRAM_HTML,
        }[url],
        collected_at="2026-04-24T08:00:00Z",
    )

    report = run_local_pipeline_dry_run(
        collector=collector,
        writer=FakeWriter(),
        verified_facts={"Boutique hotel ROI beats mass-market in Bali."},
        submitted_at="2026-04-24T10:00:00Z",
    )

    assert [item.route for item in report.item_results] == ["workflow_b", "both"]
    assert len(report.database_snapshots["sources"]) == 2
    assert len(report.database_snapshots["scripts"]) == 1
    assert len(report.database_snapshots["drafts"]) == 4
