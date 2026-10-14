# Social Media Intelligence Resilient Crawler Engine Design

**Subsystem:** `backend/app/modules/social_media_intelligence/resilient_crawler.py`  
**Architecture Lead:** Principal Social Media Collection & Systems Reliability Engineer  
**Status:** Approved for Implementation  

---

## 1. Design Overview

The Resilient Crawler Engine provides a robust, centralized collection pipeline for all social media platforms (Bluesky, Reddit, Telegram, Mastodon, YouTube).

### Key Architectural Pillars
1. **Adaptive Rate-Limiting & 429 Handling:** Respects platform quotas, parses standard `Retry-After` headers, and applies Decorrelated Jitter Exponential Backoff.
2. **Circuit Breaking & Failure Isolation:** Prevents cascading timeouts and isolates failing providers from degrading other integrations.
3. **Cursor Checkpointing & Resumability:** Tracks pagination tokens (`cursor`, `after`, `max_id`) in an in-memory/MongoDB checkpoint store.
4. **Zero Falsification:** Replaces all synthetic fallback generation with honest provider status classification.
5. **Deduplication:** Stable post ID hashing prevents duplicate storage across incremental collection runs.

```
┌────────────────────────────────────────────────────────────────────────┐
│                    ResilientCrawlerEngine                              │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Platform Rate Limiter (Token Bucket per platform)                   │
│ 2. Circuit Breaker (CLOSED -> OPEN -> HALF-OPEN)                       │
│ 3. Checkpoint Store (job_id + platform -> continuation token)          │
│ 4. Adaptive HTTP Client (Automatic 429 retry with jitter backoff)      │
│ 5. Result Normalizer (Standard SocialPost & CollectorTelemetry)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Status Classification Taxonomy

Every collection attempt returns a structured `CollectorResult`:

```python
class CollectorStatus(str, Enum):
    SUCCESS = "SUCCESS"                      # Records collected normally
    SUCCESS_EMPTY = "SUCCESS_EMPTY"          # Provider succeeded; query has 0 matches
    RATE_LIMITED = "RATE_LIMITED"            # HTTP 429 or quota exceeded
    ACCESS_DENIED = "ACCESS_DENIED"          # HTTP 401/403 (unauthorized or IP block)
    PLATFORM_UNAVAILABLE = "UNAVAILABLE"     # HTTP 5xx or connection refused
    TIMEOUT = "TIMEOUT"                      # Request exceeded deadline
    CONFIG_REQUIRED = "CONFIG_REQUIRED"      # API key / credentials required
```

```python
class CollectorResult(BaseModel):
    platform: SocialPlatformType
    status: CollectorStatus
    items_collected: int
    items: List[SocialPost] = Field(default_factory=list)
    next_cursor: Optional[str] = None
    retry_after_seconds: Optional[float] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
```

---

## 3. Adaptive Rate Limiting & Backoff Specification

### Decorrelated Jitter Algorithm
When a provider returns HTTP 429:
1. If the response contains a `Retry-After` header (seconds or RFC 2822 date), that exact interval is respected (capped at `MAX_RETRY_AFTER_SECS = 60s`).
2. If no `Retry-After` header is present, the backoff interval is calculated using full-jitter exponential backoff:
   $$t_{\text{sleep}} = \min(t_{\text{max}}, t_{\text{base}} \times 2^{\text{attempt}}) \times \text{uniform}(0.5, 1.5)$$
   - $t_{\text{base}} = 1.0\text{s}$
   - $t_{\text{max}} = 30.0\text{s}$
   - Maximum retries: 3 attempts.

---

## 4. Checkpointing & Resumable Collection State

### Checkpoint Data Schema
```python
class CrawlCheckpoint(BaseModel):
    job_id: str
    platform: str
    query: str
    cursor: Optional[str] = None
    total_items_collected: int = 0
    updated_at: str
    status: str
```

### Resumption Flow
1. Client requests collection with `(query, job_id)`.
2. Engine checks if an active `CrawlCheckpoint` exists for `job_id`.
3. If cursor is found, collection resumes directly from `next_cursor` without requesting previously seen pages.
4. Deduplication hash ring verifies no duplicate post IDs are appended to the dataset.
