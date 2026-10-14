# Social Media Intelligence Crawler Audit

**Subsystem:** `backend/app/modules/social_media_intelligence/`  
**Date:** October 2026  
**Auditor:** Senior Social Media Collection & Systems Reliability Engineer  

---

## 1. Inventory of Platforms & Collection Methods

| Platform | Current Collection Method | Endpoint Used | Auth Requirements | Current Rate Limit Handling | Checkpoint Support | Audit Finding / Defect |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bluesky** | Public XRPC Directory | `https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts` | None (Unauthenticated public directory) | None; immediate failure fallback | None (cursor returned but ignored) | **CRITICAL**: Falls back to `_generate_fallback_posts` (`@intel_wire.bsky.social`) with fake 90.0 credibility score. |
| **Telegram** | Public Web Preview Scraping | `https://t.me/s/{channel}` | None (Public web view) | None; catches all exceptions | None (channel scrape only) | **CRITICAL**: Generates fake posts on scrape error. Fragile HTML parsing prone to Telegram anti-scraping blocks. |
| **Reddit** | Public JSON Feed | `https://www.reddit.com/search.json` & `/r/{sub}/search.json` | Requires custom User-Agent; OAuth for volume | None; catches 403 / 429 and immediately triggers fallback | None (`after` token dropped) | **CRITICAL**: Reddit frequently blocks unauthenticated scripts (HTTP 403/429); collector generates fake post instead of reporting 403. |
| **Mastodon** | Public Instance REST API | `https://mastodon.social/api/v2/search` | None (Public read) | None; catches all exceptions | None (`max_id` pagination dropped) | **CRITICAL**: Generates fake posts on timeout or rate limit. |
| **YouTube** | oEmbed + Public Scrape + Subtitles | `https://www.youtube.com/oembed`, HTML meta tags | None (Public oEmbed/HTML) | None | None | **CRITICAL**: Injects fake metrics (`views = 125000`, `likes = 4200`), mock comments by `"Analyst_Observer"`, and synthetic claims. |

---

## 2. In-Depth Operational Defect Analysis

### A. Fallback Post Falsification
Every collector in `backend/app/modules/social_media_intelligence/collectors/` contains a method `_generate_fallback_posts()`:
- **Bluesky:**
  ```python
  except Exception as e:
      app_logger.warning(f"Error fetching posts from Bluesky: {e}")
      posts.extend(self._generate_fallback_posts(clean_query, limit))
  ```
  Returns a synthetic post authored by `@intel_wire.bsky.social` with text claiming breaking tactical monitoring, 45 likes, 12 reposts, and a `credibility_score = 90.0`.
- **Telegram:**
  Generates fake post authored by `@tele_intel_dispatch` with 1,200 views.
- **Reddit:**
  Generates fake post authored by `u/netsec_analyst` with 84 upvotes.
- **Mastodon:**
  Generates fake post authored by `@disinfo_tracker@mastodon.social`.
- **YouTube:**
  Generates mock comments:
  ```python
  YouTubeComment(
      id=f"yt_c_{vid}_1",
      author="Analyst_Observer",
      text="The timeline indicators presented at 0:10 corroborate independent research.",
      likes=18
  )
  ```

**Operational Impact:** In sensitive defence or intelligence investigations, analyst decisions could be based on completely hallucinated social posts, fake usernames, fabricated view metrics, and artificial credibility ratings.

---

### B. Lack of Adaptive Rate Limiting & 429 Throttling
1. **HTTP 429 Unhandled:** No collector inspects response headers for `Retry-After`, `x-ratelimit-remaining`, or `x-ratelimit-reset`.
2. **Missing Token Bucket / Leaky Bucket:** Requests are fired synchronously or concurrently without inter-request delays or platform-specific concurrency limits.
3. **No Exponential Backoff with Jitter:** When throttled, collectors immediately fail rather than executing bounded retries with jitter:
   $$t_{\text{sleep}} = 2^k + \text{random\_uniform}(0, 1)$$

---

### C. Missing Checkpointing & Resumability
- Providers returning paginated results (e.g., Bluesky XRPC `cursor`, Reddit `after`, Mastodon `max_id`) have their cursors discarded after each batch.
- If a collection job is cancelled, times out, or gets throttled mid-way, the investigator has no mechanism to resume from the last known cursor, forcing a full refetch that consumes duplicate quota and increases IP ban risk.

---

### D. Conflation of Distinct Provider Error Modes
When collection fails, the system provides zero diagnostic granularity to the investigator. The following distinct failure modes are conflated:
1. `RATE_LIMITED` (HTTP 429 / Quota reached)
2. `AUTH_REQUIRED` / `ACCESS_DENIED` (HTTP 401 / 403)
3. `EMPTY_RESULTS` (Valid search, zero matches)
4. `PLATFORM_BLOCKED` (Anti-bot captcha / IP blacklisting)
5. `NETWORK_ERROR` (DNS failure / timeout)
6. `SERVICE_UNAVAILABLE` (HTTP 502 / 503 / 504)

---

## 3. Crawler Audit Matrix & Action Requirements

| Subsystem Requirement | Current State | Required Target State |
| :--- | :--- | :--- |
| **Fake Fallback Posts** | Active in 5 of 5 collectors | **Zero Tolerance**: Completely excise all fallback post synthesis. |
| **HTTP 429 Detection** | None | Detect 429, parse `Retry-After`, pause crawler queue. |
| **Backoff Algorithm** | Immediate exit | Full-jitter exponential backoff (max 3 retries). |
| **Pagination Checkpoint**| None | Persist cursor state per (job_id, platform) to resume seamlessly. |
| **Deduplication** | None in collectors | Stable item ID hashing to discard previously seen posts. |
| **Provider Diagnostics**| None | Return structured `CollectorResult` with status, error code, and metrics. |
