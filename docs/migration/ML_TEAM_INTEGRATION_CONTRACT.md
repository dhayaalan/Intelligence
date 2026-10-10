# Machine Learning Team Integration Contract & Service Boundary

## 1. Architectural Overview & Separation of Concerns

The Intelligence Platform has decoupled all internal AI/ML model inference, prompt orchestration, and simulated reasoning agents from the core application codebase.

- **Core Application Responsibility:**
  Deterministic intelligence collection, OSINT tools (335 tools), social media ingestion (Bluesky, Telegram, Reddit, Mastodon, YouTube), coordinated inauthentic behavior (CIB) 5-gram shingle detection, source credibility metrics, news parsing, case and investigation management, tenant isolation, and cryptographic evidence custody (SHA-256).
- **ML Team Responsibility:**
  Independent development, training, fine-tuning, evaluation, containerization, and hosting of autonomous AI/ML microservices (e.g., neural synthesis, grounded question answering, narrative graph clustering, multi-modal forensics).

```
+------------------------------------+             +-------------------------------------+
|        Intelligence Platform       |             |         External ML Service         |
|  (FastAPI Backend / React 18)     |             |      (ML Team Managed Container)    |
+------------------------------------+             +-------------------------------------+
|                                    |   HTTP REST |                                     |
|  1. Investigator submits query     |  Requests   |                                     |
|  2. Collects sealed evidence       | ----------> |  1. Validates JWT / Service Key     |
|  3. Attaches Tenant & Trace Context|             |  2. Loads neural / agent models     |
|  4. Dispatches via MLServiceClient | <---------- |  3. Synthesizes grounded results    |
|  5. Renders structured citations   |  Structured |  4. Returns assertions & citations  |
|                                    |   Responses |                                     |
+------------------------------------+             +-------------------------------------+
```

---

## 2. Configuration & Independent Deployment

The external ML service is configured entirely via environment variables and does not require any shared codebase or database dependencies.

### Environment Variables
| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `ML_SERVICE_URL` | string (URL) | `None` | Base HTTP endpoint of the external ML microservice (e.g., `http://ml-service.internal:8080`). If unset, the core application returns `status: "not_configured"`. |
| `ML_SERVICE_API_KEY` | string | `None` | Optional bearer token or shared secret sent in `Authorization: Bearer <token>`. |
| `ML_SERVICE_TIMEOUT_SECONDS` | integer | `30` | Maximum timeout before the core platform marks the request as `status: "timeout"`. |

When `ML_SERVICE_URL` is omitted, the platform gracefully disables ML features without crashing and presents explicit `not_configured` status banners to investigators.

---

## 3. Security, Multi-Tenancy & Context Propagation

Every request from the Intelligence platform passes an explicit security envelope in both HTTP headers and request payload:

### Security Headers
```http
Authorization: Bearer <ML_SERVICE_API_KEY>
X-Tenant-ID: <tenant_uuid>
X-User-ID: <user_uuid>
X-Trace-ID: trace-<timestamp>-<uuid>
Content-Type: application/json
```

### Context Schema (`MLContext`)
```json
{
  "tenant_id": "tenant-001-corp",
  "user_id": "usr-inv-948",
  "investigation_id": "inv-case-8492",
  "classification_level": "TLP:AMBER",
  "trace_id": "trace-1728556800-abc123"
}
```

The ML service **must**:
1. Strictly preserve tenant boundaries: never cross-contaminate embeddings, vector memory, or prompts across different `tenant_id`s.
2. Honor classification levels (`TLP:CLEAR`, `TLP:GREEN`, `TLP:AMBER`, `TLP:RED`).

---

## 4. Evidence References & Cryptographic Provenance

To eliminate hallucinations, the Intelligence platform passes real evidence artifacts with their cryptographic signatures:

### Evidence Reference Schema (`EvidenceReference`)
```json
{
  "evidence_id": "EV-001",
  "citation_label": "[EV-001: CIOL Wire Dispatch]",
  "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "source_uri": "https://ciol.com/reports/cyber-attack-vector",
  "snippet": "Coordinated bot network identified amplifying narrative targeting critical banking infrastructure."
}
```

The ML service **must**:
- Ground every factual assertion in one or more provided `evidence_id`s.
- Return references that match the input `evidence_id`s.
- Never invent citations for non-existent evidence.

---

## 5. API Endpoints Contract

The ML team must implement the following REST endpoints on their microservice:

### 5.1 Service Health & Capabilities (`GET /health`)
```http
GET /health HTTP/1.1
```
**Response (200 OK):**
```json
{
  "status": "available",
  "service_name": "sential-ml-inference-engine",
  "version": "1.0.0",
  "supported_capabilities": [
    "evidence_grounded_synthesis",
    "multi_platform_persona_correlation"
  ],
  "model_info": {
    "synthesis_model": "mistral-large-instruct-v2",
    "embedding_model": "bge-large-en-v1.5"
  }
}
```

---

### 5.2 Evidence-Grounded Analysis (`POST /v1/analyze`)
Submits investigative queries against pinned evidence vault records.

