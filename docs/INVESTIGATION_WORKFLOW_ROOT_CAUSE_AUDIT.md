# Sential Intelligence — Investigation Workflow Root Cause Audit

**Document Version**: 1.0.0  
**Date**: October 17, 2026  
**Auditor**: Antigravity Core Engine Team  
**Status**: Root Causes Identified, Verified Against Live Services, and Targeted for Full Remediation

---

## Executive Summary

An forensic audit of the investigation workflow, live database state (MongoDB & Neo4j), backend search orchestration (`orchestrator.py`, `osint/module.py`), and frontend graph visualization (`GraphStudioComponent.tsx`) was conducted to trace the five critical anomalies observed in the investigation workspace screenshot:

1. A phone-number target (`+916382953372`) displayed as `DOMAIN` in the graph inspector.
2. A `100% confidence` verification label displayed despite only `search_query` appearing as the source.
3. A `dhayaalan` entity linked to the phone number without a valid identity-verification source or evidence.
4. OSINT results present but zero Profiles, News, and Geospatial results.
5. An empty or incomplete follow-up relationship chain with collapsed provenance.

Each defect has been traced to exact lines of code, reproduced via live database query and test fixtures, and assigned an explicit remediation plan and regression test suite.

---

## Defect 1: Phone-Number Target Displayed as `DOMAIN` in Graph Inspector

### 1. Observed Behavior
When searching a phone number (e.g., `+916382953372`), the node in the relationship graph and the inspector drawer header display `DOMAIN` with a globe icon instead of `PHONE` with a telephone icon.

### 2. Root Cause
In `frontend/src/features/graph/GraphStudioComponent.tsx` (lines 66–78):
```typescript
export const getEntityCategory = (type: string = ''): string => {
  const t = type.toUpperCase();
  if (['VEHICLE', 'CAR', 'AUTOMOBILE', 'PLATE', 'VEHICLE_PLATE', 'ASSET'].includes(t)) return 'VEHICLE';
  if (['LOCATION', 'GEO', 'COORDINATES', 'PLACE', 'CITY', 'COUNTRY', 'STATE', 'REGION'].includes(t)) return 'LOCATION';
  if (['PERSON', 'THREAT_ACTOR', 'USERNAME', 'AUTHOR', 'ACTOR'].includes(t)) return 'PERSON';
  if (['ORGANIZATION', 'ORG', 'COMPANY', 'GROUP', 'NGO', 'FOUNDATION', 'TERROR_GROUP', 'GOVERNMENT', 'AUTHORITY', 'REGISTRY'].includes(t)) return 'ORGANIZATION';
  if (['VULNERABILITY', 'CVE', 'THREAT_INDICATOR', 'MALWARE', 'THREAT'].includes(t)) return 'THREAT_INDICATOR';
  if (['IP', 'IPV4', 'IPV6'].includes(t)) return 'IP';
  if (['HASH', 'SHA256', 'MD5'].includes(t)) return 'HASH';
  if (['EMAIL'].includes(t)) return 'EMAIL';
  if (['URL', 'DOCUMENT', 'ARTICLE', 'NEWS'].includes(t)) return 'DOCUMENT';
  return 'DOMAIN'; // <-- CRITICAL BUG: Unmatched types silently default to DOMAIN
};
```
1. There was no mapping for `PHONE`, `TELEPHONE`, `MSISDN`, `CELL`, `MOBILE`, `PHONE_NUMBER`.
2. Fallback line 77 unconditionally returned `'DOMAIN'`.
3. In backend serialization, `EntityType.KEYWORD` was serialized as `'entitytype.keyword'` or `'entity'`, which was also unmatched and became `'DOMAIN'`.
4. `getCategorySvgIcon()` only supported `VEHICLE`, `LOCATION`, `PERSON`, `ORGANIZATION`, leaving phone nodes with broken or fallback icons.

### 3. Remediation
1. Expand `getEntityCategory()` in `GraphStudioComponent.tsx` to explicitly handle:
   - `PHONE`, `TELEPHONE`, `MSISDN`, `MOBILE`, `CELL`, `PHONE_NUMBER` -> `'PHONE'`
   - `EMAIL`, `MAILBOX` -> `'EMAIL'`
   - `DOMAIN`, `SUBDOMAIN`, `HOSTNAME`, `FQDN`, `WEBSITE` -> `'DOMAIN'`
   - `VIDEO`, `POST`, `IMAGE`, `MEDIA` -> respective categories
   - `EVIDENCE`, `VULNERABILITY`, `THREAT_INDICATOR`, `KEYWORD`
   - Fallback must return `'UNKNOWN'` or `'OTHER'`, **never `'DOMAIN'`**.
2. Add dedicated SVG icons and palette tokens for `PHONE`, `EMAIL`, `VIDEO`, `POST`, `DOCUMENT`, `UNKNOWN`.
3. Update inspector header to derive canonical type and category safely.

