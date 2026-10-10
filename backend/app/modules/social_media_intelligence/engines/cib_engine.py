import re
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple
from app.modules.social_media_intelligence.models import SocialPost, CibCluster

CIB_CAVEAT_DISCLAIMER = (
    "These are signals warranting review, not an automated determination of inauthenticity. "
    "Legitimate campaigns (newsrooms, volunteer groups, public emergency notices) can exhibit "
    "similar rapid cross-account dissemination. Check the specific account timings and references."
)

class CIBEngine:
    """
    Coordinated Inauthentic Behavior (CIB) Detection Engine.
    Detects synchronized message posting, phrase shingle duplication, and URL amplification bursts.
    """

    def __init__(self, burst_window_seconds: float = 60.0):
        self.burst_window_seconds = burst_window_seconds

    def normalize_text(self, text: str) -> str:
        clean = (text or "").lower()
        clean = re.sub(r'https?://\S+', ' ', clean)
        clean = re.sub(r'@[\w.:-]+', ' ', clean)
        clean = re.sub(r'[#$]', ' ', clean)
        clean = re.sub(r'[^\w\s]', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()

    def extract_shingles(self, text: str, k: int = 5) -> Set[str]:
        words = self.normalize_text(text).split()
        if not words:
            return set()
        if len(words) < k:
            return {" ".join(words)}
        return {" ".join(words[i:i + k]) for i in range(len(words) - k + 1)}

    def compute_shingle_similarity(self, text_a: str, text_b: str, k: int = 5) -> float:
        sa = self.extract_shingles(text_a, k)
        sb = self.extract_shingles(text_b, k)
        if not sa or not sb:
            return 0.0
        shared = len(sa & sb)
        return shared / len(sa | sb)

    def parse_timestamp(self, ts_str: str) -> float:
        try:
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            return dt.timestamp()
        except Exception:
            return 0.0

    def detect_clusters(self, posts: List[SocialPost]) -> List[CibCluster]:
        """
        Groups posts into CIB clusters if distinct accounts publish highly overlapping phrases
        or identical URLs within the configured burst window.
        """
        clusters: List[CibCluster] = []
        if len(posts) < 2:
            return clusters

        # 1. URL-based synchronization detection
        url_map: Dict[str, List[SocialPost]] = {}
        for p in posts:
            for link in p.links:
                # Normalize link
                clean_link = link.split("?")[0].rstrip("/")
                if len(clean_link) > 10:
                    url_map.setdefault(clean_link, []).append(p)

        for url, shared_posts in url_map.items():
            distinct_authors = list({p.author for p in shared_posts})
            if len(distinct_authors) >= 2:
                # Check timing
                timestamps = [self.parse_timestamp(p.created_at) for p in shared_posts if self.parse_timestamp(p.created_at) > 0]
                if timestamps:
                    min_t = min(timestamps)
                    max_t = max(timestamps)
                    diff_s = max(max_t - min_t, 1.0)
                    if diff_s <= (self.burst_window_seconds * 3):
                        velocity = (len(shared_posts) / diff_s) * 60.0
                        start_iso = datetime.fromtimestamp(min_t, timezone.utc).isoformat()
                        end_iso = datetime.fromtimestamp(max_t, timezone.utc).isoformat()

                        clusters.append(CibCluster(
                            cluster_id=f"cib_url_{uuid.uuid4().hex[:8]}",
                            primary_topic=f"Synchronized Link Dissemination ({url[:30]}...)",
                            post_count=len(shared_posts),
                            account_count=len(distinct_authors),
                            accounts=distinct_authors,
                            start_time=start_iso,
                            end_time=end_iso,
                            duration_seconds=round(diff_s, 1),
                            synchronization_velocity=round(velocity, 2),
                            shared_urls=[url],
                            identical_phrases=[],
                            coordination_confidence=round(min(85.0 + (len(distinct_authors) * 3), 98.0), 1),
                            caveat_warning=CIB_CAVEAT_DISCLAIMER
                        ))

        # 2. Phrase shingle duplication burst detection
        for i in range(len(posts)):
            p1 = posts[i]
            matching_cluster = [p1]
            shared_phrases: Set[str] = set()

            for j in range(i + 1, len(posts)):
                p2 = posts[j]
                if p1.author == p2.author:
                    continue

                sim = self.compute_shingle_similarity(p1.text, p2.text, k=4)
                if sim >= 0.45:
                    matching_cluster.append(p2)
                    sa = self.extract_shingles(p1.text, 4)
                    sb = self.extract_shingles(p2.text, 4)
                    shared_phrases.update(list(sa & sb)[:3])

            distinct_authors = list({p.author for p in matching_cluster})
            if len(distinct_authors) >= 2:
                timestamps = [self.parse_timestamp(p.created_at) for p in matching_cluster if self.parse_timestamp(p.created_at) > 0]
                min_t = min(timestamps) if timestamps else 0.0
                max_t = max(timestamps) if timestamps else 0.0
                diff_s = max(max_t - min_t, 1.0)
                velocity = (len(matching_cluster) / diff_s) * 60.0

                start_iso = datetime.fromtimestamp(min_t, timezone.utc).isoformat() if min_t else datetime.now(timezone.utc).isoformat()
                end_iso = datetime.fromtimestamp(max_t, timezone.utc).isoformat() if max_t else datetime.now(timezone.utc).isoformat()

                # Prevent duplicate cluster additions
                if not any(set(distinct_authors).issubset(set(c.accounts)) for c in clusters):
                    topic = p1.text[:50].strip() + "..."
                    clusters.append(CibCluster(
                        cluster_id=f"cib_txt_{uuid.uuid4().hex[:8]}",
                        primary_topic=f"Copied Phrase Burst: '{topic}'",
                        post_count=len(matching_cluster),
                        account_count=len(distinct_authors),
                        accounts=distinct_authors,
                        start_time=start_iso,
                        end_time=end_iso,
                        duration_seconds=round(diff_s, 1),
                        synchronization_velocity=round(velocity, 2),
                        shared_urls=[],
                        identical_phrases=list(shared_phrases)[:5],
                        coordination_confidence=round(min(78.0 + (len(distinct_authors) * 4), 96.0), 1),
                        caveat_warning=CIB_CAVEAT_DISCLAIMER
                    ))

        return clusters

cib_engine = CIBEngine()
