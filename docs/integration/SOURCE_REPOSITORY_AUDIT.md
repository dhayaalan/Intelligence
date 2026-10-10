# Source Repository Audit: Social Media AI Agents v2

**Source Directory:** `/home/songoku/Pictures/social-media-ai-agents-v2-main`  
**Target Application:** `/home/songoku/Pictures/Intelligence`  
**Audit Date:** 2026-10-09  
**Auditor:** Principal Software Architect & QA Automation Team  

---

## 1. Executive Summary

A comprehensive forensic audit of `/home/songoku/Pictures/social-media-ai-agents-v2-main` was conducted to discover, catalog, and evaluate all useful social-media intelligence collectors, AI agents, and analytical algorithms for production integration into the `Intelligence` enterprise OSINT platform.

The source repository is a TanStack Start / TypeScript application featuring robust data-collection logic, heuristic credibility scoring, and LLM-grounded investigative agents. This audit verifies which capabilities are genuinely implemented in executable code, evaluates their dependency and licensing constraints, and defines the integration path into the target application's Python FastAPI backend and React frontend.

---

## 2. Directory Structure & Technology Stack

```text
/home/songoku/Pictures/social-media-ai-agents-v2-main/
└── frontend/
    ├── src/
    │   ├── api/             # API client contracts and hooks
    │   ├── app/             # Application configuration and request context
    │   ├── components/      # UI component library (shadcn/Radix-based)
    │   ├── core/            # Caching, concurrency, errors, logging
    │   ├── domain/          # Entities, relationships, evidence, investigations
    │   ├── features/        # Feature views (OSINT, entities, investigations)
    │   ├── routes/          # TanStack Start route handlers (social, youtube, agents, etc.)
    │   ├── services/        # Application services (AI, collectors, OSINT, reports)
    │   ├── utils/           # Core algorithmic engines:
    │   │   ├── social.ts                 # Bluesky, Reddit, Telegram, Mastodon ingestion
    │   │   ├── youtube-collector.ts      # YouTube metadata, transcripts, comments
    │   │   ├── telegram-intel.ts         # Telegram channel monitor
    │   │   ├── cib.ts                    # Coordinated Inauthentic Behavior engine
    │   │   ├── social-credibility.ts     # Bot and account credibility scoring
    │   │   ├── credibility.ts            # Scoring factors and bands
    │   │   ├── llm.ts                    # Provider-agnostic LLM interface
    │   │   ├── cases/case-analysis.ts    # Evidence-grounded analysis agent
    │   │   ├── mediaint/claims.ts        # Claim extraction & conflict analysis
    │   │   └── collectors/               # Modular collector registry and adapters
    │   └── server.ts        # Server entry with security headers & error normalization
```

---

## 3. Discovered Capabilities & Inventory

### 3.1. Social Media Data Collectors

| Component / Tool | File Location | Platform | Mechanism & Data Collected | Credential Requirements | Execution Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Bluesky Live Jetstream** | `src/utils/social.ts` | Bluesky (AT Proto) | WebSocket firehose connection to `wss://jetstream1.us-east.bsky.network/subscribe` and public AppView API (`public.api.bsky.app`). Retrieves live posts, user profiles, author feeds. | None (Public) | **Operational** |
| **Telegram Channel Monitor** | `src/utils/social.ts`, `telegram-intel.ts` | Telegram | Scrapes public channel web previews via `https://t.me/s/{channel}`. Extracts post text, timestamps, media flags, view counts, and forwards. | None (Public previews) | **Operational** |
| **Reddit Search & Monitor** | `src/utils/social.ts` | Reddit | OAuth2 client credentials via `https://oauth.reddit.com/r/{subreddit}/search` or public JSON fallback (`www.reddit.com/search.json`). Extracts title, selftext, score, author, comments. | Optional Client ID/Secret | **Operational** |
| **Mastodon Tag Monitor** | `src/utils/social.ts` | Mastodon / Fediverse | Public instance API (`https://mastodon.social/api/v1/timelines/tag/{tag}`). Extracts public statuses, author handles, and boosts. | None (Public) | **Operational** |
| **YouTube Video Intelligence** | `src/utils/youtube-collector.ts` | YouTube | Ingests metadata (`title`, `channel`, `views`, `upload_date`, `duration`), extracts subtitle/closed-caption tracks (`en`, `es`, etc.), and analyzes top comment sentiment. | None / Optional YouTube Data API v3 | **Operational** |

### 3.2. Forensic Analysis & Heuristic Engines