### 4. Regression Test
- `test_graph_category_normalization_phone_not_domain`
- Frontend Jest/Playwright assertion verifying `getEntityCategory('phone') === 'PHONE'`.

---

## Defect 2: 100% Verification Label Despite Only `search_query` as Source

### 2. Observed Behavior
The phone number seed entity displays "100% confidence" and "VERIFIED" badge in the inspector, while the only source listed is `search_query`.

### 2. Root Cause
1. **Backend Source Injection**:
   - In `backend/app/modules/osint/module.py` (lines 302–308):
     ```python
     entities.insert(0, EntityPayload(
         type=root_type,
         value=context.query,
         confidence=1.0,  # <-- Fabricated 100% confidence for unverified input query!
         sources=["search_query"],
         metadata={"is_search_target": True}
     ))
     ```
   - In `backend/app/search/orchestrator.py` (lines 398–402):
     ```python
     corr_entities.append(EntityPayload(
         id=f"ent_{uuid.uuid4().hex[:8]}",
         type=d_type,
         value=mv,
         confidence=1.0,  # <-- Fabricated 100% confidence for synthetic graph node!
         sources=["relationship_graph"],
         metadata={}
     ))
     ```
2. **Frontend Uncritical Display**:
   - In `GraphStudioComponent.tsx` (lines 1478–1479):
     `selectedEntity.confidence != null ? `${Math.round(selectedEntity.confidence * 100)}% confidence` : 'Unrated Confidence'`
     Because `confidence=1.0` was returned by backend, the UI rendered `100% confidence`.
   - The UI lacked separation between "Query Seed", "Syntax Validated", "Source Corroborated", and "Authoritatively Verified".

### 3. Remediation
1. **Backend**:
   - A raw query seed entity must have `confidence=None` (or 0.0 unassessed) and `metadata={"is_seed_input": True, "verification_status": "UNASSESSED"}`.
   - Connected graph nodes without authoritative provider backing must have `confidence=0.5` or `None` with `verification_status="UNVERIFIED_GRAPH_LEAD"`.
   - Only entities backed by authoritative provider records (e.g., ITU-T plan or database record with matching cryptographic/registry hash) may receive calibrated confidence.
2. **Frontend**:
   - Render granular verification state:
     - `Seed Query`: "Unassessed Seed Input" (amber badge, no false 100%).
     - `Syntax Validated`: "Syntax Validated (ITU-T E.164)" (blue badge).
     - `Authoritative`: "Corroborated by Registry" (green badge with provider citations).
     - `Graph Lead`: "Uncorroborated Graph Lead" (slate badge).

### 4. Regression Test
- `test_unit_seed_query_confidence_is_unassessed_not_100`
- `test_unverified_graph_node_does_not_claim_100_percent`

---

## Defect 3: `dhayaalan` Linked to Phone Without Visible Identity-Verification Source

### 1. Observed Behavior
An entity named `dhayaalan` appears in the graph linked directly to phone `+916382953372` with an `OWNS` or `RELATED` edge, but without any underlying subscriber registry evidence or explanation.

### 2. Root Cause
1. **Live MongoDB Inspection**:
   Querying `relationships` in MongoDB revealed:
   ```json
   {
     "id": "rel_person_phone",
     "source_entity_value": "dhayaalan",
     "target_entity_value": "+916382953372",
     "relationship_type": "OWNS",
     "confidence": 0.95,
     "sources": ["identity_resolver"],
     "evidence_ids": []
   }
   ```
   This record was inserted without supporting evidence IDs (`evidence_ids: []`).
2. **Orchestrator Blind Merge**:
   In `backend/app/search/orchestrator.py` (lines 344–363), `orchestrator.py` queried stored relationships:
   ```python
   stored_rels = await relationship_repo.find_by_entity_values(tenant_id, list(verified_vals))
   ```
   It imported any stored relationship matching the phone number without verifying whether it belonged to the active investigation or had valid supporting evidence records!
3. **OSINT Module Fan-In**:
   In `backend/app/modules/osint/module.py` (lines 268–285), when any provider returned entities, it unconditionally linked them directly to `context.query` with `basis="DIRECT_OBSERVATION"`, creating spurious direct edges.

### 3. Remediation
1. Enforce strict evidentiary provenance: relationships without valid `evidence_ids` must not be presented as confirmed identity relationships.
2. In `orchestrator.py`, scope relationship retrieval to the active investigation/case, or verify that any cross-investigation relationship has corroborating evidence.
3. For phone numbers where live lawful subscriber resolution is not configured (`CONFIG_REQUIRED`), explicitly report that subscriber identity is unassigned/unresolved. Do not guess personal names.
4. If an identity candidate is found through an intermediate clue (e.g. `Phone -> Ad -> Username -> Person`), preserve intermediate parent-child hops rather than drawing a direct edge to the phone number.

