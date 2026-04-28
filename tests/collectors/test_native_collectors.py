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

TELEGRAM_MULTI_POST_HTML = """
<html>
  <body>
    <div class="tgme_widget_message_wrap js-widget_message_wrap">
      <div class="tgme_widget_message" data-post="clearvisionary/101">
        <a class="tgme_widget_message_date" href="https://t.me/clearvisionary/101">
          <time datetime="2026-04-24T07:55:00+00:00"></time>
        </a>
        <div class="tgme_widget_message_text js-message_text" dir="auto">
          Quiet post about Bali project notes.
        </div>
        <span class="tgme_widget_message_views">900</span>
      </div>
    </div>
    <div class="tgme_widget_message_wrap js-widget_message_wrap">
      <div class="tgme_widget_message" data-post="clearvisionary/102">
        <a class="tgme_widget_message_owner_name" href="https://t.me/clearvisionary">Clear Visionary</a>
        <a class="tgme_widget_message_date" href="https://t.me/clearvisionary/102">
          <time datetime="2026-04-25T07:55:00+00:00"></time>
        </a>
        <div class="tgme_widget_message_text js-message_text" dir="auto">
          Viral post about why a Bali villa launch worked: strong hook, proof, comments, and saves.
        </div>
        <span class="tgme_widget_message_views">4.8K</span>
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
      <media:community>
        <media:statistics views="4875" />
      </media:community>
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
      {
        "name": "Deal logic in Bali",
        "caption": "Cheap villas are never actually cheap.",
        "transcript": "Speaker says: cheap villas are never actually cheap after legal, design, and management costs.",
        "interactionStatistic": [
          {"interactionType":"https://schema.org/WatchAction","userInteractionCount":5200},
          {"interactionType":"https://schema.org/LikeAction","userInteractionCount":410},
          {"interactionType":"https://schema.org/CommentAction","userInteractionCount":38}
        ]
      }
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


TIKTOK_PROFILE_HTML = """
<html>
  <body>
    <script id="SIGI_STATE" type="application/json">
      {
        "ItemModule": {
          "quiet111": {
            "id": "quiet111",
            "desc": "quiet Bali note without strong proof",
            "createTime": "1777027200",
            "stats": {
              "playCount": 1200,
              "diggCount": 120,
              "commentCount": 6,
              "shareCount": 2,
              "collectCount": 7
            },
            "video": {
              "cover": "https://cdn.example.com/quiet.jpg",
              "playAddr": "https://cdn.example.com/quiet.mp4"
            },
            "author": {"uniqueId": "jepro"}
          },
          "viral777": {
            "id": "viral777",
            "desc": "Why the new Bali cafe launch worked: people saved the route, argued in comments, and shared it with friends.",
            "createTime": "1777113600",
            "stats": {
              "playCount": 48000,
              "diggCount": 5400,
              "commentCount": 380,
              "shareCount": 260,
              "collectCount": 920
            },
            "video": {
              "cover": "https://cdn.example.com/viral.jpg",
              "playAddr": "https://cdn.example.com/viral.mp4"
            },
            "author": {"uniqueId": "jepro"},
            "imageText": ["On-screen text: this is why people saved the place"]
          }
        }
      }
    </script>
  </body>
</html>
"""


WEB_HTML = """
<html>
  <head>
    <meta property="og:title" content="Bali Hotel Outlook 2026" />
    <meta property="og:description" content="Boutique hotel inventory is outperforming generic stock because occupancy, ADR, and positioning are moving together." />
    <meta property="og:url" content="https://www.realinfo.id/market-reports/bali-hotel-outlook-2026" />
    <meta property="article:published_time" content="2026-04-24T07:35:00Z" />
  </head>
</html>
"""


INSTAGRAM_PROFILE_HTML = """
<html>
  <head>
    <meta property="og:url" content="https://www.instagram.com/annalutaeva/" />
  </head>
