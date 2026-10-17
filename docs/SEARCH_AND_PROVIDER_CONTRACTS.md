# Search and Provider Architecture Contracts

## 1. Overview and Design Principles

The Sentinel Intelligence platform operates on a single unified investigation pipeline that enforces strict source provenance, bounded recursive pivoting, and deterministic input classification. This document defines the shared normalized contracts connecting all intelligence modules, external providers, database repositories, and the frontend workspace.

---

## 2. Universal Input-to-Target Normalization Contract

Incoming investigator queries undergo deterministic classification prior to provider discovery:

| Target Type | Canonical Regex / Normalization Pattern | Validation Semantics |
| :--- | :--- | :--- |
| `PHONE` | E.164 (`^\+[1-9]\d{6,14}$`), digits-only normalization | Strict exact match. No fuzzy fallback if unmatched. |
| `EMAIL` | RFC 5322 lowercase, domain lowercasing | Strict exact match. Split into username and domain tokens for pivot. |
| `DOMAIN` | FQDN lowercased, port and protocol stripped | Domain passive DNS and WHOIS search. |
| `IP_ADDRESS` | IPv4 / IPv6 validation | Infrastructure reconnaissance. |
| `VEHICLE_PLATE` | Indian / US / International registration syntax | Strict format validation. Explicitly tagged unverified if no live registry. |
| `HASH` | MD5 (32 hex), SHA-1 (40 hex), SHA-256 (64 hex) | Cryptographic threat artifact matching. |
| `SOCIAL_URL` | Regex for known platforms (Twitter/X, LinkedIn, GitHub, YouTube) | Platform-specific profile/post extraction. |
| `IMAGE_ARTIFACT` | Image file upload with OCR extraction | Reverse image and artifact lookup. |
| `KEYWORD` | Natural language text query | Global multi-engine keyword search. |

---

## 3. Provider Capabilities and Truthful Execution States

Every module and external adapter must report one of the following truthful lifecycle states:

- `PENDING`: Scheduled for execution within the bounded job pool.
- `RUNNING`: Actively querying external or internal provider APIs.
- `SUCCESS_WITH_RESULTS`: Execution completed and returned verified records.
- `SUCCESS_NO_RESULTS`: Execution completed cleanly; zero records matched the target.
- `CONFIG_REQUIRED`: Required API keys or upstream credentials are absent in the current environment.
- `RESTRICTED`: The authenticated tenant/user does not have entitlements for this provider.
- `FAILED`: Network timeout, HTTP 5xx error, or rate limit exhausted. Fault-isolated; never crashes parent pipeline.
- `SKIPPED`: Excluded by bounded pivot depth or relevance filter.

Under no circumstances does the platform report `SUCCESS` or claim external verification when a provider failed or was not configured.

---

## 4. Shared Normalized Result Envelope (`SearchResponse`)

```json
{
  "search_id": "string (UUID)",
  "query": "string (original input)",
  "target_type": "string (canonical classification)",
  "status": "completed | partial | failed",
  "investigation_id": "string (auto-linked investigation case)",
  "module_jobs": [
    {
      "module": "string",
      "status": "completed | partial | failed",
      "duration_ms": "integer",
      "records_count": "integer",
      "error": "string | null"
    }
  ],
  "entities": [
    {
      "id": "string",
      "type": "string",
      "value": "string",
      "confidence": "float (0.0 - 1.0)",
      "sources": ["string"],
      "first_seen": "ISO-8601 string",
      "last_seen": "ISO-8601 string",
      "metadata": "object"
    }
  ],
  "relationships": [
    {
      "source_id": "string",
      "target_id": "string",
      "relationship_type": "string",
      "confidence": "float (0.0 - 1.0)",
      "evidence_ids": ["string"]
    }
  ],
  "evidence": [
    {
      "provider": "string",
      "source": "string",
      "reference": "string",
      "timestamp": "ISO-8601 string",
      "hash": "SHA-256 string",
      "raw_data": "object | string"
    }
  ],
  "media": [
    {
      "id": "string",
      "media_type": "image | video",
      "url": "string (validated URL)",
      "thumbnail_url": "string | null",
      "title": "string | null",
      "description": "string | null",
      "source_provider": "string",
      "source_platform": "string | null",
      "parent_id": "string | null",
      "parent_type": "string | null",
      "parent_title": "string | null",
      "publication_date": "ISO-8601 string | null",
      "collection_date": "ISO-8601 string",
      "verification_status": "string",
      "canonical_source_url": "string | null",
      "provenance": "string",
      "evidence_ids": ["string"]
    }
  ],
  "stats": {
    "total_duration_ms": "integer",
    "modules_executed": "integer",
    "entities_count": "integer",
    "relationships_count": "integer",
    "evidence_count": "integer"
  }
}
```

---

## 5. Media Normalization Contract

All visual artifacts discovered across OSINT, news, threat intel, and social media collectors are normalized into `MediaRecord` instances by `MediaNormalizationPipeline`.

- **Images**: Extracted from entity avatars, news article hero images, social post attachments, and reverse-image hits.
- **Videos**: Extracted from YouTube search results, video broadcasts, and verified social media video URLs.
- **Provenance Linkage**: Each media record retains its exact parent entity/article/evidence ID and source provider URL.
