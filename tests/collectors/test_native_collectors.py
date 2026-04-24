import pytest

from content_engine.collectors.native import (
    NativeSourceCollector,
    NativeSourceTarget,
    collect_native_source_items,
    resolve_target_url,
)


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


YOUTUBE_RSS = """
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:yt="http://www.youtube.com/xml/schemas/2015"
      xmlns:media="http://search.yahoo.com/mrss/">
  <title>Je Pro YouTube</title>
  <entry>
    <yt:videoId>abc123</yt:videoId>
    <title>What cheap villas hide</title>
    <published>2026-04-24T07:45:00+00:00</published>
    <link rel="alternate" href="https://www.youtube.com/watch?v=abc123" />
    <media:group>
      <media:description>Cheap villas are never actually cheap when legal, design, and management costs arrive.</media:description>
      <media:thumbnail url="https://i.ytimg.com/vi/abc123/hqdefault.jpg" />
    </media:group>
  </entry>
</feed>
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


LINKEDIN_HTML = """
<html>
  <head>
    <meta property="og:title" content="Founders ignore structure at their own cost" />
    <meta property="og:description" content="Legal structure changes the deal far more than brochure language suggests." />
    <meta property="og:url" content="https://www.linkedin.com/posts/founder-deal-logic-123/" />
    <meta property="article:published_time" content="2026-04-24T07:30:00Z" />
  </head>
</html>
"""


TIKTOK_HTML = """
<html>
  <head>
    <meta property="og:title" content="What smart buyers check first" />
    <meta property="og:description" content="Good buyers check structure before price and avoid the polished-risk trap." />
    <meta property="og:url" content="https://www.tiktok.com/@jepro/video/777" />
    <meta property="og:video" content="https://cdn.example.com/tiktok.mp4" />
    <meta property="og:image" content="https://cdn.example.com/tiktok.jpg" />
    <meta property="article:published_time" content="2026-04-24T07:40:00Z" />
  </head>
</html>
"""


def test_resolve_target_url_builds_public_platform_urls() -> None:
    assert (
        resolve_target_url(
            NativeSourceTarget(
                platform="telegram",
                handle="@clearvisionary",
                audience_segment="developer_investor",
                content_theme="boutique_hotels",
            )
        )
        == "https://t.me/s/clearvisionary"
    )
    assert (
        resolve_target_url(
            NativeSourceTarget(
                platform="instagram",
                handle="@jepro",
                audience_segment="developer_investor",
                content_theme="boutique_hotels",
            )
        )
        == "https://www.instagram.com/jepro/"
    )
    assert (
        resolve_target_url(
            NativeSourceTarget(
                platform="youtube",
                handle="UC1234567890",
                audience_segment="developer_investor",
                content_theme="boutique_hotels",
            )
        )
        == "https://www.youtube.com/feeds/videos.xml?channel_id=UC1234567890"
    )


def test_collect_native_source_items_parses_telegram_channel_page() -> None:
    target = NativeSourceTarget(
        platform="telegram",
        handle="@clearvisionary",
        audience_segment="developer_investor",
        content_theme="boutique_hotels",
    )

    items = collect_native_source_items(
        targets=[target],
        fetcher=lambda _url, _timeout: TELEGRAM_HTML,
        collected_at="2026-04-24T08:00:00Z",
    )

    assert len(items) == 1
    assert items[0].source_type == "telegram_post"
    assert items[0].source_url == "https://t.me/clearvisionary/101"
    assert items[0].external_item_id == "101"
    assert items[0].engagement_signals["views"] == 1800
    assert items[0].routing_decision == "workflow_b"


def test_collect_native_source_items_parses_youtube_feed() -> None:
    target = NativeSourceTarget(
        platform="youtube",
        handle="UC1234567890",
        audience_segment="developer_investor",
        content_theme="boutique_hotels",
    )

    items = collect_native_source_items(
        targets=[target],
        fetcher=lambda _url, _timeout: YOUTUBE_RSS,
        collected_at="2026-04-24T08:00:00Z",
    )

    assert len(items) == 1
    assert items[0].source_type == "youtube_video"
    assert items[0].media_urls == ["https://i.ytimg.com/vi/abc123/hqdefault.jpg"]
    assert items[0].routing_decision == "both"
    assert items[0].routing_reason == "video signal with textual depth"


@pytest.mark.parametrize(
    ("platform", "url", "html", "expected_source_type", "expected_route"),
    [
        ("instagram", "https://www.instagram.com/reel/C123/", INSTAGRAM_HTML, "instagram_reel", "both"),
        ("linkedin", "https://www.linkedin.com/posts/founder-deal-logic-123/", LINKEDIN_HTML, "linkedin_post", "workflow_b"),
        ("tiktok", "https://www.tiktok.com/@jepro/video/777", TIKTOK_HTML, "tiktok_video", "both"),
    ],
)
def test_collect_native_source_items_parses_html_meta_platforms(
    platform: str,
    url: str,
    html: str,
    expected_source_type: str,
    expected_route: str,
) -> None:
    target = NativeSourceTarget(
        platform=platform,
        handle="@jepro",
        source_url=url,
        audience_segment="developer_investor",
        content_theme="boutique_hotels",
    )

    items = collect_native_source_items(
        targets=[target],
        fetcher=lambda _url, _timeout: html,
        collected_at="2026-04-24T08:00:00Z",
    )

    assert len(items) == 1
    assert items[0].source_type == expected_source_type
    assert items[0].routing_decision == expected_route
    assert items[0].transcript_text


def test_native_source_collector_dispatches_multiple_platform_targets() -> None:
    targets = [
        NativeSourceTarget(
            platform="telegram",
            handle="@clearvisionary",
            audience_segment="developer_investor",
            content_theme="boutique_hotels",
        ),
        NativeSourceTarget(
            platform="youtube",
            handle="UC1234567890",
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
    ]
    responses = {
        "https://t.me/s/clearvisionary": TELEGRAM_HTML,
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC1234567890": YOUTUBE_RSS,
        "https://www.instagram.com/reel/C123/": INSTAGRAM_HTML,
    }
    collector = NativeSourceCollector(
        targets=targets,
        fetcher=lambda url, _timeout: responses[url],
        collected_at="2026-04-24T08:00:00Z",
    )

    items = collector.collect()

    assert len(items) == 3
    assert [item.source_type for item in items] == [
        "telegram_post",
        "youtube_video",
        "instagram_reel",
    ]
