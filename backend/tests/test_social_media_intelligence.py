import pytest
from fastapi.testclient import TestClient
from app.modules.social_media_intelligence.models import (
    SocialPost,
    SocialPlatformType,
    CibCluster,
    CredibilityScore,
    CredibilityBand
)
from app.modules.social_media_intelligence.engines.cib_engine import cib_engine
from app.modules.social_media_intelligence.engines.credibility_engine import credibility_engine
from app.modules.social_media_intelligence.collectors.bluesky import bluesky_collector
from app.modules.social_media_intelligence.collectors.telegram import telegram_collector
from app.modules.social_media_intelligence.collectors.reddit import reddit_collector
from app.modules.social_media_intelligence.collectors.mastodon import mastodon_collector
from app.modules.social_media_intelligence.collectors.youtube import youtube_collector
from app.module_registry.registry import module_registry
from app.module_sdk.models import SearchContext


def test_cib_engine_detection():
    # Construct 2 posts from distinct accounts with identical phrases and same timestamp
    now = "2026-10-09T10:00:00+00:00"
    posts = [
        SocialPost(
            id="p1",
            platform=SocialPlatformType.BLUESKY,
            author="@bot_net_alpha",
            author_id="did:plc:001",
            text="URGENT: Global alert regarding network telemetry infrastructure disruption happening now",
            created_at=now,
            url="https://bsky.app/p1",
            links=["https://disrupt.io/incident-404"]
        ),
        SocialPost(
            id="p2",
            platform=SocialPlatformType.TELEGRAM,
            author="@bot_net_beta",
            author_id="tg:002",
            text="URGENT: Global alert regarding network telemetry infrastructure disruption happening now",
            created_at=now,
            url="https://t.me/channel/2",
            links=["https://disrupt.io/incident-404"]
        )
    ]

    clusters = cib_engine.detect_clusters(posts)
    assert len(clusters) > 0
    c = clusters[0]
    assert c.account_count == 2
    assert "@bot_net_alpha" in c.accounts
    assert "@bot_net_beta" in c.accounts
    assert c.coordination_confidence >= 80.0
    assert "signals warranting review" in c.caveat_warning.lower()


def test_credibility_engine_scoring():
    posts = [
        SocialPost(
            id=f"post_{i}",
            platform=SocialPlatformType.REDDIT,
            author="u/organic_researcher",
            author_id="usr_01",
            text=f"Discussion thread topic {i}: security analysis and network telemetry",
            created_at="2026-10-09T08:00:00+00:00",
            url=f"https://reddit.com/r/netsec/{i}",
            links=[f"https://domain-{i}.com/report"]
        ) for i in range(10)
    ]

    score = credibility_engine.score_account(
        target_handle="u/organic_researcher",
        platform=SocialPlatformType.REDDIT,
        posts=posts,
        account_age_days=365,
        has_custom_avatar=True
    )

    assert score.overall_score >= 70.0
    assert score.band in [CredibilityBand.HIGH, CredibilityBand.MODERATE]
    assert score.bot_probability <= 0.35
    assert "velocity" in score.factors


def test_youtube_collector_extraction():
    vid_id = youtube_collector.extract_video_id("https://www.youtube.com/watch?v=wb_DPZnYx04")
    assert vid_id == "wb_DPZnYx04"

    vid_short = youtube_collector.extract_video_id("https://youtu.be/wb_DPZnYx04")
    assert vid_short == "wb_DPZnYx04"


def test_social_module_contract_search(monkeypatch):
    import asyncio
    async def mock_posts(query, limit=25, job_id=None):
        return [
            SocialPost(
                id="test_post_01",
                platform=SocialPlatformType.MASTODON,
                author="@test_analyst@infosec.exchange",
                author_id="masto_usr_1",
                text="Observed cyber threat campaign telemetry across federated relays",
                created_at="2026-10-14T10:00:00Z",
                url="https://infosec.exchange/@test_analyst/1001",
                links=["https://threat-intel.org/ioc"],
                entities=["threat", "campaign"],
                credibility_score=85.0
            )
        ]
    monkeypatch.setattr(bluesky_collector, "search_posts", mock_posts)

    async def _test():
        mod = module_registry.get_module("social_media_intelligence")
        assert mod is not None
        assert "social_search" in await mod.capabilities()

        ctx = SearchContext(
            search_id="test_srch_01",
            query="cyber threat campaign",
            user_id="usr_analyst",
            tenant_id="tenant_acme",
            target_type="GENERAL"
        )
        result = await mod.search(ctx)
        assert result.module == "social_media_intelligence"
        assert len(result.entities) > 0
        assert len(result.evidence) > 0
        assert "posts" in result.metadata
    asyncio.run(_test())


