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

    def __init__(self, burst_window_seconds: float = 300.0):
        # Default window is 5 minutes (300 seconds) to capture delayed amplification waves
        self.burst_window_seconds = burst_window_seconds

    def canonicalize_url(self, url: str) -> str:
        """
        Normalizes URLs by stripping tracking queries (UTM, ref, fbclid, etc.) and standardizing
        trailing slashes, lowercase scheme, and hostnames.
        """
        if not url:
            return ""
        import urllib.parse
        parsed = urllib.parse.urlsplit(url.strip())
        query_params = urllib.parse.parse_qsl(parsed.query, keep_blank_values=False)
        tracking_prefixes = ("utm_", "fbclid", "igshid", "ref", "s", "t")
        filtered_query = [
            (k, v) for k, v in query_params
            if not any(k.lower().startswith(p) for p in tracking_prefixes)
        ]
        new_query = urllib.parse.urlencode(filtered_query)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        path = parsed.path.rstrip('/')
        canonical = f"{netloc}{path}"
        if new_query:
            canonical += f"?{new_query}"
        return canonical

    def normalize_text(self, text: str) -> str:
        clean = (text or "").lower()
        clean = re.sub(r'https?://\S+', ' ', clean)
        clean = re.sub(r'@[\w.:-]+', ' ', clean)
        clean = re.sub(r'[#$]', ' ', clean)
        clean = re.sub(r'[^\w\s]', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()

    def extract_character_ngrams(self, text: str, n: int = 3) -> Set[str]:
        """Extracts character n-grams for typo-tolerant lexical similarity."""
        norm = self.normalize_text(text)
        if len(norm) < n:
            return {norm} if norm else set()
        return {norm[i:i + n] for i in range(len(norm) - n + 1)}

    def extract_word_ngrams(self, text: str, n: int = 3) -> Set[str]:
        words = self.normalize_text(text).split()
        if not words:
            return set()
        if len(words) < n:
            return {" ".join(words)}
        return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}

    def extract_shingles(self, text: str, k: int = 5) -> Set[str]:
        return self.extract_word_ngrams(text, n=k)

    def compute_jaccard_similarity(self, set_a: Set[str], set_b: Set[str]) -> float:
        if not set_a or not set_b:
            return 0.0
        return len(set_a & set_b) / len(set_a | set_b)

    def compute_lexical_similarity(self, text_a: str, text_b: str) -> Tuple[float, List[str]]:
        """
        Computes composite lexical similarity using both token 3-grams and character 3-grams.
        Returns composite similarity float (0.0 to 1.0) and common phrase shingles.
        """
        words_a = self.extract_word_ngrams(text_a, 3)
        words_b = self.extract_word_ngrams(text_b, 3)
        word_jaccard = self.compute_jaccard_similarity(words_a, words_b)

        chars_a = self.extract_character_ngrams(text_a, 3)
        chars_b = self.extract_character_ngrams(text_b, 3)
        char_jaccard = self.compute_jaccard_similarity(chars_a, chars_b)

        composite = (word_jaccard * 0.65) + (char_jaccard * 0.35)
        shared_phrases = list(words_a & words_b)[:5]
        return composite, shared_phrases

    def compute_shingle_similarity(self, text_a: str, text_b: str, k: int = 5) -> float:
        sa = self.extract_shingles(text_a, k)
        sb = self.extract_shingles(text_b, k)
        return self.compute_jaccard_similarity(sa, sb)

    def parse_timestamp(self, ts_str: str) -> float:
        try:
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            return dt.timestamp()
        except Exception:
            return 0.0

    def detect_clusters(self, posts: List[SocialPost]) -> List[CibCluster]:
        """
        Groups posts into CIB clusters if distinct accounts publish highly overlapping phrases
        or canonicalized URLs within temporal distribution windows.
        """
        clusters: List[CibCluster] = []
        if len(posts) < 2:
            return clusters

        # 1. Canonical URL-based synchronization detection
        url_map: Dict[str, List[SocialPost]] = {}
        for p in posts:
            for link in p.links:
                clean_link = self.canonicalize_url(link)
                if len(clean_link) > 8:
                    url_map.setdefault(clean_link, []).append(p)

        for url, shared_posts in url_map.items():
            distinct_authors = list({p.author for p in shared_posts})
            if len(distinct_authors) >= 2:
                timestamps = [self.parse_timestamp(p.created_at) for p in shared_posts if self.parse_timestamp(p.created_at) > 0]
                if timestamps:
                    min_t = min(timestamps)
                    max_t = max(timestamps)
                    diff_s = max(max_t - min_t, 1.0)
                    if diff_s <= self.burst_window_seconds:
                        velocity = (len(shared_posts) / diff_s) * 60.0
                        start_iso = datetime.fromtimestamp(min_t, timezone.utc).isoformat()
                        end_iso = datetime.fromtimestamp(max_t, timezone.utc).isoformat()

                        clusters.append(CibCluster(
                            cluster_id=f"cib_url_{uuid.uuid4().hex[:8]}",
                            primary_topic=f"Synchronized Link Dissemination ({url[:35]}...)",
                            post_count=len(shared_posts),
                            account_count=len(distinct_authors),
                            accounts=distinct_authors,
                            start_time=start_iso,
                            end_time=end_iso,
                            duration_seconds=round(diff_s, 1),
                            synchronization_velocity=round(velocity, 2),
                            shared_urls=[url],
                            identical_phrases=[],
                            coordination_confidence=round(min(82.0 + (len(distinct_authors) * 3.5), 98.0), 1),
                            caveat_warning=CIB_CAVEAT_DISCLAIMER
                        ))

        # 2. Lexical n-gram similarity & temporal window clustering
        processed_pairs: Set[Tuple[int, int]] = set()
        for i in range(len(posts)):
            p1 = posts[i]
            matching_cluster = [p1]
            shared_phrases_set: Set[str] = set()

            for j in range(i + 1, len(posts)):
                p2 = posts[j]
                if p1.author == p2.author:
                    continue

                sim, shared = self.compute_lexical_similarity(p1.text, p2.text)
                if sim >= 0.40:
                    t1 = self.parse_timestamp(p1.created_at)
                    t2 = self.parse_timestamp(p2.created_at)
                    # Check temporal window (e.g. within burst_window_seconds or if timestamps are 0/unspecified)
                    if t1 > 0 and t2 > 0 and abs(t2 - t1) > self.burst_window_seconds:
                        continue

                    matching_cluster.append(p2)
                    shared_phrases_set.update(shared)
                    processed_pairs.add((i, j))

            distinct_authors = list({p.author for p in matching_cluster})
            if len(distinct_authors) >= 2:
                timestamps = [self.parse_timestamp(p.created_at) for p in matching_cluster if self.parse_timestamp(p.created_at) > 0]
                min_t = min(timestamps) if timestamps else 0.0
                max_t = max(timestamps) if timestamps else 0.0
                diff_s = max(max_t - min_t, 1.0)
                velocity = (len(matching_cluster) / diff_s) * 60.0

                start_iso = datetime.fromtimestamp(min_t, timezone.utc).isoformat() if min_t else datetime.now(timezone.utc).isoformat()
                end_iso = datetime.fromtimestamp(max_t, timezone.utc).isoformat() if max_t else datetime.now(timezone.utc).isoformat()

                # Prevent adding duplicate clusters with the same account subset
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
                        identical_phrases=list(shared_phrases_set)[:5],
                        coordination_confidence=round(min(78.0 + (len(distinct_authors) * 4.0), 96.0), 1),
                        caveat_warning=CIB_CAVEAT_DISCLAIMER
                    ))

        return clusters

cib_engine = CIBEngine()
