# Deployment Guide

## Docker Compose Deployment

The entire SaaS platform can be launched locally or in staging via Docker Compose:

```bash
docker-compose up -d --build
```

Services provisioned:
1. `postgres`: PostgreSQL 15 database instance with persistent volume `pgdata`.
2. `redis`: Redis 7 cache and async task queue with volume `redisdata`.
3. `backend`: FastAPI Python 3.10 production image on port `8000`.
4. `frontend`: High-performance Nginx production image serving static build on port `3000`.

## Production Checklist

* [x] Set strong random string for `SECRET_KEY`.
* [x] Enforce HTTPS termination via Reverse Proxy (Cloudflare / Traefik / Nginx).
* [x] Set realistic `SEARCH_JOB_TIMEOUT_SECONDS` (30s default).
* [x] Restrict `CORS_ORIGINS` to trusted enterprise domain names.
