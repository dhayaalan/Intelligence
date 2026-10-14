# Social Media Crawler Test Strategy & Validation Plan

**Subsystem:** `backend/app/modules/social_media_intelligence/`  
**Test Suite:** Unit, Integration, Rate-Limiting, and Circuit-Breaker Test Specifications  
**Status:** Verification Baseline  

---

## 1. Test Strategy Overview

The testing strategy validates that:
1. All social media collectors return authentic data only, with **zero fallback posts**.
2. HTTP 429 status codes trigger adaptive backoff, honoring `Retry-After` headers.
3. Pagination continuation tokens (`cursor`, `after`, `max_id`) are properly captured and can resume interrupted collections.
4. Circuit breakers transition between `CLOSED`, `OPEN`, and `HALF-OPEN` without cascading failures.
5. Errors (403 Forbidden, 401 Unauthorized, 503 Unavailable) produce explicit diagnostic statuses instead of empty or fake responses.

---

## 2. Test Cases Specification

### Case 1: Zero Fallback Verification on Provider Error
- **Goal:** Verify that when Bluesky, Telegram, Reddit, Mastodon, or YouTube fail (e.g., simulating HTTP 403 or network failure), the collector returns `0` posts and a structured error status, NOT synthetic posts.
- **Assertion:** `len(result.items) == 0` and `result.status in [CollectorStatus.ACCESS_DENIED, CollectorStatus.PLATFORM_UNAVAILABLE]`.
- **Integrity Rule:** No fake `@intel_wire.bsky.social` or `@tele_intel_dispatch` entities.

### Case 2: Adaptive HTTP 429 & Retry-After Handling
- **Goal:** Mock HTTP 429 response with header `Retry-After: 3`.
- **Execution:** Engine parses `3` seconds, waits, and performs a single jittered retry.
- **Assertion:** Request retried after delay; if still 429, marks status as `RATE_LIMITED` and records `retry_after_seconds = 3`.

### Case 3: Checkpoint Persistence and Resume
- **Goal:** Simulate multi-page collection where page 1 returns 5 posts and `next_cursor = "cur_page_2"`.
- **Execution:** First call collects page 1 and saves checkpoint. Second call with `resume_job_id` starts directly at `cur_page_2`.
- **Assertion:** No duplicate post IDs; seamless progression across pages.

### Case 4: YouTube Telemetry Authenticity
- **Goal:** Verify that YouTube video lookup retrieves authentic oEmbed data; when metadata cannot be scraped, it does NOT inject hardcoded `views = 125000` or mock comments.
- **Assertion:** Only authentic fields returned; missing metrics remain `None`.