**Request Schema (`MLAnalysisRequest`):**
```json
{
  "target": "Infrastructure Disruption Investigation",
  "target_type": "DOMAIN",
  "query": "Synthesize verified evidence regarding command-and-control beacons and state remaining gaps.",
  "context": {
    "tenant_id": "tenant-001-corp",
    "user_id": "usr-inv-948",
    "investigation_id": "inv-case-8492",
    "classification_level": "TLP:AMBER",
    "trace_id": "trace-1728556800-abc123"
  },
  "evidence": [
    {
      "evidence_id": "EV-001",
      "citation_label": "[EV-001: Suricata Alert]",
      "sha256_hash": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
      "source_uri": "https://logs.internal/suricata/alert/4812",
      "snippet": "Beacon detected connecting to external IP 198.51.100.42 on port 443."
    }
  ],
  "parameters": {
    "max_tokens": 1024,
    "temperature": 0.1
  }
}
```

**Response Schema (`MLAnalysisResponse`):**
```json
{
  "status": "success",
  "model_id": "mistral-large-instruct-v2",
  "synthesis": "Suricata network logs substantiate active outbound beaconing to IP 198.51.100.42 over TLS port 443 [EV-001]. No persistence mechanism has yet been verified on local disk.",
  "citations": [
    {
      "evidence_id": "EV-001",
      "citation_label": "[EV-001: Suricata Alert]",
      "sha256_hash": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
      "source_uri": "https://logs.internal/suricata/alert/4812",
      "snippet": "Beacon detected connecting to external IP 198.51.100.42 on port 443."
    }
  ],
  "key_assertions": [
    "Outbound beaconing confirmed against IP 198.51.100.42.",
    "Communication established using port 443 (HTTPS)."
  ],
  "intelligence_gaps": [
    "Host-level memory dump and process lineage remain uncollected.",
    "Parent domain registration for IP 198.51.100.42 has not been correlated."
  ],
  "contradictions": [],
  "execution_time_ms": 1420.5,
  "error_message": null
}
```

---

### 5.3 Multi-Platform Persona Correlation (`POST /v1/persona-correlation`)
Correlates aliases and cross-platform behavior across social networks.

**Request Schema (`MLPersonaCorrelationRequest`):**
```json
{
  "target_handle": "disinfo_actor_99",
  "context": {
    "tenant_id": "tenant-001-corp",
    "user_id": "usr-inv-948",
    "investigation_id": "inv-case-8492",
    "classification_level": "TLP:AMBER",
    "trace_id": "trace-1728556800-def456"
  },
  "platforms": ["bluesky", "telegram", "reddit", "mastodon", "youtube"],
  "parameters": {
    "min_similarity_threshold": 0.85
  }
}
```

**Response Schema (`MLPersonaCorrelationResponse`):**
```json
{
  "status": "success",
  "model_id": "graph-persona-embedder-v1",
  "discovered_profiles": [
    {
      "platform": "bluesky",
      "handle": "disinfo_actor_99.bsky.social",
      "profile_url": "https://bsky.app/profile/disinfo_actor_99.bsky.social",
      "similarity_score": 0.96,
      "correlated_attributes": ["bio_text_match", "creation_window_cluster"]
    }
  ],
  "credibility_score": 14.5,
  "risk_indicators": [
    "Cross-platform handle reuse across 4 networks within 48h.",
    "Account created during coordinated narrative launch window."
  ],
  "execution_time_ms": 2105.0,
  "error_message": null
}
```

---

## 6. Execution Status & Error Representation

The integration contract defines explicit execution statuses in `MLExecutionStatus`:

| Status | Code / Condition | Meaning |
| :--- | :--- | :--- |
| `not_configured` | Platform setting unset | Core platform has no `ML_SERVICE_URL`. Gracefully skips ML processing. |
| `available` | HTTP 200 from `/health` | External service is reachable and ready to process requests. |
| `unavailable` | Connection refused / 503 | External ML microservice is offline or unhealthy. |
| `pending` | Background worker queue | Asynchronous analysis job queued. |
| `success` | HTTP 200 with result | Inference succeeded with structured grounding. |
| `failed` | HTTP 4xx / 5xx | ML service encountered an error; message returned in `error_message`. |
| `timeout` | Exceeded timeout limit | Request aborted after `ML_SERVICE_TIMEOUT_SECONDS`. |

### Error Payload Format
If an error occurs on the ML service, return HTTP 4xx/5xx or a structured payload:
```json
{
  "status": "failed",
  "model_id": null,
  "execution_time_ms": 320.0,
  "error_message": "Invalid input: Evidence payload EV-999 is corrupted or exceeds token limit."
}
```

---

## 7. Python Implementation Reference

The core application provides the contract definitions in:
- `backend/app/ml_contracts/models.py`: Pydantic V1/V2 compatible models (`MLAnalysisRequest`, `MLAnalysisResponse`, etc.).
- `backend/app/ml_contracts/client.py`: Non-blocking `MLServiceClient` using `httpx`.
- `backend/app/ml_contracts/router.py`: API endpoints mounted at `/api/v1/ml/*`.

The ML team can import or mirror these schemas in Python (FastAPI/Pydantic) or any other language/framework.
