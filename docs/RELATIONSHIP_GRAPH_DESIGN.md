# Relationship Graph Architecture & Neo4j Integration Design

## 1. Dedicated Graph Database Architecture: Neo4j Integration

### Architectural Separation of Responsibilities

To achieve scalable relationship intelligence and prevent graph visualization clutter, the platform utilizes **Neo4j as the dedicated relationship graph persistence and traversal engine**, operating alongside **MongoDB 7.0 as the authoritative system of record**.

| System Component | Role & Scope of Authority |
| :--- | :--- |
| **MongoDB 7.0** | Authoritative store of record for investigations, dossiers, raw OSINT source documents, evidence texts, user credentials, tenancy configurations, and case metadata. |
| **Neo4j 5.20** | High-performance property graph database storing canonical entities (`(:Entity)`), directed typed relationships (`-[:INVESTIGATION_REL]->`), graph topology, path traversals, and multi-hop relationship provenance. |
| **Backend API** | FastAPI service enforcing multi-tenant isolation, query parameterization, Cypher injection prevention, bounded traversal limits, and transparent fallback to MongoDB if Neo4j is offline. |
| **Frontend UI** | ReactFlow-based investigator studio rendering compact, uncluttered nodes, focus-first seed layouts, branch expansion/collapse, and evidence inspectors. |

---

## 2. Neo4j Infrastructure & Deployment Configuration

### Docker Compose Service Definition

Neo4j is provisioned as `intelligence-neo4j` in `docker-compose.yml`:

```yaml
neo4j:
  image: neo4j:5.20.0-community
  container_name: intelligence-neo4j
  restart: unless-stopped
  environment:
    - NEO4J_AUTH=neo4j/sential_neo4j_secret
    - NEO4J_PLUGINS=["apoc"]
    - NEO4J_dbms_memory_heap_initial__size=512m
    - NEO4J_dbms_memory_heap_max__size=1024m
    - NEO4J_dbms_memory_pagecache_size=512m
  ports:
    - "127.0.0.1:7474:7474" # Browser & HTTP API
    - "127.0.0.1:7687:7687" # Bolt Binary Protocol
  volumes:
    - neo4j_data:/data
  healthcheck:
    test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:7474 || exit 1"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### Connection Management & Pooling

The backend manages Neo4j connections through `Neo4jClient` (`backend/app/infrastructure/neo4j/client.py`):
- **Asynchronous Driver**: Uses `neo4j.AsyncGraphDatabase` with connection pooling (`max_connection_pool_size=50`, `max_connection_lifetime=3600`, `connection_timeout=15.0`).
- **Event-Loop Resiliency**: Implements running-loop validation so async tests and worker coroutines cleanly instantiate drivers without loop attachment collisions.
- **Health Checks & Observability**: Exposes `/health/ready` and `/api/v1/graph/status` endpoints reporting Bolt connectivity status and server engine version.

---

## 3. Graph Schema Constraints & Indexes

Upon startup or migration, `neo4j_client.init_schema()` idempotently enforces the following Cypher constraints and indexes:

```cypher
-- Unique entity constraint scoped to stable entity ID
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS 
FOR (e:Entity) REQUIRE e.id IS UNIQUE;

-- Tenant partitioning index
CREATE INDEX entity_tenant_idx IF NOT EXISTS 
FOR (e:Entity) ON (e.tenant_id);

-- Composite tenant + normalized value index for sub-millisecond seed discovery
CREATE INDEX entity_tenant_val_idx IF NOT EXISTS 
FOR (e:Entity) ON (e.tenant_id, e.value);

-- Entity classification index
CREATE INDEX entity_type_idx IF NOT EXISTS 
FOR (e:Entity) ON (e.tenant_id, e.type);

