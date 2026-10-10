# Social Media AI Agents Integration Plan

**Target Architecture:** Sentinel Enterprise OSINT & Threat Intelligence Platform  
**Target Root:** `/home/songoku/Pictures/Intelligence`  
**Source Root:** `/home/songoku/Pictures/social-media-ai-agents-v2-main`  
**Execution Version:** 2.0.0-PROD  
**Date:** 2026-10-09  

---

## 1. Architectural Blueprint & Target Alignment

The integration follows the target application's established pluggable modular design:

```text
                               ┌─────────────────────────────┐
                               │     Unified Frontend UI     │
                               │   (Investigator Workspace)  │
                               └──────────────┬──────────────┘
                                              │ REST / WebSocket
                               ┌──────────────▼──────────────┐
                               │   FastAPI Gateway (v1)      │
                               │ /api/v1/social & /ai/agents │
                               └──────────────┬──────────────┘
                                              │
                   ┌──────────────────────────┼──────────────────────────┐
                   ▼                          ▼                          ▼
     ┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐
     │ Search Orchestrator      │ │ Social Media Module      │ │ AI Agents Framework      │
     │ - Intent classification  │ │ - Bluesky, Telegram      │ │ - Grounded Case Agent    │
     │ - Scope routing          │ │ - Reddit, Mastodon, YT   │ │ - Persona Pivot Agent    │
     │ - Correlation engine     │ │ - CIB & Bot Scorer       │ │ - Model Manager Failover │
     └─────────────┬────────────┘ └───────────┬──────────────┘ └───────────┬──────────────┘
                   │                          │                            │
                   └──────────────────────────┼────────────────────────────┘
                                              ▼
                               ┌─────────────────────────────┐
                               │  Persistence & Vault Core   │
                               │  - MongoDB (Truth)          │
                               │  - Redis (Queues/Cache)     │
                               │  - MinIO (Evidence SHA-256) │
                               └─────────────────────────────┘
```

---

## 2. Multi-Phase Implementation Plan

### Phase 1 — Audit & Capability Discovery (Completed)
* Forensic audit of `/home/songoku/Pictures/social-media-ai-agents-v2-main`.
* Delivery of `SOURCE_REPOSITORY_AUDIT.md` and `TOOL_CAPABILITY_MATRIX.md`.

### Phase 2 — Backend Social Media Intelligence Engine
1. **Module Manifest & Models (`backend/app/modules/social_media_intelligence/`)**:
   - `manifest.py`: Defines permissions, providers, and capabilities conforming to `ModuleManifest`.
   - `models.py`: Defines `SocialPost`, `CibCluster`, `CredibilityScore`, `SocialSearchRequest`, `SocialSearchResponse`, `YouTubeMetadata`, `YouTubeSubtitleTrack`.
2. **Platform Collectors (`backend/app/modules/social_media_intelligence/collectors/`)**:
   - `bluesky.py`: Public AppView client for actor feed & profile lookup.
   - `telegram.py`: Channel preview scraper for `https://t.me/s/{channel}`.
   - `reddit.py`: Multi-subreddit keyword & author search with error classification.
   - `mastodon.py`: Public Fediverse tag timeline extractor.
   - `youtube.py`: YouTube video metadata, transcript extraction, and comments collector.
3. **Forensic Heuristic Engines (`backend/app/modules/social_media_intelligence/engines/`)**:
   - `cib_engine.py`: Coordinated Inauthentic Behavior clustering by temporal bursts (< 60s) and URL propagation.
   - `credibility_engine.py`: Multi-factor bot scoring (0–100) with confidence breakdown.
4. **Service & Module Entry (`backend/app/modules/social_media_intelligence/`)**:
   - `service.py`: Service coordinator for social searches, analytics, and YouTube intelligence.
   - `module.py`: Implements `IntelligenceModule` contract with `search()`, `health_check()`, and normalized entities/evidence generation.

### Phase 3 — AI Agents Framework & Grounded Case Reasoning
1. **Grounded Case Analysis Agent (`backend/app/ai/agents/case_agent.py`)**:
   - Implements evidence-grounded Q&A over case evidence files.
   - Strictly enforces citation resolution against real evidence IDs (`EV-xxx`).
   - Rejects ungrounded statements and explicitly marks gaps.
2. **Social Persona Correlation Agent (`backend/app/ai/agents/social_agent.py`)**:
   - Aggregates identity signals across Bluesky, Telegram, Reddit, and Web.
   - Reconstructs persona activity timelines and detects handle reuse.
3. **Agent Router (`backend/app/api/v1/ai_agents.py`)**:
   - Exposes agent execution endpoints with authentication, tenant isolation, and audit logging.

### Phase 4 — Platform Core & Search Orchestration Integration
1. **Register Module**:
   - Register `social_media_intelligence_module` in `backend/app/main.py` and `conftest.py`.
2. **Search Orchestrator**:
   - Add `"SOCIAL MEDIA INTELLIGENCE"` scope and include module in `"ALL INTELLIGENCE"` in `backend/app/search/orchestrator.py`.
3. **API Routing**:
   - Register `/api/v1/social` and `/api/v1/agents` routes in `backend/app/api/v1/router.py`.

### Phase 5 — Investigator Frontend Workbenches
1. **API Client Hooks (`frontend/src/core/api/socialHooks.ts`, `agentHooks.ts`)**:
   - React Query hooks for social searches, CIB analysis, credibility scoring, YouTube extraction, and agent execution.
2. **Social Intelligence Workbench (`frontend/src/features/social_intelligence/SocialIntelligencePage.tsx`)**:
   - Tabbed platform search (Bluesky, Telegram, Reddit, Mastodon, YouTube).
   - Real-time CIB cluster analyzer with synchronization velocity graphs.
   - Credibility band badges (High, Moderate, Low, Inauthentic).
   - Video player with interactive timestamped transcript viewer.
   - Direct "Pin to Case / Evidence Vault" actions.
3. **AI Agents Workbench (`frontend/src/features/agents/AgentsPage.tsx`)**:
   - Case selector and agent capability picker.
   - Grounded Case Analysis chat with citation links.
   - Investigation gap analysis and executive summary generator.
4. **Navigation & Shell Integration**:
   - Add `Social Intelligence` and `AI Agents` to `InvestigatorShell.tsx` navigation items.

### Phase 6 — Production Verification & Automated Testing
1. **Backend Tests**:
   - Unit tests for collectors, CIB clustering, credibility scoring, and agent validation.
   - Integration tests verifying module registration, search orchestration, and tenant isolation.
2. **Frontend Build & Typechecks**:
   - Typechecking (`npm run typecheck`) and bundle build validation.
3. **Execution Validation**:
   - Test live execution with real and fixture targets.