</html>
"""


APIFY_INSTAGRAM_PROFILE = {
    "inputUrl": "https://www.instagram.com/annalutaeva",
    "id": "204762173",
    "username": "annalutaeva",
    "url": "https://www.instagram.com/annalutaeva",
    "fullName": "ANNA LUTAEVA ARCHITECT",
    "biography": "anna lutaeva architect design spaces you want to touch bali",
    "followersCount": 27476,
    "followsCount": 4959,
    "postsCount": 1573,
    "profilePicUrl": "https://cdn.example.com/profile.jpg",
    "latestPosts": [
        {
            "id": "3655476118233595350",
            "type": "Video",
            "caption": "решила больше рассказывать о своей жизни и о школе на Бали, которая стала моей сбывшейся мечтой",
            "url": "https://www.instagram.com/p/DK63Cl4PL3W/",
            "displayUrl": "https://cdn.example.com/post.jpg",
            "videoUrl": "https://cdn.example.com/post.mp4",
            "likesCount": 25454,
            "commentsCount": 461,
            "videoViewCount": 50191,
            "timestamp": "2025-06-15T11:28:54.000Z",
            "ownerUsername": "annalutaeva",
        }
    ],
}


APIFY_INSTAGRAM_PROFILE_WITH_MIXED_POSTS = {
    "inputUrl": "https://www.instagram.com/annalutaeva",
    "id": "204762173",
    "username": "annalutaeva",
    "url": "https://www.instagram.com/annalutaeva",
    "fullName": "ANNA LUTAEVA ARCHITECT",
    "biography": "anna lutaeva architect design spaces you want to touch bali",
    "followersCount": 27476,
    "followsCount": 4959,
    "postsCount": 1573,
    "latestPosts": [
        {
            "id": "low_latest",
            "type": "Image",
            "caption": "latest quiet note",
            "url": "https://www.instagram.com/p/LOW/",
            "displayUrl": "https://cdn.example.com/low.jpg",
            "likesCount": 120,
            "commentsCount": 4,
            "timestamp": "2026-04-25T10:00:00.000Z",
        },
        {
            "id": "viral_carousel",
            "type": "Sidecar",
            "caption": "caption: why Bali life content worked this week",
            "url": "https://www.instagram.com/p/VIRAL/",
            "displayUrl": "https://cdn.example.com/viral-cover.jpg",
            "likesCount": 5400,
            "commentsCount": 320,
            "sharesCount": 190,
            "savesCount": 870,
            "timestamp": "2026-04-24T10:00:00.000Z",
            "title": "Carousel title: Bali life hook",
            "carouselText": [
                "Slide 1: The Bali life post that made people save",
                "Slide 2: Proof beats postcard content",
            ],
            "images": [
                {"url": "https://cdn.example.com/slide1.jpg", "alt": "OCR: first slide text"},
                {"url": "https://cdn.example.com/slide2.jpg", "alt": "OCR: second slide text"},
            ],
        },
        {
            "id": "views_only",
            "type": "Video",
            "caption": "views but weak comments",
            "url": "https://www.instagram.com/reel/VIEWS/",
            "videoUrl": "https://cdn.example.com/views.mp4",
            "videoViewCount": 45000,
            "likesCount": 300,
            "commentsCount": 8,
            "timestamp": "2026-04-23T10:00:00.000Z",
        },
    ],
}


APIFY_TIKTOK_PROFILE = {
    "profile": {
        "name": "baligasm",
        "profileUrl": "https://www.tiktok.com/@baligasm",
    },
    "latestPosts": [
        {
            "id": "quiet_tiktok",
            "text": "Quiet Bali cafe note",
            "createTime": 1777027200,
            "authorMeta": {"name": "baligasm"},
            "webVideoUrl": "https://www.tiktok.com/@baligasm/video/quiet_tiktok",
            "playCount": 1200,
            "diggCount": 80,
            "commentCount": 3,
            "shareCount": 4,
            "collectCount": 6,
        },
        {
            "id": "viral_tiktok",
            "text": "Why this Bali music event made people save the date and send it to friends.",
            "createTimeISO": "2026-04-26T10:00:00.000Z",
            "authorMeta": {"name": "baligasm"},
            "webVideoUrl": "https://www.tiktok.com/@baligasm/video/viral_tiktok",
            "videoMeta": {"coverUrl": "https://cdn.example.com/tiktok-cover.jpg"},
            "playCount": 48000,
            "diggCount": 5400,
            "commentCount": 380,
            "shareCount": 260,
            "collectCount": 920,
        },
    ],
}


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
    assert (
        resolve_target_url(
            NativeSourceTarget(
                platform="web",
                handle="realinfo-bali-2026",
                source_url="https://www.realinfo.id/market-reports/bali-hotel-outlook-2026",
                audience_segment="developer_investor",
                content_theme="boutique_hotels",
            )
        )
        == "https://www.realinfo.id/market-reports/bali-hotel-outlook-2026"
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


def test_collect_native_source_items_selects_top_telegram_post_by_public_engagement() -> None:
    target = NativeSourceTarget(
        platform="telegram",
        handle="@clearvisionary",
        audience_segment="developer_investor",
        content_theme="boutique_hotels",
    )

    items = collect_native_source_items(
        targets=[target],
        fetcher=lambda _url, _timeout: TELEGRAM_MULTI_POST_HTML,
        collected_at="2026-04-25T08:00:00Z",
    )

    assert len(items) == 1
    assert items[0].source_url == "https://t.me/clearvisionary/102"
    assert items[0].external_item_id == "102"
    assert items[0].engagement_signals["views"] == 4800
    assert items[0].raw_payload["monitoring_selection"] == "best_performing_post"
    assert items[0].raw_payload["engagement_rank"] == 1
    assert items[0].raw_payload["scanned_posts_count"] == 2
    assert "public engagement score" in items[0].raw_payload["engagement_selection_reason"]


def test_telegram_source_url_uses_post_ref_when_owner_link_appears_first() -> None:
    target = NativeSourceTarget(
        platform="telegram",
        handle="@clearvisionary",
        audience_segment="developer_investor",
        content_theme="boutique_hotels",
    )

    items = collect_native_source_items(
        targets=[target],
        fetcher=lambda _url, _timeout: TELEGRAM_MULTI_POST_HTML,
        collected_at="2026-04-25T08:00:00Z",
    )

    assert items[0].source_url == "https://t.me/clearvisionary/102"
    assert items[0].raw_payload["source_post_url"] == "https://t.me/clearvisionary/102"


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
    assert items[0].raw_payload["video_title"] == "What cheap villas hide"
    assert items[0].raw_payload["caption_text"].startswith("Cheap villas are never actually cheap")
    assert items[0].raw_payload["transcript_source"] == "caption_or_description"
    assert items[0].engagement_signals["views"] == 4875
    assert items[0].routing_decision == "both"
    assert items[0].routing_reason == "video signal with textual depth"


def test_collect_native_source_items_ignores_empty_youtube_thumbnail_url() -> None:
    target = NativeSourceTarget(
        platform="youtube",
        handle="UC1234567890",
        audience_segment="developer_investor",
        content_theme="boutique_hotels",
    )
    rss_without_thumbnail_url = YOUTUBE_RSS.replace(
        'url="https://i.ytimg.com/vi/abc123/hqdefault.jpg"',
        'url=""',
    )

    items = collect_native_source_items(
        targets=[target],
        fetcher=lambda _url, _timeout: rss_without_thumbnail_url,
        collected_at="2026-04-24T08:00:00Z",
    )

    assert len(items) == 1
    assert items[0].media_urls == []


@pytest.mark.parametrize(
    ("platform", "url", "html", "expected_source_type", "expected_route"),
    [
        ("instagram", "https://www.instagram.com/reel/C123/", INSTAGRAM_HTML, "instagram_reel", "both"),
        ("linkedin", "https://www.linkedin.com/posts/founder-deal-logic-123/", LINKEDIN_HTML, "linkedin_post", "workflow_b"),
        ("tiktok", "https://www.tiktok.com/@jepro/video/777", TIKTOK_HTML, "tiktok_video", "both"),
        (
            "web",
            "https://www.realinfo.id/market-reports/bali-hotel-outlook-2026",
            WEB_HTML,
            "web_report",
            "workflow_b",
        ),
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
    if platform == "instagram":
        assert items[0].raw_payload["video_title"] == "Deal logic in Bali"
        assert items[0].raw_payload["caption_text"] == "Cheap villas are never actually cheap."
        assert "Speaker says" in items[0].raw_payload["spoken_transcript"]
        assert items[0].engagement_signals == {"views": 5200, "likes": 410, "comments": 38}


def test_tiktok_profile_scan_selects_best_performing_video_and_extracts_post_text() -> None:
    target = NativeSourceTarget(
        platform="tiktok",
        handle="@jepro",
        audience_segment="dreamer_woman",
        content_theme="bali_life",
        source_name="Jane TikTok",
    )

    items = collect_native_source_items(
        targets=[target],
        fetcher=lambda _url, _timeout: TIKTOK_PROFILE_HTML,
        collected_at="2026-04-26T08:00:00Z",
    )

    assert len(items) == 1
    item = items[0]
    assert item.source_type == "tiktok_video"
    assert item.source_url == "https://www.tiktok.com/@jepro/video/viral777"
    assert item.external_item_id == "viral777"
    assert item.engagement_signals == {
        "views": 48000,
        "likes": 5400,
        "comments": 380,
        "shares": 260,
        "saves": 920,
    }
    assert item.raw_payload["monitoring_selection"] == "best_performing_post"
    assert item.raw_payload["engagement_rank"] == 1
    assert item.raw_payload["scanned_posts_count"] == 2
    assert item.raw_payload["caption_text"].startswith("Why the new Bali cafe launch worked")
    assert "On-screen text" in item.raw_payload["image_text"]
    assert "Why the new Bali cafe launch worked" in item.transcript_text
    assert "On-screen text" in item.transcript_text
    assert item.routing_decision == "both"


def test_tiktok_profile_falls_back_to_apify_when_public_html_has_no_posts() -> None:
    target = NativeSourceTarget(
        platform="tiktok",
        handle="@baligasm",
        audience_segment="bali_life",
        content_theme="bali_travel",
        source_name="Baligasm TikTok",
    )

    items = collect_native_source_items(
        targets=[target],
        fetcher=lambda _url, _timeout: "<html><body>No public payload</body></html>",
        collected_at="2026-04-26T08:00:00Z",
        apify_tiktok_profile_fetcher=lambda _target, _timeout: APIFY_TIKTOK_PROFILE,
    )

    assert len(items) == 1
    item = items[0]
    assert item.source_type == "tiktok_video"
    assert item.source_url == "https://www.tiktok.com/@baligasm/video/viral_tiktok"
    assert item.external_item_id == "viral_tiktok"
    assert item.engagement_signals == {
        "views": 48000,
        "likes": 5400,
        "comments": 380,
        "shares": 260,
        "saves": 920,
    }
    assert item.raw_payload["monitoring_selection"] == "best_performing_post"
    assert item.raw_payload["scanned_posts_count"] == 2
    assert item.raw_payload["caption_text"].startswith("Why this Bali music event")
    assert item.media_urls == ["https://cdn.example.com/tiktok-cover.jpg"]


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


def test_collect_native_source_items_falls_back_to_apify_for_instagram_profiles() -> None:
    target = NativeSourceTarget(
        platform="instagram",
        handle="@annalutaeva",
        source_url="https://www.instagram.com/annalutaeva/",
        audience_segment="dreamer_woman",
        content_theme="founder_journey",
        source_name="Anna Lutaeva",
    )

    items = collect_native_source_items(
        targets=[target],
        fetcher=lambda _url, _timeout: INSTAGRAM_PROFILE_HTML,
        collected_at="2026-04-25T09:00:00Z",
        apify_profile_fetcher=lambda _target, _timeout: APIFY_INSTAGRAM_PROFILE,
    )

    assert len(items) == 1
    assert items[0].source_type == "instagram_reel"
    assert items[0].source_url == "https://www.instagram.com/p/DK63Cl4PL3W/"
    assert items[0].external_item_id == "3655476118233595350"
    assert items[0].published_at == "2025-06-15T11:28:54.000Z"
    assert items[0].engagement_signals["followers"] == 27476
    assert items[0].engagement_signals["video_views"] == 50191
    assert "больше рассказывать о своей жизни" in items[0].transcript_text
    assert items[0].raw_payload["monitoring_selection"] == "best_performing_post"
    assert items[0].routing_decision == "both"


def test_instagram_profile_targets_use_apify_without_public_html_fetch() -> None:
    target = NativeSourceTarget(
        platform="instagram",
        handle="@annalutaeva",
        source_url="https://www.instagram.com/annalutaeva/",
        audience_segment="dreamer_woman",
        content_theme="founder_journey",
        source_name="Anna Lutaeva",
    )

    def blocked_fetcher(_url: str, _timeout: float) -> str:
        raise TimeoutError("public Instagram profile HTML should not be fetched first")

    items = collect_native_source_items(
        targets=[target],
        fetcher=blocked_fetcher,
        collected_at="2026-04-25T09:00:00Z",
        apify_profile_fetcher=lambda _target, _timeout: APIFY_INSTAGRAM_PROFILE,
    )

    assert len(items) == 1
    assert items[0].source_url == "https://www.instagram.com/p/DK63Cl4PL3W/"
    assert items[0].raw_payload["monitoring_selection"] == "best_performing_post"


def test_instagram_profile_fallback_selects_best_performing_post_and_extracts_all_post_text() -> None:
    target = NativeSourceTarget(
        platform="instagram",
        handle="@annalutaeva",
        source_url="https://www.instagram.com/annalutaeva/",
        audience_segment="dreamer_woman",
        content_theme="founder_journey",
        source_name="Anna Lutaeva",
    )

    items = collect_native_source_items(
        targets=[target],
        fetcher=lambda _url, _timeout: INSTAGRAM_PROFILE_HTML,
        collected_at="2026-04-25T09:00:00Z",
        apify_profile_fetcher=lambda _target, _timeout: APIFY_INSTAGRAM_PROFILE_WITH_MIXED_POSTS,
    )

    assert len(items) == 1
    item = items[0]
    assert item.source_type == "instagram_post"
    assert item.source_url == "https://www.instagram.com/p/VIRAL/"
    assert item.external_item_id == "viral_carousel"
    assert item.published_at == "2026-04-24T10:00:00.000Z"
    assert item.engagement_signals == {
        "followers": 27476,
        "following": 4959,
        "posts": 1573,
        "likes": 5400,
        "comments": 320,
        "shares": 190,
        "saves": 870,
    }
    assert item.raw_payload["monitoring_selection"] == "best_performing_post"
    assert item.raw_payload["engagement_rank"] == 1
    assert item.raw_payload["scanned_posts_count"] == 3
    assert item.raw_payload["caption_text"] == "caption: why Bali life content worked this week"
    assert item.raw_payload["post_title"] == "Carousel title: Bali life hook"
    assert "Slide 1: The Bali life post" in item.raw_payload["carousel_text"]
    assert "OCR: first slide text" in item.raw_payload["image_text"]
    assert "Carousel title: Bali life hook" in item.transcript_text
    assert "caption: why Bali life content worked this week" in item.transcript_text
    assert "Slide 2: Proof beats postcard content" in item.transcript_text