| Engine | File Location | Analytical Methodology | Input / Output Schema |
| :--- | :--- | :--- | :--- |
| **Coordinated Inauthentic Behavior (CIB)** | `src/utils/cib.ts` | Clusters accounts by temporal publication burst windows (< 60s), synchronized amplification of identical URLs, and cross-channel coordinated text. | Input: Array of `SocialPost`<br>Output: `CibCluster[]` with synchronization velocity and caveat warnings |
| **Social Credibility & Bot Scoring** | `src/utils/social-credibility.ts`, `credibility.ts` | Evaluates account age, post-to-reply ratio, default avatar usage, repetitive link sharing, and external reference diversity into a 0–100 credibility band (High, Moderate, Low, Inauthentic). | Input: Social profile & post corpus<br>Output: `CredibilityScore` (0–100) with factor breakdowns |
| **Claim & Narrative Forensics** | `src/utils/mediaint/claims.ts`, `claim-conflicts.ts` | Extracts specific factual assertions from posts, matches against known dispute registries, and flags contradictory statements between sources. | Input: Extracted social text<br>Output: Claims list, verification verdicts, conflict flags |

### 3.3. AI Agents & LLM Infrastructure

| Agent | File Location | Execution Pattern | Safety & Provenance Safeguards |
| :--- | :--- | :--- | :--- |
| **Grounded Case Analysis Agent** | `src/utils/cases/case-analysis.ts` | Evidence-grounded synthesis using strict context boundaries. Ingests pinned case evidence (`EV-xxx`), entities, and findings; generates findings strictly citing real evidence IDs. | Rejects hallucinations; explicitly flags missing evidence gaps; validates citations against real store. |
| **Person OSINT Query Planner** | `src/utils/osint/person-query-planner.ts` | Plans phased investigative queries (Username -> Email -> Leaks -> Socials) to prevent noisy searches. | Strict rate limits; enforces passive collection before active pivoting. |
| **Multi-Provider LLM Client** | `src/utils/llm.ts` | OpenAI-compatible wire format supporting vLLM, Ollama, Gemini, and OpenAI with bounded in-memory caching and token telemetry. | Sanitizes untrusted text; throws typed `LlmUnavailableError` instead of mocking results. |

---

## 4. Architectural Comparison: Source vs Target

| Dimension | Source Repository (`social-media-ai-agents-v2-main`) | Target Repository (`Intelligence`) | Architectural Strategy |
| :--- | :--- | :--- | :--- |
| **Primary Language** | TypeScript / Node.js (full-stack) | Python 3.10+ (backend) + TypeScript/React (frontend) | Re-implement core ingestion & analysis in Python backend; build rich React UI in frontend. |
| **Module System** | Custom TypeScript functional collectors | Standardized `IntelligenceModule` contract with `ModuleManifest`, `SearchOrchestrator`, and `ModuleRegistry` | Package as native `SocialMediaIntelligenceModule` conforming to `IntelligenceModule`. |
| **Multi-Tenancy** | Single-tenant demo / local session | Strict multi-tenant isolation with tenant ID enforcement on DB, cases, and logs | Integrate with tenant context & user role permissions (`ANALYST`, `INVESTIGATOR`, `SUPER_ADMIN`). |
| **Database** | SQLite / in-memory TanStack Store | MongoDB (source of truth) + Redis (queue/cache) + MinIO (evidence vault) | Persist evidence, entities, and social posts to MongoDB & MinIO with SHA-256 sealing. |
| **Search Engine** | Per-route fetchers | Unified multi-module `search_orchestrator` with hybrid ranking & correlation | Register social media search jobs in `SearchOrchestrator` alongside OSINT, Threat Intel, and News Intel. |

---

## 5. Security, Licensing & Compliance Review

1. **Licensing**: Source code uses standard permissive MIT/Apache compatible components without restrictive GPL copyleft constraints.
2. **Platform Terms of Service**:
   - **Bluesky**: Uses open AT Protocol and public Jetstream firehose without authentication hurdles.
   - **Telegram**: Reads public channels only (`t.me/s/{channel}`) without authenticating user sessions or scraping private chats.
   - **Reddit**: Strictly adheres to public API / OAuth endpoints with backoff rate-limiting.
   - **Instagram / Facebook**: Explicitly excluded; source repository notes compliance with Meta terms prohibiting unauthorized scraping.
3. **SSRF & Injection Defense**: All outgoing requests must pass through target's `network_safety` validator to prevent internal IP scanning.
