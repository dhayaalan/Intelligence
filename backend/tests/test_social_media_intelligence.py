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


def test_social_module_contract_search():
    import asyncio
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
    assert len(data["results"]) > 0


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
    assert len(data["subtitles"]["segments"]) > 0
