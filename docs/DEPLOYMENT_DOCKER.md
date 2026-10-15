# Sential Intelligence Platform — Docker Deployment Guide

This guide documents how to build, run, test, and manage the complete Sential Intelligence Platform container stack using Docker Compose.

---

## 1. System Prerequisites

Before launching the platform, verify that the host machine satisfies:

- **Operating System:** Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+), macOS, or Windows WSL2
- **Docker Engine:** `v24.0.0` or higher (`docker --version`)
- **Docker Compose:** `v2.20.0` or higher (`docker compose version`)
- **System Memory:** Minimum 4 GB RAM (8 GB recommended for concurrent multi-module OSINT/CTI analysis)
- **Disk Space:** 10 GB free disk space for Docker images, build caches, and MongoDB persistence

---

## 2. Architecture & Service Topology

The application stack communicates across an isolated Docker bridge network (`intelligence-network`):

```
                                  [ Host Browser ]
                                         │
                         ┌───────────────┴───────────────┐
                         │                               │
                HTTP :3000 (UI / Assets)        HTTP :3000/api/v1/ (Reverse Proxy)
                         │                               │
                         ▼                               │
               ┌───────────────────┐                     │
               │ frontend (Nginx)  │─────────────────────┘
               │  SPA Static Files │
               └───────────────────┘
                         │
              proxy_pass http://backend:8000/api/
                         │
                         ▼
               ┌───────────────────┐
               │  backend (FastAPI)│
               │  Python 3.10 Non-Root
               └───────────────────┘
                         │
                         │ Motor / PyMongo (mongodb:27017)
                         ▼
               ┌───────────────────┐
               │ mongodb (Mongo 7) │
               │ Named Volume Data │
               └───────────────────┘
```

### Core vs. Supporting Services

| Service Name | Container Name | Role | Status | Host Port | Internal Port |
|---|---|---|---|---|---|
| **`frontend`** | `intelligence-frontend` | Nginx web server, SPA routing, reverse proxy | **Core (Mandatory)** | `3000` | `80` |
| **`backend`** | `intelligence-backend` | FastAPI intelligence engine (non-root `sential`) | **Core (Mandatory)** | `127.0.0.1:8000` | `8000` |
| **`mongodb`** | `intelligence-mongodb` | Document persistence & collection indexing | **Core (Mandatory)** | `127.0.0.1:27018` | `27017` |
| **`redis`** | `intelligence-redis` | Message broker & cache (Profile: `supporting`) | *Optional* | `127.0.0.1:6380` | `6379` |
| **`minio`** | `intelligence-minio` | S3 object store (Profile: `supporting`) | *Optional* | `127.0.0.1:9002` | `9000` |
| **`zap`** | `intelligence-zap` | Dynamic web scanner (Profile: `scanners`) | *Optional* | `127.0.0.1:8091` | `8090` |

> [!NOTE]
> In the current implementation, evidence records and audit trails are persisted directly to MongoDB (`evidence` collection) and background execution is managed via asynchronous in-process tasks. `redis` and `minio` are architectural placeholders for future distributed multi-worker architectures and are activated on-demand via Compose profiles.

---

## 3. Environment Configuration

### Step 1: Initialize `.env` from Example

The platform uses a root `.env` file that is excluded from Git to protect secrets:

```bash
cp .env.docker.example .env
```

### Step 2: Configure Environment Variables

Open `.env` and configure:

```bash
# Application Environment
APP_ENV=production
APP_NAME="Sential Intelligence Platform"

# Generate a 256-bit signing secret: openssl rand -hex 32
SECRET_KEY=generate-a-strong-hex-key-here

# MongoDB Connection
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DATABASE=sential_db
MONGODB_HOST_PORT=27018

# Host Port Bindings
FRONTEND_PORT=3000
BACKEND_PORT=8000

# Engine Execution Limits
SEARCH_JOB_TIMEOUT_SECONDS=60
PROVIDER_TIMEOUT_SECONDS=10

# Optional External ML Microservice (Operated by separate ML team)
ML_SERVICE_URL=
ML_SERVICE_API_KEY=
```

---

## 4. Launching the Platform

### Validate Configuration

Verify syntax and variable interpolation without starting containers:

```bash
docker compose config --quiet
```

### Build & Start Core Stack

To build and launch the core stack (`mongodb`, `backend`, `frontend`) in detached mode:

```bash
docker compose build
docker compose up -d
```