def test_api_social_search(client: TestClient, super_admin_headers):
    payload = {
        "query": "malware infrastructure",
        "platforms": ["bluesky", "telegram", "reddit"],
        "limit": 10,
        "detect_cib": True
    }
    res = client.post("/api/v1/social/search", json=payload, headers=super_admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["search_id"].startswith("soc_")
    assert data["query"] == "malware infrastructure"
    assert "results" in data
    assert "provider_statuses" in data
    assert len(data["provider_statuses"]) > 0


def test_api_cib_analysis(client: TestClient, super_admin_headers):
    payload = [
        {
            "id": "c1",
            "platform": "bluesky",
            "author": "@user_a",
            "author_id": "did:a",
            "text": "Coordinated dispatch broadcast notice for all stations",
            "created_at": "2026-10-09T10:00:00+00:00",
            "url": "https://bsky.app/c1",
            "links": ["https://alert.org/event"]
        },
        {
            "id": "c2",
            "platform": "telegram",
            "author": "@user_b",
            "author_id": "did:b",
            "text": "Coordinated dispatch broadcast notice for all stations",
            "created_at": "2026-10-09T10:00:15+00:00",
            "url": "https://t.me/c2",
            "links": ["https://alert.org/event"]
        }
    ]
    res = client.post("/api/v1/social/analyze/cib", json=payload, headers=super_admin_headers)
    assert res.status_code == 200
    clusters = res.json()
    assert len(clusters) > 0
    assert clusters[0]["account_count"] == 2


def test_api_youtube_investigation(client: TestClient, super_admin_headers):
    res = client.post(
        "/api/v1/social/youtube/video",
        json={"video_url_or_id": "wb_DPZnYx04"},
        headers=super_admin_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["metadata"]["video_id"] == "wb_DPZnYx04"
    assert data["subtitles"] is not None
    # Subtitle honesty: When authentic captions are not accessible, status must be TRANSCRIPT_UNAVAILABLE
    # and placeholder/synthetic segments must never be fabricated.
    assert data["subtitles"]["status"] == "TRANSCRIPT_UNAVAILABLE"
    assert len(data["subtitles"]["segments"]) == 0
    assert data["metadata"]["transcript_status"] == "TRANSCRIPT_UNAVAILABLE"


@pytest.mark.asyncio
async def test_resilient_crawler_local_extraction():
    from app.modules.social_media_intelligence.crawler_engine import resilient_social_crawler

    html = '''<!DOCTYPE html>
    <html>
    <head>
        <title>Leaked Intel Report 2026</title>
        <meta property="og:title" content="Leaked Network Asset Vulnerabilities">
        <meta property="og:description" content="Detailed analysis of exposed perimeter infrastructure and CCTV telemetry for @target_analyst. Contact lead@sec.org">
        <meta property="og:image" content="https://example.com/evidence.jpg">
        <meta name="author" content="ThreatScout">
    </head>
    <body>
        <h1>Perimeter Breach Notice</h1>
        <p>Investigation notes for #cyberthreat intelligence.</p>
        <div class="comment-body">Excellent report on vulnerability remediation.</div>
    </body>
    </html>'''

    result = await resilient_social_crawler._extract_intelligence_from_page(
        html=html,
        original_url="https://x.com/target_analyst/status/1234567890",
        final_url="https://x.com/target_analyst/status/1234567890",
        platform="twitter",
        post_type="post",
        status_code=200,
        bypass_strategy="DIRECT_STEALTH",
        is_blocked=False,
        extract_media=True,
        extract_comments=True,
        extract_entities=True,
        extra_meta={}
    )
    assert result.platform == "twitter"
    assert result.title == "Leaked Network Asset Vulnerabilities"
    assert "Detailed analysis" in result.text
    assert result.author == "ThreatScout"
    assert "https://example.com/evidence.jpg" in result.media_urls
    assert any("@target_analyst" in e for e in result.extracted_entities)
    assert len(result.comments) >= 1
    assert "remediation" in result.comments[0].text


@pytest.mark.asyncio
async def test_instagram_reel_and_comment_extraction():
    from app.modules.social_media_intelligence.crawler_engine import resilient_social_crawler

    reel_html = '''<!DOCTYPE html>
    <html>
    <head>
        <title>Instagram Reel</title>
        <meta property="og:title" content="Drone Patrol Reel">
        <meta property="og:video" content="https://cdninstagram.com/reel/drone_feed.mp4">
        <meta property="og:image" content="https://cdninstagram.com/reel/poster.jpg">
    </head>
    <body>
        <div class="Caption">Aerial patrol footage recording movement along sector 4. #surveillance</div>
        <span class="UsernameText">@aerial_patrol_unit</span>
        <div class="Feedback">14.5k likes 340 comments</div>
        <script type="application/ld+json">
        {
            "@type": "SocialMediaPosting",
            "headline": "Aerial surveillance footage",
            "comment": [
                {"@type": "Comment", "text": "Confirmed visual on vehicle tag", "author": {"name": "dispatcher_01"}}
            ]
        }
        </script>
    </body>
    </html>'''

    reel_url = "https://www.instagram.com/reel/C8xyz9876/"
    post_type = resilient_social_crawler.detect_post_type(reel_url)
    assert post_type == "reel"

    result = await resilient_social_crawler._extract_intelligence_from_page(
        html=reel_html,
        original_url=reel_url,
        final_url=reel_url,
        platform="instagram",
        post_type=post_type,
        status_code=200,
        bypass_strategy="INSTAGRAM_EMBED_BYPASS",
        is_blocked=False,
        extract_media=True,
        extract_comments=True,
        extract_entities=True,
        extra_meta={}
    )

    assert result.platform == "instagram"
    assert result.post_type == "reel"
    assert result.video_url == "https://cdninstagram.com/reel/drone_feed.mp4"
    assert "Aerial patrol footage" in result.text
    assert result.author == "@aerial_patrol_unit"
    assert result.likes_count == 14500
    assert len(result.comments) >= 1
    assert result.comments[0].author == "dispatcher_01"
    assert "Confirmed visual" in result.comments[0].text


@pytest.mark.asyncio
async def test_facebook_post_and_comment_extraction():
    from app.modules.social_media_intelligence.crawler_engine import resilient_social_crawler

    fb_html = '''<!DOCTYPE html>
    <html>
    <head>
        <title>Facebook Video</title>
        <meta property="og:title" content="Checkpoint Video Incident">
        <meta property="og:description" content="Dashcam footage of suspicious crossing attempt.">
        <meta property="og:video" content="https://video.xx.fbcdn.net/dashcam.mp4">
        <meta name="author" content="Border Watch Network">
    </head>
    <body>
        <p>Full incident report filed with municipal command.</p>
        <div data-sigil="comment-body">Verified with ANPR logs from station 2.</div>
    </body>
    </html>'''

    fb_url = "https://www.facebook.com/watch/?v=9876543210"
    post_type = resilient_social_crawler.detect_post_type(fb_url)
    assert post_type == "video"

    result = await resilient_social_crawler._extract_intelligence_from_page(
        html=fb_html,
        original_url=fb_url,
        final_url=fb_url,
        platform="facebook",
        post_type=post_type,
        status_code=200,
        bypass_strategy="FACEBOOK_OEMBED_BYPASS",
        is_blocked=False,
        extract_media=True,
        extract_comments=True,
        extract_entities=True,
        extra_meta={}
    )

    assert result.platform == "facebook"
    assert result.post_type == "video"
    assert result.video_url == "https://video.xx.fbcdn.net/dashcam.mp4"
    assert "Incident" in result.title
    assert len(result.comments) >= 1
    assert "Verified with ANPR logs" in result.comments[0].text


def test_api_crawl_url_endpoint(client: TestClient, super_admin_headers):
    from unittest.mock import patch
    from app.modules.social_media_intelligence.models import SocialCrawlResult, SocialCommentItem

    fake_result = SocialCrawlResult(
        url="https://instagram.com/reel/test1234",
        final_url="https://instagram.com/reel/test1234",
        platform="instagram",
        post_type="reel",
        title="Verified Case Footage",
        text="Surveillance recording of target license plate at highway checkpoint.",
        author="@traffic_unit",
        published_at="2026-10-22T12:00:00Z",
        media_urls=["https://instagram.com/media/test.jpg", "https://cdninstagram.com/video.mp4"],
        video_url="https://cdninstagram.com/video.mp4",
        likes_count=1200,
        comments_count=15,
        comments=[
            SocialCommentItem(author="inspector_dave", text="Identified matching plate in Sector B")
        ],
        bypass_technique="INSTAGRAM_EMBED_BYPASS",
        http_status=200,
        is_blocked_url=False,
        extracted_entities=["@traffic_unit"]
    )

    with patch("app.modules.social_media_intelligence.crawler_engine.resilient_social_crawler.crawl_url") as mock_crawl:
        async def fake_crawl(*args, **kwargs):
            return fake_result
        mock_crawl.side_effect = fake_crawl

        res = client.post(
            "/api/v1/social/crawl-url",
            json={"url": "https://instagram.com/reel/test1234", "bypass_blocking": True, "extract_comments": True},
            headers=super_admin_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["platform"] == "instagram"
        assert data["post_type"] == "reel"
        assert data["video_url"] == "https://cdninstagram.com/video.mp4"
        assert data["author"] == "@traffic_unit"
        assert len(data["comments"]) == 1
        assert data["comments"][0]["author"] == "inspector_dave"

