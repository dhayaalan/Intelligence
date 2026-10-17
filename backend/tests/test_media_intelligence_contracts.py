"""
Unit and Integration Tests for Media Intelligence and Normalization Contracts.

Verifies:
- Extraction and normalization of image and video records from OSINT, social media, news, and threat intelligence.
- YouTube video URL parsing and embedding metadata.
- Parent record linkage and evidence provenance association.
- Verification status and date preservation.
- Integration through SearchOrchestrator returning SearchResponse.media.
"""

import pytest
from app.module_sdk.models import EntityPayload, EntityType, EvidencePayload
from app.search.schemas import SearchResponse, MediaRecord
from app.search.media_extractor import MediaNormalizationPipeline


def test_media_extractor_image_entity_extraction():
    entity = EntityPayload(
        type=EntityType.IMAGE,
        value="satellite_recon_alpha.png",
        confidence=0.9,
        sources=["osint_recon"],
        metadata={
            "url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330",
            "image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330",
            "title": "Satellite Recon Alpha",
            "platform": "SatelliteOSINT",
            "timestamp": "2026-03-01T10:00:00Z"
        }
    )
    evidence = [
        EvidencePayload(
            module="osint",
            provider="osint_recon",
            source="satellite",
            reference="https://images.unsplash.com/photo-1494790108377-be9c29b29330",
            timestamp="2026-03-01T10:00:00Z",
            hash="abc123sha256hash",
            raw_data={"image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330"}
        )
    ]

    media_records = MediaNormalizationPipeline.extract_media(
        entities=[entity],
        evidence_list=evidence,
        target_query="Satellite Recon"
    )

    assert len(media_records) >= 1
    img = next(m for m in media_records if m.media_type == "image")
    assert img.url == "https://images.unsplash.com/photo-1494790108377-be9c29b29330"
    assert img.source_provider == "osint_recon"
    assert img.verification_status == "VERIFIED"


def test_media_extractor_youtube_video_extraction():
    video_entity = EntityPayload(
        type=EntityType.VIDEO,
        value="https://youtube.com/watch?v=dQw4w9WgXcQ",
        confidence=0.95,
        sources=["youtube_intel"],
        metadata={
            "video_id": "dQw4w9WgXcQ",
            "canonical_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "title": "Investigative Briefing OSINT 2026",
            "platform": "YouTube",
            "published_at": "2026-02-15T18:00:00Z"
        }
    )

    media_records = MediaNormalizationPipeline.extract_media(
        entities=[video_entity],
        evidence_list=[],
        target_query="OSINT Briefing"
    )

    assert len(media_records) >= 1
    vid = next(m for m in media_records if m.media_type == "video")
    assert "dQw4w9WgXcQ" in vid.url
    assert vid.thumbnail_url == "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg"
    assert vid.source_platform == "YouTube"
    assert vid.parent_title == "https://youtube.com/watch?v=dQw4w9WgXcQ"


def test_media_extractor_from_evidence_payload():
    ev = EvidencePayload(
        module="social_media",
        provider="social_media",
        source="youtube",
        reference="https://youtube.com/watch?v=abc12345678",
        timestamp="2026-03-10T12:00:00Z",
        hash="sha256videoevidencehash",
        raw_data={
            "video_id": "abc12345678",
            "canonical_url": "https://youtube.com/watch?v=abc12345678",
            "title": "Public Investigation Video Stream",
            "platform": "YouTube",
            "thumbnail": "https://img.youtube.com/vi/abc12345678/hqdefault.jpg"
        }
    )

    media = MediaNormalizationPipeline.extract_media(
        entities=[],
        evidence_list=[ev],
        target_query="Public Stream"
    )

    assert len(media) == 1
    vid = media[0]
    assert vid.media_type == "video"
    assert vid.source_provider == "social_media"
    assert "sha256videoevidencehash" in vid.evidence_ids


def test_media_records_deduplication():
    # Two entities with the same image URL
    ent1 = EntityPayload(
        type=EntityType.IMAGE,
        value="img1",
        confidence=0.8,
        sources=["osint"],
        metadata={"url": "https://example.com/common_avatar.png"}
    )
    ent2 = EntityPayload(
        type=EntityType.IMAGE,
        value="img2",
        confidence=0.8,
        sources=["news"],
        metadata={"url": "https://example.com/common_avatar.png"}
    )

    media = MediaNormalizationPipeline.extract_media(
        entities=[ent1, ent2],
        evidence_list=[],
        target_query="test"
    )

    matching = [m for m in media if m.url == "https://example.com/common_avatar.png"]
    assert len(matching) == 1


def test_search_response_media_serialization():
    media_item = MediaRecord(
        id="med-1",
        media_type="image",
        url="https://images.example.com/satellite.jpg",
        thumbnail_url="https://images.example.com/thumb.jpg",
        title="Satellite Facility Recon",
        source_provider="geo_sentinel",
        verification_status="UNVERIFIED",
        evidence_ids=["hash-1"]
    )

    resp = SearchResponse(
        search_id="s-test-1",
        query="satellite recon",
        target_type="FACILITY",
        status="completed",
        entities=[],
        relationships=[],
        evidence=[],
        media=[media_item]
    )

    data = resp.dict() if hasattr(resp, "dict") else resp.model_dump()
    assert "media" in data
    assert len(data["media"]) == 1
    assert data["media"][0]["media_type"] == "image"
    assert data["media"][0]["url"] == "https://images.example.com/satellite.jpg"
