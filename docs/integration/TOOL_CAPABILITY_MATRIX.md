# Tool & Capability Comparison Matrix

**Target:** `/home/songoku/Pictures/Intelligence`  
**Source:** `/home/songoku/Pictures/social-media-ai-agents-v2-main`  
**Last Updated:** 2026-10-09  

---

## 1. Classification Definitions

* **Class 1 (Implemented & Working):** Target application already contains a fully functional, tested implementation.
* **Class 2 (Incomplete / Broken):** Target has a stub, mock, or partial implementation needing enhancement.
* **Class 3 (Missing & Approved for Integration):** Genuinely missing from target, provides high intelligence value, and is technically compatible.
* **Class 4 (Duplicate):** Equivalent capability already exists under a different name in the target.
* **Class 5 (Incompatible / Obsolete):** Uses deprecated APIs, obsolete protocols, or conflicting runtime patterns.
* **Class 6 (Blocked / Prohibited):** Violates platform Terms of Service, requires invasive scraping, or exposes security risks.

---

## 2. Comparative Matrix

| Capability / Tool | Source Implementation | Target Status | Classification | Integration Recommendation |
| :--- | :--- | :--- | :---: | :--- |
| **Bluesky Live Jetstream Firehose** | `src/utils/social.ts` (WebSocket to Jetstream) | None | **Class 3** | **Integrate**: Create `BlueskyCollector` in Python backend and WebSocket bridge in frontend for real-time post discovery. |
| **Bluesky Author Feed & Profile Lookup** | `src/utils/social.ts` (public AT-Proto API) | None | **Class 3** | **Integrate**: Implement REST client for `public.api.bsky.app` in `SocialMediaIntelligenceModule`. |
| **Telegram Public Channel Monitor** | `src/utils/social.ts`, `telegram-intel.ts` | None | **Class 3** | **Integrate**: Implement asynchronous parser for `t.me/s/{channel}` public dispatches, extracting text, timestamps, views, forwards, and media. |
| **Reddit Search & Thread Collector** | `src/utils/social.ts` | Partial (Catalog entry only) | **Class 2** | **Upgrade & Integrate**: Port OAuth2 and JSON search collector into backend with automatic rate limiting and subreddit scoping. |
| **Mastodon / Fediverse Monitor** | `src/utils/social.ts` | None | **Class 3** | **Integrate**: Port public tag & user timeline search via standard ActivityPub / Mastodon API. |
| **YouTube Video Intelligence** | `src/utils/youtube-collector.ts` | News search has YouTube wire stubs only | **Class 2** | **Upgrade & Integrate**: Add full YouTube video intelligence (metadata extraction, subtitles/captions parsing, and comment sentiment analysis). |
| **Coordinated Inauthentic Behavior (CIB) Detector** | `src/utils/cib.ts` | None | **Class 3** | **Integrate**: Port burst window clustering (< 60s), synchronized URL amplification detection, and velocity analysis to Python backend service. |
| **Social Credibility & Bot Scorer** | `src/utils/social-credibility.ts`, `credibility.ts` | None | **Class 3** | **Integrate**: Implement multi-factor account credibility scoring (account age, post ratio, avatar, link patterns) into Social Intelligence engine. |
| **Grounded Case Analysis AI Agent** | `src/utils/cases/case-analysis.ts` | Generic heuristic summary exists in `AIService` | **Class 2** | **Upgrade & Integrate**: Build dedicated `GroundedCaseAnalysisAgent` that reasons over case evidence records and resolves citations strictly to `EV-xxx`. |
| **Social Media Identity Correlation Agent** | `src/utils/osint/person-query-planner.ts` | Basic username recon | **Class 2** | **Upgrade & Integrate**: Build multi-platform pivot agent correlating usernames across Bluesky, Telegram, Reddit, and GitHub. |
| **Misinformation & Claim Contradiction Engine** | `src/utils/mediaint/claims.ts` | Exists in `news_ml_synthesizer.py` | **Class 1 / 4** | **Preserve Target**: Target's `news_ml_synthesizer` is already a 1000-line DisInfoLab engine. Extend it to accept social post inputs. |
| **Instagram / Facebook Scraper** | Excluded in source | None | **Class 6** | **Do Not Integrate**: Prohibited by platform Terms of Service; requires private account credentials. Retain as manual capture only. |
| **WHOIS & DNS Enumerator** | `src/utils/collectors/existing/dns.ts` | Exists in `threat_intelligence` | **Class 1** | **Preserve Target**: Target already implements `dns_intel.py` and `host_discovery.py`. |
| **Shodan Host Intelligence** | `src/utils/collectors/existing/shodan-internetdb.ts` | Exists in `osint` & `threat_intelligence` | **Class 1** | **Preserve Target**: Target already implements `shodan.py` and `scanner_adapter.py`. |
| **theHarvester Email Search** | `src/utils/collectors/external/theharvester.ts` | Exists in `osint/providers/theharvester.py` | **Class 1** | **Preserve Target**: Already implemented in target. |

---

## 3. Approved Integration Backlog

1. **Backend Social Media Intelligence Module** (`app.modules.social_media_intelligence`):
   - Manifest: `social_media_intelligence`
   - Collectors: `BlueskyCollector`, `TelegramCollector`, `RedditCollector`, `MastodonCollector`, `YouTubeCollector`.
   - Heuristics: `CIBEngine`, `SocialCredibilityEngine`.
   - Module SDK Contract: Conforms to `IntelligenceModule` with `search()`, `health_check()`, `initialize()`.
2. **Search Orchestration Extension**:
   - Register `social_media_intelligence` in `search_orchestrator.py` under applicable scopes (`"SOCIAL MEDIA INTELLIGENCE"`, `"ALL INTELLIGENCE"`, `"PEOPLE & IDENTITIES"`, `"MEDIA"`).
3. **AI Agents Architecture**:
   - `GroundedCaseAnalysisAgent` in `backend/app/ai/agents/case_agent.py` ensuring grounded evidence citations.
   - `SocialPersonaAgent` in `backend/app/ai/agents/social_agent.py` for cross-platform persona timeline aggregation.
4. **API Endpoints**:
   - `POST /api/v1/social/search`: Multi-platform social query search.
   - `POST /api/v1/social/analyze/cib`: Coordinated Inauthentic Behavior clustering.
   - `POST /api/v1/social/analyze/credibility`: Account credibility and bot scoring.
   - `POST /api/v1/social/youtube/video`: Full YouTube metadata and transcript extraction.
   - `POST /api/v1/ai/agents/grounded-analysis`: Case-grounded evidence interrogation.
5. **Frontend Workbenches**:
   - `SocialIntelligencePage`: Interactive multi-platform feed, CIB cluster inspector, bot score badges, and YouTube transcript viewer.
   - `AgentsPage`: Interactive AI Agent workbench for investigators to query case files with verifiable evidence citations.
