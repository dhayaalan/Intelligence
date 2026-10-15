# Normalized OSINT Profile Metadata Schema

## Overview
This document specifies the standard schema, field-level provenance model, and state lifecycle for OSINT profile extraction in the Sential Intelligence Platform. It eliminates the conflation of simple HTTP 200 URL availability with verified metadata extraction.

---

## 1. Extraction Statuses

The platform enforces 12 distinct extraction states:

| Status Code | Description | Criteria |
|---|---|---|
| `DISCOVERED` | Candidate URL or account handle located | URL template generated or handle candidate found, but profile existence not verified. |
| `PROFILE_VALIDATED` | Profile existence confirmed | Remote endpoint responded indicating profile existence (e.g., HTTP 200 on profile page), but no structured metadata was parsed. |
| `METADATA_EXTRACTED` | Profile attributes parsed and normalized | Verified attributes (bio, real avatar, display name, follower counts, creation dates) were extracted from JSON/HTML. |
| `CONTENT_COLLECTED` | Public posts or artifacts collected | Public posts, repositories, or artifacts were successfully retrieved and normalized. |
| `PARTIAL_EXTRACTION` | Partial metadata retrieved | Some supported fields were extracted, while other supported fields were inaccessible or empty. |
| `CONFIG_REQUIRED` | Authentication/API key required | Platform requires credentials (e.g., official Graph API tokens, Amazon PA-API, Twitter Bearer) that are not configured. |
| `ACCESS_RESTRICTED` | Protected/Private content | Account is private, protected, or restricted by platform policy. |
| `RATE_LIMITED` | Rate limit or quota exhausted | HTTP 429 or provider rate limit threshold was triggered. |
| `UNAVAILABLE` | Source offline or unreachable | Network timeout, DNS failure, or HTTP 5xx error. |
| `PARSE_ERROR` | Malformed response payload | Endpoint returned invalid JSON or unparseable HTML structure. |
| `NOT_FOUND` | Profile confirmed nonexistent | Platform explicitly returned HTTP 404 or recognized "user not found" keyword signature. |
| `UNVERIFIED` | Ambiguous or inconclusive result | Response does not provide sufficient certainty to declare existence or absence. |

---

## 2. Core Profile Entity Schema

```json
{
  "platform_id": "github",
  "platform_name": "GitHub",
  "native_id": "583231",
  "username": "octocat",
  "display_name": "The Octocat",
  "canonical_url": "https://github.com/octocat",
  "submitted_url": "https://github.com/octocat",
  "account_type": "User",
  "is_verified": true,
  "bio": "Monalisa Octocat living in the cloud.",
  "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4",
  "banner_url": null,
  "website_urls": ["https://octocat.github.io"],
  "locale": null,
  "location": "San Francisco, CA",
  "category": "Developer & Tech",
  "account_created_at": "2011-01-25T18:44:36Z",
  "account_updated_at": "2024-03-12T12:00:00Z",
  "statistics": {
    "followers": 14200,
    "following": 9,
    "post_count": null,
    "subscribers": null,
    "likes": null,
    "repositories_count": 8,
    "stars": null,
    "contributions": null,
    "custom_metrics": {
      "public_gists": 8
    }
  },
  "artifacts": [
    {
      "artifact_id": "repo_1296269",
      "artifact_type": "repository",
      "canonical_url": "https://github.com/octocat/Hello-World",
      "text_content": "My first repository on GitHub!",
      "published_at": "2011-01-26T19:01:12Z",
      "media_urls": [],
      "attachment_types": [],
      "engagement_metrics": {
        "stars": 2400,
        "forks": 1800
      }
    }
  ],
  "status": "METADATA_EXTRACTED",
  "first_seen_at": "2026-10-15T06:00:00Z",
  "last_seen_at": "2026-10-15T06:00:00Z",
  "fetched_at": "2026-10-15T06:00:00Z",
  "is_cached": false,
  "source_endpoint": "https://api.github.com/users/octocat",
  "extraction_method": "JSON_REST_API",
  "requested_region": null,
  "observed_egress_route": "DIRECT",
  "fields_extracted": ["display_name", "bio", "avatar_url", "location", "website_urls", "followers", "repositories_count"],
  "fields_unsupported": ["banner_url", "subscribers"],
  "field_provenance": {
    "bio": {
      "field_name": "bio",
      "value": "Monalisa Octocat living in the cloud.",
      "source_provider": "osint_github",
      "source_path": "$.bio",
      "is_inferred": false,
      "observed_at": "2026-10-15T06:00:00Z",
      "confidence": 0.99
    }
  },
  "errors": [],
  "evidence_hash": "a1b2c3d4..."
}
```

---

## 3. Freshness & Snapshot Model

To support change detection over time:
- Each profile fetch compares current attributes against the previous snapshot in `profile_snapshots` collection.
- Any changed field emits a `ProfileChangeRecord` specifying `field_name`, `previous_value`, `new_value`, and `observed_at`.
- Unchanged fetches do not generate redundant snapshot copies.
