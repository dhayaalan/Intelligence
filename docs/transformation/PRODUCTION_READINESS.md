# Production Readiness and Operational Architecture

**Target Repository**: `/home/songoku/Pictures/Intelligence`  
**Standard**: High-Assurance Evidence-Driven Investigative Architecture  
**Document Status**: Production Baseline  

---

## 1. Secrets and Configuration Management

### 1.1 Strict Credential Enforcement
To ensure evidence authenticity and operational honesty, the platform enforces strict credential policies. No tool or crawler falls back to mocked or synthetic data when credentials are absent or expired.

| Provider / Integration | Environment Variable | Required For | Failure Behavior When Unconfigured |
| :--- | :--- | :--- | :--- |
| **X / Twitter** | `TWITTER_BEARER_TOKEN` | Twitter Intelligence OSINT Probing | Returns `CONFIG_REQUIRED` with official API portal instructions. |
| **Reddit** | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` | Subreddit & User Profiling | Falls back to public JSON endpoints (`.json`) with strict rate limiting; returns `RATE_LIMITED` / `AUTH_FAILED` if blocked. |
| **Bluesky** | `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` | ATProto Authenticated Feed Access | Uses public unauthenticated AppView endpoints (`public.api.bsky.app`); throttles gracefully under 429. |
| **YouTube** | `YOUTUBE_API_KEY` | Official v3 Data API | Uses public search metadata without video synthesis; returns `CONFIG_REQUIRED` or authentic search matches only. |
| **Telegram** | `TELEGRAM_BOT_TOKEN` | Official Bot API Telemetry | Inquires public channel previews via safe web preview; unverified channels return `NOT_FOUND` / `UNAVAILABLE`. |
| **Mastodon** | `MASTODON_ACCESS_TOKEN` | Instance-specific API reads | Queries public instance endpoints; honors `Retry-After` headers. |

### 1.2 Environment File Security
- `.env` must never be committed to source control.
- Production deployments must inject secrets via Kubernetes Secrets, HashiCorp Vault, or AWS Secrets Manager.
- All secrets are excluded from debug logging and diagnostic error serializations.

---

## 2. Database Indexes, Migrations, and Tenancy Isolation

### 2.1 Multi-Tenant Isolation
- Every investigation, evidence item, and relationship is strictly scoped by `tenant_id` and `case_id`.
- Foreign key cascading is restricted (`ON DELETE RESTRICT` or soft-delete) to prevent accidental loss of historical investigative records.
- Database access patterns require tenant context injection in all SQLAlchemy / SQL query filters.

### 2.2 Indexing Strategy
To support sub-second graph traversal and timeline navigation across millions of records:
- `idx_investigations_tenant_status`: `(tenant_id, status, created_at DESC)`
- `idx_evidence_case_source`: `(case_id, source_type, collected_at DESC)`
- `idx_relationships_nodes`: `(source_node_id, target_node_id)`
- `idx_social_crawler_checkpoints`: `(job_id, platform, updated_at DESC)`

---

## 3. Background Job Infrastructure and Crawler Execution

### 3.1 Adaptive Rate-Limiting & Throttling
All social media and news collectors utilize the unified `ResilientCrawlerEngine`:
- **HTTP 429 Handling**: Automatically parses `Retry-After` (in seconds or RFC 2822 HTTP date).
- **Exponential Backoff with Full Jitter**: Prevents "thundering herd" retry storms (`delay = random(0.5, min(max_backoff, base * 2^attempt))`).
- **Circuit Breaking**: Opens circuit after 5 consecutive provider failures; stops outbound requests to failing hosts for 60 seconds before probing in `HALF_OPEN` state.
- **Deduplication**: Content hashes and native platform IDs prevent redundant database writes.

### 3.2 Checkpointing and Resumability
- Long-running collection jobs persist pagination cursors (`cursor_token`) to disk or database every $N$ items.
- Interrupted or throttled jobs can resume from their exact continuation token without duplicate processing.

---

## 4. Health Probes and Lifecycle Management

### 4.1 Health Check Endpoints
- **Liveness Probe**: `GET /api/v1/health`  
  Returns 200 if the FastAPI application event loop is responsive.
- **Readiness Probe**: `GET /api/v1/health/ready`  
  Validates database connectivity, module registry status, and crawler circuit states.
- **Provider Status Probe**: `GET /api/v1/social/status` & `GET /api/v1/news/providers`  
  Returns honest real-time availability of external data pipelines without invoking costly scraping cycles.

### 4.2 Graceful Shutdown
- `app.on_event("shutdown")` ensures all active HTTPX async client connection pools are closed cleanly.
- Ongoing collection checkpoints are flushed to persistent storage before process termination.

---

## 5. Security Enforcement and SSRF Defenses

### 5.1 Network Safety Layer
- All URL fetching (e.g., news article lead image extraction, web scrapers, link preview generators) passes through `NetworkSafety.validate_url()`.
- **Blocked IP Ranges**:
  - Loopback (`127.0.0.0/8`, `::1`)
  - Private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
  - Link-local and cloud metadata (`169.254.169.254`, `fe80::/10`)
  - Broadcast and multicast ranges
- URL redirects are strictly validated against the same policy before following.

### 5.2 Safe Subprocess Invocation
- Any legacy system command execution (such as `whois` or `traceroute`) must pass through strictly whitelisted argument parsers with zero shell interpolation (`shell=False`).
- Bounded execution timeouts (default 10s) prevent hung child processes.

---

## 6. AI/ML Ownership Boundary

### 6.1 Strict Contract Adherence
- The Intelligence Platform maintains a pure deterministic data plane.
- Zero local LLM dependencies (LangChain, Llama, OpenAI direct bindings, or synthetic claim generators) exist in the core codebase.
- Communication with the ML service is strictly via HTTP REST contracts defined in `app/ml_contracts/`.
- When the ML service is unconfigured or unreachable, the platform returns honest `NOT_CONFIGURED` or `UNAVAILABLE` status, accompanied by deterministic rule-based dossiers and raw evidence logs.

---

## 7. Rollback and Disaster Recovery Procedures

1. **Database Snapshot**: Prior to running migrations, take a full transactional dump (`pg_dump` or SQLite copy).
2. **Code Rollback**: Deployment images are tagged with Git commit SHAs. In case of regression, roll back deployment pod to previous known good image.
3. **Evidence Integrity**: Evidence tables use immutable write-once audit logs; recovery never requires recalculating historical confidence scores.
