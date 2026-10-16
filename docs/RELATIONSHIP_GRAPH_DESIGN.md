# Relationship Graph Architecture & Persistence Design

## 1. Persistence Layer Architecture: Neo4j Evaluation vs MongoDB

### Architectural Assessment

The prompt mandated an evaluation of **Neo4j as a dedicated graph persistence and traversal layer** versus improving the existing database architecture:

1. **Current Infrastructure Context**:
   - The platform relies on **MongoDB 7.0** running as a production container (`intelligence-mongodb` exposed on port 27018) via Docker Compose.
   - Primary collections already exist for `entities`, `relationships`, `evidence`, `cases`, and `investigations`.
   - The platform backend is asynchronous Python (FastAPI with Motor and PyMongo drivers).
   - Tenancy boundaries are strictly partitioned on `tenant_id` across every document.

2. **Neo4j Evaluation Results**:
   - **Strengths**: Native property graph storage, Cypher query language, efficient deep multi-hop pathfinding ($k \ge 3$).
   - **Trade-offs & Constraints in this Environment**:
     - Introducing Neo4j requires provisioning a dedicated JVM container (minimum 1.5–2GB RAM), configuring Bolt authentication, managing dual-writes between MongoDB (system of record) and Neo4j, and handling distributed transaction failures.
     - The investigator workflow operates primarily on **bounded 1-hop expansions**, neighborhood traversals, and typed entity inspections rather than global graph path computations.
   - **Architectural Decision**:
     - **Primary Graph Layer in MongoDB with Idempotent Schema Setup**: We improved the graph traversal engine directly in MongoDB using indexed document-based relationship modeling with compound indexes (`(tenant_id, source_id)`, `(tenant_id, target_id)`, `(tenant_id, relationship_type)`).
     - **Dedicated Graph APIs**: Abstracted graph traversal behind clean, versioned REST endpoints (`/api/v1/graph/expand`, `/api/v1/graph/relationships/{id}/evidence`, `/api/v1/entities/{id}/expand`).
     - **Neo4j Upgrade Path**: If multi-hop global shortest-path algorithms are required in the future, the dedicated API contract will allow swapping the persistence adapter without modifying the frontend or orchestrator.

---

## 2. Graph Data Model & Evidence Provenance

### Entities
- **Stable ID**: Formatted as `ent_<hash>` or UUID.
- **Entity Types**: `person`, `organization`, `email`, `phone`, `domain`, `ip`, `username`, `article`, `location`.
- **Properties**: `tenant_id`, `type`, `value`, `confidence`, `sources`, `metadata`.

### Typed Relationships
Every relationship has typed semantics and clear epistemic classification:
- **Relationship Types**: `OWNS`, `AFFILIATED_WITH`, `RESOLVES_TO`, `HOSTED_ON`, `COMMUNICATED_WITH`, `MENTIONED_IN`, `SUBSIDIARY_OF`, `ASSOCIATED_WITH`.
- **Basis Distinction**:
  - `DIRECT_OBSERVATION`: Relationships directly corroborated by telemetry, WHOIS registrations, corporate registries, DNS zone files, or official publications.
  - `INFERRED`: Hypothesized connections derived from co-occurrence or similarity algorithms.
- **Provenance Attributes**:
  - `evidence_ids`: Array of stable evidence record references (`["ev_whois_01", "ev_registry_02"]`).
  - `source`: Primary origin provider or document.
  - `confidence`: Calibrated score (0.0 to 1.0).
  - `first_seen` / `last_seen`: ISO-8601 observation timestamps.

### Elimination of Synthetic Edges
- Removed all arbitrary `CO_OCCURS_IN_INVESTIGATION` $O(N^2)$ cross-product edge generation in `backend/app/entities/resolver.py`.
- Removed all `e-synth-...` hardcoded mock edge generators in `frontend/src/features/graph/GraphStudioComponent.tsx`.

---

## 3. Idempotent Graph Writes & Deduplication

In `RelationshipRepository.save()`:
- Writes use MongoDB `$set` with `upsert=True` keyed on `{"id": rel_id, "tenant_id": tenant_id}` or composite keys `{"source_id": s, "target_id": t, "relationship_type": type, "tenant_id": tenant_id}`.
- Repeated ingestion scans update `last_seen` timestamps and merge new `evidence_ids` without duplicating edges on the investigator canvas.

---

## 4. State-Aware 1-Hop Expansion & Collapse Interaction Model

### Expansion Algorithm (`POST /api/v1/graph/expand` & `GET /api/v1/graph/expand`)
1. **Seed Isolation**: Traversal begins strictly from the requested seed entity ID.
2. **Hop Bound**: Only relationships directly connected (1 hop) to the seed are returned. Traversal depth defaults to 1, avoiding unconstrained graph explosion.
3. **Canvas De-duplication**:
   - The backend checks `visible_node_ids` sent by the frontend.
   - Nodes already present on the canvas are classified as `shared_nodes`, while new entities are classified as `new_nodes`.
4. **Shared Node Retention on Collapse**:
   - When an investigator collapses branch $B$, only nodes and edges exclusively introduced by branch $B$ that have no other active connections to visible branches are pruned.
   - Shared nodes (e.g. an organization shared by multiple individuals) remain intact on the canvas.
5. **Position Stability**: Existing node layout coordinates are preserved during incremental expansions; auto-relayout is only triggered upon explicit investigator request.

---

## 5. Security & Tenant Isolation

- Every graph query requires a valid JWT with `current_user` injected via FastAPI dependency.
- All database queries filter on `tenant_id == current_user.tenant_id`.
- Attempts to expand an entity belonging to another tenant or access evidence cross-tenant return `404 Not Found` or `403 Forbidden`.
