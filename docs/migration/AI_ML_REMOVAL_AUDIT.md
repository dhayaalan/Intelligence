# AI/ML Codebase Audit & Removal Plan

## 1. Executive Summary

This audit document identifies all artificial intelligence (AI), machine learning (ML), large language model (LLM), and agent orchestration code currently present in the `Intelligence` repository (`/home/songoku/Pictures/Intelligence`).

The ML team is developing AI/ML capabilities independently as a separate service. The purpose of this migration is to decouple and remove the internal, application-owned AI/ML implementations while preserving 100% of the platform's core open-source intelligence (OSINT), threat intelligence, social-media collection, news wire aggregation, search orchestration, and case management capabilities.

---

## 2. Inventory of AI/ML Implementation Artifacts

The forensic scan identified the following components across backend, frontend, tests, and configuration:

### 2.1 Backend Implementation Code

| File Path | Description / Role | Classification | Removal / Retention Decision | Justification & Impact |
| :--- | :--- | :--- | :--- | :--- |
| `backend/app/ai/providers.py` | Multi-provider LLM abstraction (`OpenAIProvider`, `AnthropicProvider`, `OllamaProvider`, `GeminiProvider`, `AIModelManager`, `PromptInjectionDefense`). | **Exclusively AI/ML** | **DELETE** | Core application should not manage LLM API keys or provider connections directly. |
| `backend/app/ai/models.py` | Pydantic models for LLM provider types, prompt templates, and execution telemetry. | **Exclusively AI/ML** | **DELETE / REPLACE** | Replaced with a lightweight, implementation-free integration contract schema (`app/ml_contracts/`). |
| `backend/app/ai/service.py` | Centralized `AIService` orchestrating LLM prompt execution with deterministic rule fallback for case summaries. | **Mixed (AI + Deterministic)** | **SEPARATE & DELETE** | The LLM prompting code is deleted. The deterministic, rule-based summary builder is migrated into `app/investigations/summary_builder.py`. |
| `backend/app/ai/news_ml_synthesizer.py` | `NewsMLSynthesizer` invoking LLM completions via `ai_model_manager`, alongside deterministic news dossier compilation logic. | **Mixed (AI + Deterministic)** | **SEPARATE & DELETE** | The LLM execution logic is deleted. The deterministic dossier compiler (sections, timeline, claims schema) is relocated into `app/modules/news_intelligence/dossier_compiler.py`. |
| `backend/app/ai/agents/case_agent.py` | `GroundedCaseAnalysisAgent` performing LLM prompt synthesis and citation extraction. | **Exclusively AI/ML** | **DELETE** | Application-owned agent logic removed; will be replaced by external ML team API. |
| `backend/app/ai/agents/social_agent.py` | `SocialPersonaAgent` executing agent correlation over social collectors. | **Exclusively AI/ML** | **DELETE** | Collector functionality remains in `social_media_intelligence`; AI agent wrapper removed. |
| `backend/app/api/v1/ai_agents.py` | FastAPI route endpoints (`/api/v1/agents/grounded-analysis` and `/api/v1/agents/persona-correlation`). | **Exclusively AI/ML** | **REMOVE / CONTRACT STUB** | Removed from active routing. Replaced with documented ML Team Integration Contract endpoint returning `status: "not_configured"`. |

### 2.2 Frontend Implementation Code

| File Path | Description / Role | Classification | Removal / Retention Decision | Justification & Impact |
| :--- | :--- | :--- | :--- | :--- |
| `frontend/src/features/agents/AgentsPage.tsx` | AI Intelligence Agents Workbench containing Grounded Case Copilot and Persona Correlator UI. | **Exclusively AI/ML** | **REMOVE** | UI invokes deleted backend agent endpoints. Removed from active navigation to avoid broken/mock states. |
| `frontend/src/core/api/agentHooks.ts` | React Query hooks (`useGroundedCaseAnalysis`, `usePersonaCorrelation`). | **Exclusively AI/ML** | **DELETE** | Dangling API client code no longer needed. |
| `frontend/src/components/layout/InvestigatorShell.tsx` | Navigation entry (`{ id: 'agents', label: 'AI Agents' }`) and page mount. | **Shared Shell Component** | **UPDATE** | Remove `agents` navigation tab and router branch. Keep all other 11 navigation tabs. |

### 2.3 Tests & Fixtures

| File Path | Description / Role | Classification | Removal / Retention Decision | Justification & Impact |
| :--- | :--- | :--- | :--- | :--- |
| `backend/tests/test_ai_agents.py` | Unit and integration tests for `grounded_case_agent`, `social_persona_agent`, and agent API endpoints. | **Exclusively AI/ML** | **REPLACE** | Replaced with tests verifying the new clean ML integration boundary (`test_ml_integration_contract.py`). |

