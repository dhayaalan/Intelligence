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


def is_safe_media_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    u = url.strip().lower()
    if not (u.startswith("http://") or u.startswith("https://")):
        return False
    # SSRF protection: reject local and internal addresses
    bad_hosts = ["localhost", "127.0.0.1", "0.0.0.0", "169.254.", "::1", "metadata.google.internal"]
    for bh in bad_hosts:
        if f"://{bh}" in u or f"@{bh}" in u:
            return False
    # Filter out text documents / scripts
    bad_exts = [".html", ".htm", ".php", ".asp", ".aspx", ".pdf", ".txt", ".json", ".xml"]
    clean_path = u.split("?")[0].split("#")[0]
    for be in bad_exts:
        if clean_path.endswith(be):
            return False
    return True


class MediaNormalizationPipeline:
    """
    Extracts, validates, deduplicates, and bounds media records (Images and Videos)
    directly from correlated search entities, social accounts, news, and evidence records.
    """

    @classmethod
    def extract_media(
        cls,
        entities: List[EntityPayload],
        evidence_list: List[EvidencePayload],
        target_query: str = ""
    ) -> List[MediaRecord]:
        media_map: Dict[str, MediaRecord] = {}

        # 1. Extract from all verified entities (IMAGE, VIDEO, and entity metadata like avatar_url/profile_image)
        for ent in entities:
            e_type = ent.type.value if hasattr(ent.type, "value") else str(ent.type)
            val = str(ent.value or "").strip()
            meta = ent.metadata or {}

            if e_type == "image":
                url = meta.get("url") or meta.get("image_url") or meta.get("canonical_url") or val
                if not is_safe_media_url(url):
                    continue
                url_norm = url.strip()
                m_id = f"med_img_{hashlib.md5(url_norm.encode()).hexdigest()[:12]}"
                
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
                if not is_safe_media_url(url):
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

            else:
                # Capture profile images, avatars, and hero media from any other entity
                ent_media_url = (
                    meta.get("avatar_url") or meta.get("profile_image_url") or
                    meta.get("profile_image") or meta.get("image_url") or
                    meta.get("hero_image") or meta.get("hero_image_url") or
                    meta.get("thumbnail_url")
                )
                if is_safe_media_url(ent_media_url):
                    norm_url = ent_media_url.strip()
                    if norm_url not in media_map:
                        m_id = f"med_img_{hashlib.md5(norm_url.encode()).hexdigest()[:12]}"
                        media_map[norm_url] = MediaRecord(
                            id=m_id,
                            media_type="image",
                            url=norm_url,
                            thumbnail_url=norm_url,
                            title=meta.get("name") or meta.get("username") or f"{val} Profile Image",
                            description=f"Avatar / media attached to {e_type} entity '{val}'",
                            source_provider=(ent.sources[0] if getattr(ent, "sources", None) else getattr(ent, "source", None)) or "Profile Intelligence",
                            source_platform=meta.get("platform") or "Social Profile",
                            parent_id=getattr(ent, "id", None),
                            parent_type="entity",
                            parent_title=val,
                            publication_date=meta.get("timestamp") or meta.get("publication_date"),
                            collection_date=meta.get("lookup_timestamp") or datetime.utcnow().isoformat(),
                            verification_status="VERIFIED" if (getattr(ent, "confidence", 1.0) or 1.0) >= 0.7 else "UNVERIFIED",
                            canonical_source_url=meta.get("profile_url") or meta.get("source_url") or norm_url,
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
            
            if is_safe_media_url(video_url):
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

            # B. Images from Evidence (News lead image, Social post media URLs, EXIF forensic images, attachments)
            images_found = []
            if raw.get("lead_image_url"):
                images_found.append((raw["lead_image_url"], raw.get("title"), "article_image"))
            if raw.get("image_url"):
                images_found.append((raw["image_url"], raw.get("title"), "lead_image"))
            if raw.get("hero_image"):
                images_found.append((raw["hero_image"], raw.get("title"), "hero_image"))
            if raw.get("avatar_url"):
                images_found.append((raw["avatar_url"], raw.get("author") or raw.get("title"), "avatar"))
            
            # Additional image arrays (media_urls, images, attachments)
            candidate_media_lists = [
                raw.get("media_urls", []),
                raw.get("images", []),
                raw.get("attachments", [])
            ]
            for m_list in candidate_media_lists:
                if not isinstance(m_list, list):
                    continue
                for m_item in m_list:
                    if isinstance(m_item, str) and is_safe_media_url(m_item):
                        images_found.append((m_item, raw.get("content") or raw.get("title"), "post_media"))
                    elif isinstance(m_item, dict) and m_item.get("url") and is_safe_media_url(m_item["url"]):
                        images_found.append((m_item["url"], m_item.get("alt") or raw.get("title"), "post_media"))

            for img_url, img_title, img_context in images_found:
                if not is_safe_media_url(img_url):
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
