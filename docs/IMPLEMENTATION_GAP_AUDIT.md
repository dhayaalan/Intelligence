# IMPLEMENTATION GAP AUDIT: CLUE-TO-CLUE INVESTIGATION WORKFLOW

**Repository:** `/home/songoku/Pictures/Intelligence`  
**Date:** October 17, 2026  
**Auditor:** Antigravity Autonomous Engineering Pair  
**Branch:** `feat/clue-to-clue-investigation-remediation`

---

## EXECUTIVE SUMMARY

A rigorous code-level and test-driven audit was performed across the investigation orchestration engine, identifier normalization, OSINT pivot engine, vehicle intelligence, social media intelligence, geospatial intelligence, Neo4j graph service, and MongoDB repositories.

While foundational models and modules exist, **10 critical implementation gaps** were identified that break the clue-to-clue investigative pipeline:
1. Exact identifier queries manufactured synthetic root entities that bypassed verification and synthesized fake telecom claims for non-existent entities.
2. Hardcoded phone region assumptions (`"US"`) and silent ambiguity resolution without tenant locale or user region input.
3. Module selection in the search orchestrator restricted identifier searches to `{"osint"}` and dropped follow-up pivots to social media, news, threat intel, and geo intelligence.
4. Search relationships were never persisted into MongoDB `relationship_repo` or Neo4j, breaking 1-hop graph expansion for freshly searched queries.
5. Neo4j relationship sanitization whitelist dropped legitimate domain, transport, and identity relationships to generic `"RELATED"`.
6. Vehicle intelligence created high-confidence (0.99) and factual `REGISTERED_TO` relationships based purely on regex prefix syntax without querying registration databases.
7. Geo Intelligence module created unsupported personal `LOCATED_AT` relationships to searched persons from unassociated geographic mentions via `obs.associated_entity_value or context.query`.
8. YouTube collector returned empty lists for general keyword searches, lacking YouTube Data API and authentic public video search.
9. Motor MongoDB repositories lacked resilience against closed event loops in asynchronous multi-test suites.
10. Frontend components defaulted missing entity confidence values to "85% Verified" instead of displaying "Unknown / Unrated".

---

## CODE-LEVEL DEFECT MATRIX

