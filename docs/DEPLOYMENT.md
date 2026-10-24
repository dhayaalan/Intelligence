# Deployment Guide & Local Execution Topology

## 1. System Overview

Sential Intelligence Platform is engineered for hybrid local and cloud deployments. The core system operates across containerized microservices communicating over an isolated Docker bridge network (`intelligence-network`).

```
                              ┌─────────────────────────────────────────┐
                              │          Nginx Reverse Proxy            │
                              │           (Port 3000 / SPA)             │
                              └────────────────────┬────────────────────┘
                                                   │
                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FastAPI Core Backend (Port 8000)                             │
│                                                                                                │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌────────────────────────────────────┐  │
│  │ Investigation Engine  │  │   Search Orchestrator │  │   Camera & ANPR Forensics Engine   │  │
│  └───────────────────────┘  └───────────────────────┘  └────────────────────────────────────┘  │
└───────┬─────────────────────────┬─────────────────────────────┬──────────────────────────┬─────┘
        │                         │                             │                          │
        ▼                         ▼                             ▼                          ▼
┌──────────────┐          ┌──────────────┐            ┌───────────────────┐      ┌───────────────────┐
│   MongoDB    │          │    Neo4j     │            │  theHarvester     │      │   SpiderFoot      │
│  (Port 27018)│          │ (7474 / 7687)│            │  Worker (5002)    │      │  Daemon (5001)    │
│ Primary Store│          │ Graph Store  │            │  [Profile:scanners│      │ [Profile:scanners]│
└──────────────┘          └──────────────┘            └───────────────────┘      └───────────────────┘
```

---

## 2. Tool Execution Compatibility Matrix

Every intelligence provider and processing engine has an explicitly defined execution boundary:

| Tool / Component | Execution Mode | Container / Runtime | Port / Interface | Network Bound | External Key Required |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sential Backend** | Container | Python 3.10 non-root | `8000` (FastAPI) | Localhost bridge | No (Secret Key required) |
| **Sential Frontend** | Container | Nginx Alpine | `3000` (HTTP) | Localhost bridge | No |
| **MongoDB 7.0** | Container | Official Mongo image | `27018:27017` | Localhost bridge | No |
| **Neo4j 5.20** | Container | Official Community | `7474`, `7687` | Localhost bridge | No (Internal auth) |
| **SpiderFoot** | Container / Fallback | Alpine Python 3.10 | `5001:5001` (REST) | Profile: `scanners` | No (API key optional for 3rd-party modules) |
| **theHarvester** | Worker Container / CLI | Isolated Worker | `5002:5002` (REST) | Profile: `scanners` | No (Uses crt.sh/DNS by default) |
| **Shodan** | Hybrid (Cloud / Adapter) | Embedded Client | Outbound HTTPS | Internet egress | Optional (`SHODAN_API_KEY` for full banners; InternetDB keyless) |
| **Google Dorks** | Safe Generator / RSS | Embedded Engine | Inbound/Outbound | News RSS / Analyst browser | No |
| **Maltego** | File Export / Transform | Python RFC-4180 | CSV Download | Local analyst desktop | Requires Maltego Desktop on analyst workstation |
| **ANPR / Vision** | Native Python / Container | OpenCV + Tesseract | Async Worker / Internal | In-process / Local | No |
| **OWASP ZAP** | Container | OWASP ZAP Stable | `8090:8080` (REST) | Profile: `scanners` | API Key configured via `.env` |

---

## 3. Quickstart & Deployment Steps

### Step 1: Environment Configuration
Copy `.env.example` to `.env` in the project root and configure production secrets:
```bash
cp .env.example .env
```
Ensure you generate a cryptographically strong 32-byte secret:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 2: Deploy Core Infrastructure
Launch the core database and application services:
```bash
docker compose up -d --build
```
This starts:
- `intelligence-mongodb` (port 27018)
- `intelligence-neo4j` (ports 7474 and 7687)
- `intelligence-backend` (port 8000)
- `intelligence-frontend` (port 3000)

Verify all core health checks:
```bash
docker compose ps
curl -s http://localhost:8000/health/ready | jq .
```

### Step 3: Deploy Local OSINT Scanners (Optional Profile)
To run SpiderFoot, theHarvester isolated worker, and OWASP ZAP locally:
```bash
docker compose --profile scanners up -d --build
```
This provisions:
- `spiderfoot` listening on `http://127.0.0.1:5001`
- `theharvester-worker` listening on `http://127.0.0.1:5002`
- `zap` dynamic application security scanner on `http://127.0.0.1:8090`

---

## 4. Operational Health Checks

The backend provides continuous observability endpoints:
- `GET /health/live` — Liveness probe (HTTP 200 if process alive).
- `GET /health/ready` — Readiness probe (validates MongoDB, Neo4j, and storage connectivity).
- `GET /api/v1/tools` — Lists all registered tool adapters and their runtime health states.
- `GET /api/v1/modules` — Lists all 6 intelligence modules (`osint`, `threat_intelligence`, `news_intelligence`, `social_media_intelligence`, `test_intelligence`, `example_intelligence`).

---

## 5. Security & Resource Controls

1. **Non-Root Execution**: Backend and worker containers execute as unprivileged user `sential` (UID 1000).
2. **Subprocess Isolation**: theHarvester runs in an isolated container via HTTP, preventing shell injection. Any fallback CLI execution uses `shell=False` and strict regex validation.
3. **SSRF Guard**: Video and RTSP stream ingest endpoints reject private IP ranges (RFC 1918, link-local, loopback).
4. **Media Storage**: Uploaded evidence files are restricted to 50MB for video and 15MB for images, stored in `/tmp/sential_footage` or persistent S3 storage with cryptographic hashes (SHA-256 + dHash).
