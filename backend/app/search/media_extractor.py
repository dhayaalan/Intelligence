"""
Normalized Media Extraction & Provenance Pipeline.
Surfaces genuine, source-backed Images and Videos from all intelligence module findings,
evidence payloads, and correlated entities.
"""

import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.module_sdk.models import EntityPayload, EntityType, EvidencePayload
from app.search.schemas import MediaRecord


class MediaNormalizationPipeline:
    """
    Extracts, validates, deduplicates, and bounds media records (Images and Videos)
    directly from correlated search entities and evidence records.
    """

    @classmethod
    def extract_media(
        cls,
        entities: List[EntityPayload],
        evidence_list: List[EvidencePayload],
        target_query: str = ""
    ) -> List[MediaRecord]:
        media_map: Dict[str, MediaRecord] = {}

        # 1. Extract directly from verified IMAGE and VIDEO entities
        for ent in entities:
            e_type = ent.type.value if hasattr(ent.type, "value") else str(ent.type)
            val = str(ent.value or "").strip()
            meta = ent.metadata or {}

            if e_type == "image":
                url = meta.get("url") or meta.get("image_url") or meta.get("canonical_url") or val
                if not url:
                    continue
                url_norm = url.strip()
                m_id = f"med_img_{hashlib.md5(url_norm.encode()).hexdigest()[:12]}"
                
                # Derive thumbnail
                thumb = meta.get("thumbnail_url") or meta.get("preview_url")
                if not thumb and (url_norm.startswith("http://") or url_norm.startswith("https://")):
                    thumb = url_norm

                media_map[url_norm] = MediaRecord(
                    id=m_id,
                    media_type="image",
                    url=url_norm,
                    thumbnail_url=thumb,
                    title=meta.get("title") or meta.get("filename") or f"Image: {val}",
                    description=meta.get("caption") or meta.get("description"),
                    source_provider=ent.sources[0] if ent.sources else "Visual Intelligence",
                    source_platform=meta.get("platform") or meta.get("source"),
                    parent_id=getattr(ent, "id", None),
                    parent_type="entity",
                    parent_title=val,
                    publication_date=meta.get("timestamp") or meta.get("publication_date"),
                    collection_date=meta.get("lookup_timestamp") or datetime.utcnow().isoformat(),
                    verification_status="VERIFIED" if ent.confidence >= 0.7 else "UNVERIFIED",
                    canonical_source_url=meta.get("source_url") or (url_norm if url_norm.startswith("http") else None),
                    evidence_ids=[],
                    metadata=meta
                )

            elif e_type == "video":
                url = meta.get("canonical_url") or meta.get("video_url") or val
                if not url:
                    continue
                url_norm = url.strip()
                v_id = meta.get("video_id")
                m_id = f"med_vid_{hashlib.md5(url_norm.encode()).hexdigest()[:12]}"
                
                thumb = meta.get("thumbnail_url") or meta.get("thumbnail")
                if not thumb and v_id:
                    thumb = f"https://img.youtube.com/vi/{v_id}/hqdefault.jpg"

                media_map[url_norm] = MediaRecord(
                    id=m_id,
                    media_type="video",
                    url=url_norm,
                    thumbnail_url=thumb,
                    title=meta.get("title") or meta.get("channel") or f"Video: {val}",
                    description=meta.get("description") or meta.get("summary"),
                    source_provider=ent.sources[0] if ent.sources else "Video Forensics",
                    source_platform=meta.get("platform") or "YouTube",
                    parent_id=getattr(ent, "id", None),
                    parent_type="entity",
                    parent_title=val,
                    publication_date=meta.get("published_at") or meta.get("publication_date"),
                    collection_date=datetime.utcnow().isoformat(),
                    verification_status="VERIFIED",
                    canonical_source_url=url_norm if url_norm.startswith("http") else None,
                    evidence_ids=[],
                    metadata=meta
                )

        # 2. Extract media from Evidence payloads
        for ev in evidence_list:
            raw = getattr(ev, "raw_data", None) or {}
            ev_id = getattr(ev, "id", None) or getattr(ev, "hash", None) or f"ev_{hashlib.md5(str(raw).encode()).hexdigest()[:10]}"
            ev_provider = getattr(ev, "provider", None) or getattr(ev, "source", None) or "Media Intelligence"
            ev_time = getattr(ev, "timestamp", None)
            time_iso = ev_time.isoformat() if hasattr(ev_time, "isoformat") else (str(ev_time) if ev_time else None)
            ref_content = getattr(ev, "reference", "") or ""

            # A. Video from Evidence (YouTube, Social video, News video)
            video_id = raw.get("video_id")
            video_url = raw.get("canonical_url") or raw.get("video_url")
            if not video_url and video_id:
                video_url = f"https://youtube.com/watch?v={video_id}"
            
            if video_url:
                v_url_norm = video_url.strip()
                thumb = raw.get("thumbnail") or raw.get("thumbnail_url")
                if not thumb and video_id:
                    thumb = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                
                if v_url_norm in media_map:
                    if ev_id not in media_map[v_url_norm].evidence_ids:
                        media_map[v_url_norm].evidence_ids.append(ev_id)
                else:
                    media_map[v_url_norm] = MediaRecord(
                        id=f"med_vid_{hashlib.md5(v_url_norm.encode()).hexdigest()[:12]}",
                        media_type="video",
                        url=v_url_norm,
                        thumbnail_url=thumb,
                        title=raw.get("title") or getattr(ev, "title", None) or f"Video target ({video_id or v_url_norm})",
                        description=raw.get("description") or raw.get("summary") or ref_content,
                        source_provider=ev_provider,
                        source_platform=raw.get("platform") or "YouTube",
                        parent_id=ev_id,
                        parent_type="evidence",
                        parent_title=target_query,
                        publication_date=raw.get("published_at") or raw.get("publication_date") or time_iso,
                        collection_date=time_iso or datetime.utcnow().isoformat(),
                        verification_status="VERIFIED" if getattr(ev, "confidence", 1.0) >= 0.7 else "UNVERIFIED",
                        canonical_source_url=v_url_norm,
                        evidence_ids=[ev_id],
                        metadata=raw
                    )

            # B. Images from Evidence (News lead image, Social post media URLs, EXIF forensic images)
            images_found = []
            if raw.get("lead_image_url"):
                images_found.append((raw["lead_image_url"], raw.get("title"), "article_image"))
            if raw.get("image_url"):
                images_found.append((raw["image_url"], raw.get("title"), "lead_image"))
            
            for m_url in raw.get("media_urls", []):
                if isinstance(m_url, str) and any(m_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif", "/photo/"]):
                    images_found.append((m_url, raw.get("content") or raw.get("title"), "post_media"))
                elif isinstance(m_url, dict) and m_url.get("url"):
                    images_found.append((m_url["url"], m_url.get("alt") or raw.get("title"), "post_media"))

            for img_url, img_title, img_context in images_found:
                if not img_url or not str(img_url).strip().startswith("http"):
                    continue
                img_norm = str(img_url).strip()
                if img_norm in media_map:
                    if ev_id not in media_map[img_norm].evidence_ids:
                        media_map[img_norm].evidence_ids.append(ev_id)
                else:
                    media_map[img_norm] = MediaRecord(
                        id=f"med_img_{hashlib.md5(img_norm.encode()).hexdigest()[:12]}",
                        media_type="image",
                        url=img_norm,
                        thumbnail_url=img_norm,
                        title=img_title or f"Media image from {ev_provider}",
                        description=ref_content if len(ref_content) <= 150 else f"{ref_content[:147]}...",
                        source_provider=ev_provider,
                        source_platform=raw.get("publisher") or raw.get("platform") or "Web Source",
                        parent_id=ev_id,
                        parent_type="evidence",
                        parent_title=target_query,
                        publication_date=raw.get("publication_date") or raw.get("published_at") or time_iso,
                        collection_date=time_iso or datetime.utcnow().isoformat(),
                        verification_status="VERIFIED" if getattr(ev, "confidence", 1.0) >= 0.7 else "UNVERIFIED",
                        canonical_source_url=raw.get("url") or raw.get("canonical_url") or img_norm,
                        evidence_ids=[ev_id],
                        metadata={"context": img_context, **raw}
                    )

        # Sort: Videos first, then images ordered by publication or collection date
        result_list = list(media_map.values())
        result_list.sort(key=lambda m: (m.media_type == "video", m.publication_date or m.collection_date or ""), reverse=True)
        return result_list


media_pipeline = MediaNormalizationPipeline()