| # | Component | Defect | Root Cause | Reproducing Test / Condition | Expected Fix |
|---|---|---|---|---|---|
| 1 | `backend/app/search/orchestrator.py` & `osint/module.py` | Non-existent emails/phones return 1 entity and fake telecom registry evidence | `osint/module.py` unconditionally injects a synthetic `KEYWORD` entity from `context.query` with `sources=["search_query"]`. `verify_identifier_match` matched the string equality, causing `verified_entities` to treat the synthetic query as a verified record. | `test_api_nonexistent_email_returns_zero_matches`, `test_api_nonexistent_phone_returns_zero_matches` in `backend/tests/test_identifier_search_accuracy.py` | Exclude `search_query` from verifying sources; ensure non-existent identifiers return zero matches and zero synthesized evidence. |
| 2 | `backend/app/search/normalization.py` | Hardcoded `"US"` phone default region and silent country plan guessing | `orchestrator.py` passed `default_phone_region="US"`. Numbers without `+` silently guessed across `["IN", "GB", "US", "CA", "AU"]` without tenant configuration or ambiguity detection. | Unprefixed international 10-digit numbers tested without tenant region configuration. | Add tenant/system default phone region configuration and detect ambiguous dial plans. |
| 3 | `backend/app/search/orchestrator.py` & `osint/pivot_engine.py` | Discovery pivots cannot reach Social, Threat Intel, or News; provenance chain broken | Line 96 hardcoded `target_modules_set = {"osint"}` for identifiers. Line 701 filtered pivots against `effective_module_ids` (which only had `osint`). Line 86 in `pivot_engine.py` hardcoded `parent_entity_value = original_query`. | Email search discovering a username cannot launch social search; domain discovery cannot launch threat intel. | Evaluate follow-up capabilities dynamically per discovered entity; record actual triggering parent entity; implement bounded recursive multi-stage queue. |
| 4 | `backend/app/search/orchestrator.py` & `infrastructure/neo4j/service.py` | Search relationships not persisted into MongoDB or Neo4j | `orchestrator.py` only wrote to `entity_repo` and `evidence_repo`, omitting `relationship_repo` and `neo4j_service.upsert_relationship`. | Graph expand endpoint `/api/v1/graph/expand` after search returns zero relationships from newly searched target. | Persist all `corr_relationships` with tenant and investigation scope into `relationship_repo` and Neo4j idempotently. |
| 5 | `backend/app/infrastructure/neo4j/service.py` | Legitimate relationship types sanitized to `"RELATED"` | `ALLOWED_REL_TYPES` omitted `LOCATED_AT`, `REGISTERED_TO`, `SUBDOMAIN_OF`, `HOSTED_ON_IP`, `HAS_VULNERABILITY`, etc. | Writing a `REGISTERED_TO` or `LOCATED_AT` edge rewrote the Neo4j edge type to `"RELATED"`. | Expand `ALLOWED_REL_TYPES` to mirror all canonical types in `RelationshipType` enum. |
| 6 | `backend/app/modules/osint/providers/vehicle_intelligence.py` | Factually misleading 0.99 registration confidence from regex plate prefix | `execute()` assigned 0.99 confidence and `REGISTERED_TO` relationship based purely on syntax parsing of Indian HSRP or UK plates. | Vehicle search for `TN34MA8562` claims verified registration to Tiruchengode RTO. | Separate syntax validity, administrative jurisdiction attribution, and live registration database queries. |
| 7 | `backend/app/modules/geo_intelligence/module.py` | Bogus `LOCATED_AT` relationships to searched query | Line 136: `target_val = obs.associated_entity_value or context.query`. Creates a personal `LOCATED_AT` relationship even when the observation is unassociated with the searched subject. | Querying a person when a general news article mentions a city links the person to that city as `LOCATED_AT`. | Only link `LOCATED_AT` if observation has an explicit verified association; otherwise create `MENTIONED_LOCATION` or `POSSIBLE_ASSOCIATION`. |
| 8 | `backend/app/modules/social_media_intelligence/collectors/youtube.py` | Keyword queries return empty video lists | `search_posts()` only checked `extract_video_id()`, returning `[]` for any general keyword or subject name. | Searching an investigative topic or person on YouTube returned 0 posts. | Implement keyword video discovery using YouTube Data API and public RSS feeds with strict zero fake transcripts. |
| 9 | `backend/app/infrastructure/mongodb/repositories.py` | `RuntimeError: Event loop is closed` in asynchronous test runs | Motor async client instances cached closed event loops between test functions. | `test_api_relationship_evidence_provenance` in full test suite. | Wrap Motor cursor executions with error catching and seamless in-memory fallback. |
| 10 | Frontend Graph & Detail views | Absent confidence rendered as "85% Verified" | UI components defaulted `confidence ?? 0.85`, displaying fabricated confidence. | Viewing an unrated node in GraphStudioComponent shows 85%. | Display "Unknown / Unrated" when confidence is absent. |

---

## REMEDIATION ROADMAP

1. **Phase 1: Identifier Accuracy & Clean Seed Separation (Rule 2)**
   - Eliminate synthetic query entity validation bypass.
   - Separate seed verification status from discovered candidates.
   - Configure tenant-aware phone dial plan settings.
2. **Phase 2: Dynamic Clue-to-Clue Investigation Orchestrator (Rule 3, 4, 6)**
   - Implement capability-aware dynamic module routing for follow-up pivots.
   - Preserve exact parent-child provenance in `pivot_engine.py`.
   - Bounded recursive execution queue respecting max depth and tenant entitlements.
3. **Phase 3: Search-to-Graph & Neo4j Dual Persistence (Rule 10)**
   - Persist entities, evidence, and relationships to MongoDB and Neo4j.
   - Expand Neo4j allowlist for all `RelationshipType` values.
4. **Phase 4: Domain, Vehicle & Social Media Truthfulness (Rule 5, 8)**
   - Passive threat intel on discovered domains.
   - Vehicle prefix attribution separated from live registration.
   - YouTube keyword search and Meta Graph API version validation.
5. **Phase 5: Geospatial Provenance & Time Filtering (Rule 7)**
   - Eliminate unsupported `LOCATED_AT` associations.
   - Preserve coordinate precision and case isolation.
6. **Phase 6: Frontend Telemetry & End-to-End Verification (Rule 11, 12)**
   - Remove fake confidence defaults in UI.
   - Add comprehensive end-to-end multi-stage integration tests (Scenarios A through F).