### 4. Regression Test
- `test_phone_search_does_not_link_unsupported_person_without_evidence`
- `test_relationship_requires_supporting_evidence_ids`

---

## Defect 4: OSINT Results Present but Zero Profiles, News, and Geospatial Results

### 1. Observed Behavior
Searching a phone number returns OSINT metadata (carrier and country), but all other intelligence tabs (Profiles, News, Geospatial, Media) show 0 results.

### 2. Root Cause
In `backend/app/search/orchestrator.py` (lines 81–98):
```python
if is_identifier and normalized_identifier:
    if identifier_type == "EMAIL":
        target_type = "email"
        selected_scopes = ["PEOPLE & IDENTITIES"]
    elif identifier_type == "PHONE":
        target_type = "phone"
        selected_scopes = ["PEOPLE & IDENTITIES"]
    ...
    target_modules_set = {"osint"} # <-- HARDCODED EXCLUSION OF OTHER MODULES
```
1. When an exact identifier was detected, `target_modules_set` was strictly restricted to `{"osint"}`.
2. `social_media_intelligence`, `news_intelligence`, and `geo_intelligence` were never invoked for the initial search.
3. Furthermore, when OSINT discovered secondary clues (such as geographic jurisdiction `India`, carrier `Reliance Jio Infocomm`, or associated accounts), no automated follow-up jobs were dispatched to `news_intelligence` or `geo_intelligence`.

### 3. Remediation
1. Dynamic Multi-Stage Pipeline:
   - Initial stage validates the seed identifier via OSINT/telecom provider.
   - When verified clues are discovered (e.g., jurisdiction, carrier, or source-backed candidate usernames/names):
     - Route candidate usernames/names to `social_media_intelligence`.
     - Route entity names and incident keywords to `news_intelligence`.
     - Route geographic locations and coordinate-bearing evidence to `geo_intelligence`.
     - Route domains and hostnames to `threat_intelligence`.
2. Allow user-selected modules or scope-based multi-module execution even for identifier searches.

### 4. Regression Test
- `test_identifier_search_dispatches_multimodule_followups`
- `test_phone_with_location_populates_geo_intelligence`

---

## Defect 5: Empty or Incomplete Follow-Up Relationship Chain

### 1. Observed Behavior
The graph showed isolated nodes or flat 1-hop star topologies, with missing intermediate provenance (e.g., why a person was connected to a phone, or how a post was connected to an account).

### 2. Root Cause
1. In `orchestrator.py` and `osint/module.py`, pivots were either not recursively scheduled, or were flattened into direct edges to the root query.
2. In `Neo4jGraphService.expand_entity()`, 1-hop expansions returned only immediate edges without evidence lineage.
3. Intermediate entities (such as a specific post, video, or registry certificate) were skipped in favor of connecting the end entity directly to the root.

### 3. Remediation
1. Maintain an explicit multi-stage investigation queue with:
   - `root_target` -> `provider_executions` -> `extracted_clues` -> `candidate_evaluations` -> `follow_up_jobs`.
2. Every relationship payload must carry:
   - `source_id`, `target_id`, `relationship_type`, `hop_depth`, `parent_job_id`, `evidence_ids`, `basis`.
3. Graph expansion endpoint must preserve shared nodes and intermediate provenance chains.

### 4. Regression Test
- `test_multihop_provenance_chain_preservation`
- `test_neo4j_expansion_retains_evidence_links`

---

## Comprehensive Defect Matrix

| Defect # | Symptom | Root Cause File & Line | Resolution | Regression Test |
|---|---|---|---|---|
| **1** | Phone shown as `DOMAIN` | `frontend/src/features/graph/GraphStudioComponent.tsx:77` | Add canonical types to `getEntityCategory()`, fallback to `'UNKNOWN'`, add SVG icon | `test_graph_category_normalization_phone_not_domain` |
| **2** | False 100% confidence for `search_query` | `backend/app/modules/osint/module.py:305`, `orchestrator.py:399` | Seed query confidence `None`/unassessed; require evidence for high confidence | `test_unit_seed_query_confidence_is_unassessed_not_100` |
| **3** | Unverified `dhayaalan` linked to phone | `orchestrator.py:344`, stale MongoDB `rel_person_phone` | Require `evidence_ids`; isolate cases; do not link uncorroborated candidates | `test_phone_search_does_not_link_unsupported_person_without_evidence` |
| **4** | 0 Profiles, News, Geo on identifier search | `orchestrator.py:98` (`target_modules_set = {"osint"}`) | Implement multi-stage investigation queue dispatching to all relevant modules | `test_identifier_search_dispatches_multimodule_followups` |
| **5** | Incomplete relationship chain | `osint/module.py:270`, collapsed graph edges | Preserve intermediate parent-child hops (`Phone -> Carrier/Loc`, `User -> Post -> Loc`) | `test_multihop_provenance_chain_preservation` |