### Monitor Container Health

Check container status and healthchecks:

```bash
docker compose ps
```

Expected status:
```text
NAME                    IMAGE                   COMMAND                  SERVICE    STATUS
intelligence-backend    intelligence-backend    "uvicorn app.main:ap…"   backend    Up (healthy)
intelligence-frontend   intelligence-frontend   "nginx -g 'daemon of…"   frontend   Up (healthy)
intelligence-mongodb    mongo:7.0               "docker-entrypoint.s…"   mongodb    Up (healthy)
```

---

## 5. Starting Optional Profiles

### Supporting Infrastructure (Redis & MinIO)

If external task workers or S3-compatible vault testing is required:

```bash
docker compose --profile supporting up -d
```

### Dynamic Vulnerability Scanners (OWASP ZAP)

To spin up isolated containerized scanners:

```bash
docker compose --profile scanners up -d
```

---

## 6. Access Endpoints

Once the containers report `healthy`:

- **Investigator UI:** [http://localhost:3000](http://localhost:3000)
- **Interactive OpenAPI Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Direct Backend OpenAPI Schema:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- **Platform Healthcheck:** [http://localhost:8000/health](http://localhost:8000/health)
- **Liveness Probe:** [http://localhost:8000/health/liveness](http://localhost:8000/health/liveness)
- **Readiness Probe:** [http://localhost:8000/health/readiness](http://localhost:8000/health/readiness)
- **Frontend Container Health:** [http://localhost:3000/health](http://localhost:3000/health)
- **Nginx API Reverse Proxy Test:** [http://localhost:3000/api/v1/tools](http://localhost:3000/api/v1/tools)

---

## 7. Operating & Maintenance Commands

### Viewing Logs

Stream aggregated logs across all running containers:
```bash
docker compose logs -f
```

Inspect specific service logs with timestamps:
```bash
docker compose logs -f --tail=100 backend
docker compose logs -f --tail=100 frontend
docker compose logs -f --tail=100 mongodb
```

### Restarting Services

```bash
# Restart a single service (e.g. backend after configuration changes)
docker compose restart backend

# Restart the entire stack
docker compose restart
```

### Rebuilding After Code Changes

When source code in `backend/` or `frontend/src/` is updated:

```bash
docker compose build
docker compose up -d
```

### Stopping the Stack (Safe Persistence)

To stop running containers while **preserving all MongoDB data volumes**:

```bash
docker compose down
```

> [!CAUTION]
> **NEVER** run `docker compose down -v` on production or investigator environments. The `-v` flag permanently destroys the `intelligence_mongodb_data` volume containing investigations, cases, and cryptographic evidence hashes.

---

## 8. Backup & Restore Data

### Backing Up MongoDB Data

```bash
# Execute mongodump directly inside the running container
docker compose exec -T mongodb mongodump --db sential_db --archive > ./backup_sential_db_$(date +%Y%m%d).archive
```

### Restoring MongoDB Data

```bash
# Restore an archived database backup
cat ./backup_sential_db_YYYYMMDD.archive | docker compose exec -T mongodb mongorestore --db sential_db --archive
```

---

## 9. Troubleshooting & Diagnostics

### Problem: Backend Container Fails Healthcheck

1. Inspect backend logs:
   ```bash
   docker compose logs backend --tail=100
   ```
2. Verify MongoDB readiness:
   ```bash
   docker compose exec mongodb mongosh --eval "db.adminCommand('ping')"
   ```
3. Test backend readiness endpoint directly:
   ```bash
   curl -i http://localhost:8000/health/readiness
   ```

### Problem: Frontend Returns 502 Bad Gateway on API Calls

1. Check that the backend container is healthy:
   ```bash
   docker compose ps backend
   ```
2. Verify internal DNS resolution between Nginx and Backend:
   ```bash
   docker compose exec frontend ping -c 2 backend
   ```
3. Check Nginx error logs:
   ```bash
   docker compose logs frontend --tail=50
   ```

### Problem: Host Port Conflict (e.g. Port 27017 or 6379 already in use)

The `docker-compose.yml` binds MongoDB to host port `27018` by default (`MONGODB_HOST_PORT=27018`) to prevent collision with any existing host MongoDB daemon running on `27017`. If port `3000` or `8000` is occupied, change `FRONTEND_PORT` or `BACKEND_PORT` in your `.env` file without modifying application source code.