---

## 3. Verified Core Non-AI Functionality to PRESERVE

The following components were audited and confirmed to be **conventional, deterministic, or algorithmic tools** that must remain 100% intact:

1. **OSINT Module (`backend/app/modules/osint/`)**:
   - 335 registered reconnaissance tools (Shodan, SpiderFoot, theHarvester, Maltego, Google Dorking, Image EXIF).
   - `UsernameReconProvider`: Probing across 30+ public platform endpoints (Twitter/X, YouTube, Telegram, Reddit, Bluesky, Mastodon, etc.).
   - Pure HTTP requests, DNS queries, and regex extraction. **No AI/ML.**

2. **Social Media Intelligence Module (`backend/app/modules/social_media_intelligence/`)**:
   - Public AppView & Web Collectors: Bluesky, Telegram preview scraper, Reddit API, Mastodon ActivityPub, YouTube timed-text closed-caption extractor.
   - `CIBEngine`: Deterministic 5-gram shingle Jaccard similarity and 60-second burst window clustering. **No AI/ML.**
   - `CredibilityEngine`: Deterministic arithmetic scoring (post velocity, repetition rate, domain diversity, account age). **No AI/ML.**

3. **Threat Intelligence Module (`backend/app/modules/threat_intelligence/`)**:
   - DNS enumeration, WHOIS probers, CT-log lookups, OWASP ZAP spider/scanner, Wazuh CVE correlation. **No AI/ML.**

4. **News Intelligence Module (`backend/app/modules/news_intelligence/`)**:
   - Multi-provider search, RSS wire aggregation, publisher verification, story clustering. **No AI/ML.**

5. **Search Orchestrator & Classifier (`backend/app/search/`)**:
   - Target and intent classification via regex and keyword sets (`TargetClassifier`).
   - Cross-module asynchronous search orchestration (`SearchOrchestrator`).
   - Entity and relationship deduplication (`CorrelationEngine`). **No AI/ML.**

6. **Case & Investigation Management (`backend/app/investigations/`, `backend/app/cases/`)**:
   - Case CRUD, timeline events, evidence vault, finding association, report generation. **No AI/ML.**

7. **Database Collections & Multi-Tenancy**:
   - MongoDB repositories (`tenants`, `users`, `investigations`, `cases`, `entities`, `relationships`, `evidence`, `findings`, `reports`, `searches`, `audit`).
   - No collections will be dropped or modified.

---

## 4. Decoupling & Separation Strategy

For components containing both AI/ML logic and useful deterministic capabilities:

1. **News Article Compilation**:
   - Extract the `NewsArticle` compilation logic from `app/ai/news_ml_synthesizer.py` into a new file: `backend/app/modules/news_intelligence/dossier_compiler.py`.
   - The compiler will assemble verified article sections, source lineage nodes, timelines, and extracted claims deterministically from the parsed content without any LLM dependencies.
   - Update `search_engine.py` to import `dossier_compiler` instead of `news_ml_synthesizer`.

2. **Investigation Summary Generation**:
   - Extract the `_generate_deterministic_investigative_summary` logic from `app/ai/service.py` into `backend/app/investigations/summary_builder.py`.
   - Update `app/investigations/service.py` to import `summary_builder` instead of `app.ai.service`.

3. **External ML Team Integration Boundary**:
   - Create a clean, typed interface under `backend/app/ml_contracts/`:
     - Defines input/output schemas for future ML capabilities.
     - Provides an optional integration router that returns `503 / {"status": "not_configured"}` if an external ML endpoint is not set up.
     - Completely decoupled from internal model files, weights, or provider SDKs.

---

## 5. Execution Steps

1. Create `backend/app/modules/news_intelligence/dossier_compiler.py` and update `search_engine.py`.
2. Create `backend/app/investigations/summary_builder.py` and update `investigations/service.py`.
3. Create `backend/app/ml_contracts/` containing the clean external ML service contract.
4. Remove `backend/app/ai/` directory completely.
5. Update `backend/app/api/v1/router.py` to disconnect `ai_agents` router or replace with the decoupled ML contract router.
6. Remove `backend/tests/test_ai_agents.py` and create `backend/tests/test_ml_contract.py`.
7. Clean up frontend: remove `AgentsPage.tsx`, `agentHooks.ts`, and update `InvestigatorShell.tsx`.
8. Run full test suite (`pytest`) and frontend build (`npm run build`).
9. Generate `docs/migration/ML_TEAM_INTEGRATION_CONTRACT.md` and `docs/migration/AI_ML_REMOVAL_RESULTS.md`.
