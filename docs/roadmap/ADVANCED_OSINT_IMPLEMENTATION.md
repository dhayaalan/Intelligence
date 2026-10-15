# Advanced OSINT Implementation and Profile Extraction Architecture

## Overview
This document specifies the upgraded OSINT extraction engine, standardized profile contracts, field-level provenance, historical snapshotting, and operational status architecture implemented in `backend/app/modules/osint/`.

---

## 1. Separation of URL Discovery vs. Metadata Extraction

Prior architectures conflated discovering that a web URL existed with validating an account and extracting profile metadata. The upgraded Sential platform enforces an explicit 12-tier operational status enum (`ExtractionStatus`):

```
+-------------------------------------------------------------------------------+
|                       EXTRACTION STATUS TAXONOMY                              |
|                                                                               |
|  DISCOVERED          - Candidate URL generated from pattern or catalog        |
|  PROFILE_VALIDATED   - Confirmed live account (HTTP 200 without soft-404)     |
|  METADATA_EXTRACTED  - Bio, name, stats, and links parsed and verified        |
|  CONTENT_COLLECTED   - Public posts, repositories, or artifacts retrieved     |
|  PARTIAL_EXTRACTION  - Subset of fields retrieved; others blocked or failed   |
|  CONFIG_REQUIRED     - Provider requires API credentials / tokens             |
|  ACCESS_RESTRICTED   - Login wall, private account, or privacy boundary       |
|  RATE_LIMITED        - Upstream HTTP 429 encountered; backoff applied         |
|  UNAVAILABLE         - Upstream service down or network unreachable           |
|  PARSE_ERROR         - Upstream schema altered; parsing failed                |
|  NOT_FOUND           - Confirmed non-existent account (HTTP 404)              |
|  UNVERIFIED          - Probe returned ambiguous status                        |
+-------------------------------------------------------------------------------+
```

---

## 2. Standardized Profile Extraction Contract (`ProfileExtractionResult`)

Implemented in `backend/app/modules/osint/models.py`:

- **Identity & Platform:** `platform_id`, `platform_name`, `native_id`, `username`, `display_name`, `canonical_url`, `account_type`, `is_verified`.
- **Profile Metadata:** `bio`, `avatar_url`, `banner_url`, `website_urls`, `locale`, `location`, `category`, `account_created_at`, `account_updated_at`.
- **Public Account Statistics:** `PublicAccountStatistics` (`followers`, `following`, `post_count`, `subscribers`, `likes`, `repositories_count`, `stars`, `contributions`). Explicit `None` for unsupported or unextracted metrics; zero is only recorded when genuinely returned by the upstream provider.
- **Public Content Artifacts:** `ProfileArtifactItem` (`artifact_id`, `artifact_type`, `canonical_url`, `text_content`, `published_at`, `media_urls`, `engagement_metrics`).
- **Provenance & Verification:** `first_seen_at`, `last_seen_at`, `fetched_at`, `is_cached`, `source_endpoint`, `extraction_method`, `requested_region`, `observed_egress_route`, `fields_extracted`, `fields_unsupported`, `field_provenance` (with confidence and origin path), `errors`, `evidence_hash`.

---

## 3. Profile Snapshots and Historical Change Tracking

- **Service:** `backend/app/modules/osint/snapshot_service.py` (`ProfileSnapshotService`).
- **Storage:** MongoDB collection `osint_profile_snapshots`.
- **Endpoints:**
  - `POST /api/v1/tools/profile/refresh`: Forces on-demand collection, saves new snapshot, and calculates diff against prior state.
  - `GET /api/v1/tools/profile/history`: Retrieves versioned timeline of observations and field-level changes.
- **Diff Tracking:** Computes additions, deletions, and alterations across `bio`, `display_name`, `avatar_url`, `website_urls`, and numerical statistics.

---

## 4. Multi-Region Marketplace Intelligence

- **Provider:** `MarketplaceReconProvider` (`backend/app/modules/osint/providers/marketplace_recon.py`).
- **Regional Targets:**
  - `amazon_in`: Amazon India catalog (`amazon.in`) via `https://www.amazon.in/dp/{asin}` or product query.
  - `amazon_us`: Amazon US catalog (`amazon.com`) via `https://www.amazon.com/dp/{asin}` or product query.
- **Extracted Fields:** Product title, currency (INR vs. USD), canonical product URL, availability, and image URL. Zero hardcoded mock strings.