-- Relationship constraint for stable relationship ID
CREATE CONSTRAINT rel_id_unique IF NOT EXISTS 
FOR ()-[r:INVESTIGATION_REL]-() REQUIRE r.id IS UNIQUE;
```

---

## 4. Entity and Relationship Data Model

### Entity Nodes (`(:Entity)`)

Every entity in the graph is represented with the following properties:
- `id` (string, unique): Canonical identifier (e.g. `ent_alice_sec`).
- `tenant_id` (string): Mandatory tenant isolation key.
- `value` (string): Primary label or identifier (e.g. `Alice Sec`, `example.com`).
- `type` (string): Semantic entity type (`person`, `organization`, `email`, `phone`, `domain`, `ip`, `document`, `threat_indicator`).
- `confidence` (float): Analyst or algorithm confidence score (0.0 to 1.0).
- `sources` (list of strings): Correlating source providers (`["whois", "shodan"]`).
- `metadata` (JSON string): Additional verified key-value attributes.
- `last_seen` (datetime): Timestamp of latest corroboration.

### Directed Typed Relationships (`-[r]->`)

Connections represent verifiable relationships between entities:
- `id` (string): Stable edge ID (e.g. `rel_alice_owns_darkinfra`).
- `tenant_id` (string): Tenant boundary key.
- `type` (string): Canonical relationship type (`OWNS`, `AFFILIATED_WITH`, `RESOLVES_TO`, `HOSTED_ON`, `COMMUNICATED_WITH`, `MENTIONED_IN`, etc.).
- `basis` (string): Epistemic classification:
  - `DIRECT_OBSERVATION`: Confirmed by authoritative technical records (WHOIS, DNS, TLS certificates, corporate registries).
  - `INFERRED`: Derived via algorithmic association (co-occurrence, text extraction).
- `is_inferred` (boolean): Flag explicitly indicating inferred connections.
- `inference_method` (string): Explanation if inferred (e.g. `nlp_entity_co_occurrence`).
- `confidence` (float): Edge confidence score (0.0 to 1.0).
- `evidence_ids` (list of strings): Foreign keys referencing supporting evidence records in MongoDB (`["ev_whois_proof_01"]`).
- `source` (string): Origin system or provider.
- `investigation_id` (string): Case/investigation scope.

---

## 5. Parameterized Cypher & Security Rules

### Cypher Injection Prevention

Dynamic relationship types or labels are never concatenated from raw user input. `Neo4jGraphService` enforces a strict allowlist:

```python
ALLOWED_REL_TYPES = {
    "OWNS", "AFFILIATED_WITH", "RESOLVES_TO", "HOSTED_ON", "COMMUNICATED_WITH",
    "MENTIONED_IN", "SUBSIDIARY_OF", "ASSOCIATED_WITH", "FOUNDER", "CHAIR",
    "PRESIDENT", "DIRECTOR", "LEADERSHIP", "MEMBER", "CO_FOUNDER", "SPONSORS",
    "USES", "POWERED_BY", "PROJECT_OF", "WORKS_WITH", "EXPOSED_BY", "THREAT",
    "ATTRIBUTED_TO", "MALICIOUS", "INVESTIGATION_REL", "CO_OCCURS", "RELATED"
}
```

Any unknown or unsanitized input defaults to `RELATED`. All query values (`tenant_id`, `clean_val`, `limit`, `min_conf`) are strictly passed as Cypher query parameters.

### Bounded 1-Hop Traversal Cypher

```cypher
MATCH (s:Entity)
WHERE s.tenant_id = $tenant_id 
  AND (s.id = $clean_val OR toLower(s.value) = toLower($clean_val))
MATCH (s)-[r]-(t:Entity)
WHERE r.tenant_id = $tenant_id
  AND ($min_conf IS NULL OR r.confidence >= $min_conf)
  AND ($inv_id = '' OR r.investigation_id = $inv_id OR r.investigation_id = '')
RETURN properties(s) AS s, properties(r) AS r, properties(t) AS t, type(r) AS rel_type,
       startNode(r).id AS start_id, endNode(r).id AS end_id
LIMIT $limit
```

---

## 6. Synchronization & MongoDB Backfill Strategy

### Idempotent Backfill API (`POST /api/v1/graph/sync`)

To ensure MongoDB and Neo4j stay synchronized without uncontrolled dual writes:
1. `Neo4jGraphService.sync_from_mongodb(tenant_id)` retrieves existing entity and relationship records from MongoDB.
2. Entities are upserted into Neo4j using `MERGE (e:Entity {id: $id, tenant_id: $tenant_id})`.
3. Relationships are merged using `MERGE (s)-[r:INVESTIGATION_REL {id: $rel_id, tenant_id: $tenant_id}]->(t)`.
4. The migration is idempotent, safe to re-run repeatedly, and preserves all `evidence_ids` and timestamps.
5. In case of Neo4j service disruption, backend API routes seamlessly fall back to MongoDB repositories without returning fabricated data.
