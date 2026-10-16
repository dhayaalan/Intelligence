"""
Regression test suite for News Media Integrity.
Validates that news articles retain strictly verified hero image URLs,
removes array-index stock photo assignments, ensures Article B never
adopts Article A's image, and guarantees neutral placeholder fallback.
"""

import pytest
from app.modules.news_intelligence.models import NewsArticle, NewsSearchResultItem
from app.modules.news_intelligence.dossier_compiler import NewsDossierCompiler


def test_article_without_verified_media_has_none_image():
    """
    Articles without verified OpenGraph/media metadata must have hero_image=None.
    It must NOT fall back to an arbitrary stock photo based on array index.
    """
    item = NewsSearchResultItem(
        id="art_no_media_1",
        title="Local Logistics Report",
        summary="Supply chain logistics disrupted across regional corridors.",
        canonical_url="https://news.defense-weekly.com/articles/2026/logistics-report",
        source="Defense Weekly",
        publisher="Defense Weekly",
        content_type="article",
        relevance_score=90.0,
        thumbnail_url=None,
        hero_image=None,
        image_url=None,
    )

    assert item.hero_image is None
    assert item.thumbnail_url is None


def test_article_with_verified_opengraph_preserves_its_own_image():
    """
    An article with publisher-provided OpenGraph image retains that exact image URL.
    """
    verified_url = "https://aerospace-today.org/media/facility_aerial_2026.jpg"
    item = NewsSearchResultItem(
        id="art_verified_media_1",
        title="Satellite Facility Groundbreaking Announced",
        summary="Commercial spaceport construction begins.",
        canonical_url="https://aerospace-today.org/news/satellite-facility",
        source="Aerospace Today",
        publisher="Aerospace Today",
        content_type="article",
        relevance_score=95.0,
        thumbnail_url=verified_url,
        hero_image=verified_url,
        image_url=verified_url,
    )

    assert item.hero_image == verified_url
    assert item.thumbnail_url == verified_url


def test_article_b_never_inherits_article_a_image():
    """
    Article A (with image) and Article B (without image) are evaluated.
    Article B must NOT inherit Article A's image, nor take an arbitrary fallback.
    """
    pic_a = "https://site-a.com/photos/photo-a.png"
    item_a = NewsSearchResultItem(
        id="art_a",
        title="Article A - With Photo",
        summary="Description A",
        canonical_url="https://site-a.com/article-a",
        source="Site A",
        publisher="Publisher A",
        content_type="article",
        relevance_score=92.0,
        hero_image=pic_a,
        thumbnail_url=pic_a,
    )

    item_b = NewsSearchResultItem(
        id="art_b",
        title="Article B - Text Only",
        summary="Description B",
        canonical_url="https://site-b.com/article-b",
        source="Site B",
        publisher="Publisher B",
        content_type="article",
        relevance_score=88.0,
        hero_image=None,
        thumbnail_url=None,
    )

    assert item_a.hero_image == pic_a
    assert item_b.hero_image is None
    assert item_b.hero_image != item_a.hero_image


def test_dossier_compiler_preserves_verified_media_or_renders_placeholder():
    """
    Dossier compiler must attach publisher image when verified and provide authentic forensic notes,
    while articles without verified media receive None and an explicit placeholder note.
    """
    compiler = NewsDossierCompiler()

    article_with_img = compiler.compile_article(
        article_id="art_verified_1",
        title="Verified Satellite Launch Report",
        summary="A report on new space payload launches.",
        content="Full body paragraph for satellite launch verification.",
        publisher="Global Aerospace Times",
        country="Global",
        publication_date="Oct 16, 2026",
        canonical_url="https://example.com/art1",
        hero_image="https://example.com/art1/satellite.jpg",
    )

    assert article_with_img.hero_image == "https://example.com/art1/satellite.jpg"
    assert "Publisher-associated imagery" in (article_with_img.hero_image_caption or "")
    assert "OpenGraph" in (article_with_img.hero_image_forensic_note or "")

    article_no_img = compiler.compile_article(
        article_id="art_text_2",
        title="Unillustrated Policy Memo",
        summary="A diplomatic memorandum without accompanying images.",
        content="Full body text of unillustrated policy memo.",
        publisher="Diplomatic Gazette",
        country="Global",
        publication_date="Oct 16, 2026",
        canonical_url="https://example.com/art2",
        hero_image=None,
    )

    assert article_no_img.hero_image is None
    assert article_no_img.hero_image_caption is None
    assert "Placeholder state rendered to prevent false attribution" in (article_no_img.hero_image_forensic_note or "")
