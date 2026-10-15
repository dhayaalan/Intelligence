# Collection Limits, Concurrency, and Data Retention Policy

## Overview
This document specifies the extraction limits, account controls, circuit breakers, and data retention rules implemented in `backend/app/core/config.py` and enforced across the OSINT, Social Media, and Threat Intelligence collection pipelines.

---

## 1. Configurable Policy Settings

The system enforces bounded execution to prevent uncontrolled crawling, platform bans, IP rate limiting, and runaway resource consumption.

| Setting | Default Value | Environment Variable | Enforcement Layer | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `MAX_PROFILES_PER_INVESTIGATION` | `100` | `MAX_PROFILES_PER_INVESTIGATION` | Investigation Engine | Bounded entity graph expansion per case |
| `MAX_POSTS_PER_PROFILE` | `50` | `MAX_POSTS_PER_PROFILE` | Social Media Intelligence | Upper threshold on historical timeline collection |
| `MAX_PAGINATION_DEPTH` | `5` | `MAX_PAGINATION_DEPTH` | Provider Collectors | Bounds cursor / page requests per endpoint |
| `MAX_COMMENTS_PER_CONTENT` | `20` | `MAX_COMMENTS_PER_CONTENT` | Social Media Intelligence | Limits engagement thread depth |
| `MAX_CONCURRENT_EXTRACTION_REQUESTS` | `10` | `MAX_CONCURRENT_EXTRACTION_REQUESTS` | Module SDK / Worker Pool | Protects network sockets & thread pool |
| `COLLECTION_TIMEOUT_SECONDS` | `45` | `COLLECTION_TIMEOUT_SECONDS` | Async HTTP Client | Hard deadline for external API response |
| `CIRCUIT_BREAKER_FAILURE_THRESHOLD` | `5` | `CIRCUIT_BREAKER_FAILURE_THRESHOLD` | Provider Adapter Base | Tripping threshold on consecutive upstream errors |
| `CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS` | `60` | `CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS` | Provider Adapter Base | Cooldown before half-open probe |
| `ENABLE_HISTORICAL_SNAPSHOTS` | `true` | `ENABLE_HISTORICAL_SNAPSHOTS` | Snapshot Service | Preserves versioned profile diffs |
| `SNAPSHOT_RETENTION_DAYS` | `90` | `SNAPSHOT_RETENTION_DAYS` | Database Cleaner / Retention Task | Deletion horizon for aged historical observations |
| `FAIL_CLOSED_REGIONAL_ROUTING` | `true` | `FAIL_CLOSED_REGIONAL_ROUTING` | Egress Controller | Strict abort if requested VPN tunnel is down |

---

## 2. Rate-Limiting & Backoff Strategy

- **Exponential Backoff with Jitter:** When an external provider responds with HTTP 429 (Too Many Requests), collectors sleep for `min(2^attempt + random(0, 1), 30)` seconds before retrying.
- **Retry-After Header Compliance:** If an HTTP 429 response includes a valid `Retry-After` header, the collector honors the specified delay up to a maximum threshold of 60 seconds; otherwise, the task yields and marks the result `RATE_LIMITED`.
- **Failure Isolation:** Under the modular architecture, one provider's failure or rate limiting never aborts other operational providers.

---

## 3. Snapshot Freshness & Retention

- **Snapshot Keying:** Profiles are keyed by `platform_id:username` in MongoDB `osint_profile_snapshots`.
- **Change Detection:** Field-level comparisons are executed across `bio`, `display_name`, `avatar_url`, `statistics`, and `website_urls`.
- **Retention Horizon:** Automated cleanup retains snapshots up to 90 days. Records older than `SNAPSHOT_RETENTION_DAYS` are purged to comply with data minimization and storage limits.
