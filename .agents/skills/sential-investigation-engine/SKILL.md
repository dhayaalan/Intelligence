---
name: sential-investigation-engine
description: Maintains the Sential Intelligence investigation architecture, source provenance, clue-to-clue orchestration, media extraction, authorized vehicle evidence, geospatial records, and investigator experience.
---

# Sential Intelligence Investigation Engine & Architecture Guide

This skill governs engineering workflows, architectural boundaries, and operational guidelines for the Sential Intelligence Platform (`/home/songoku/Pictures/Intelligence`).

---

## 1. Core Principles & Forensic Truthfulness

1. **Defensible Source Provenance**:
   - Every entity, claim, media item, sighting, and relationship must trace back to a verifiable source or evidence ID.
   - Never fabricate data, subscriber identities, owner names, locations, video transcripts, or verification scores.
   - If an integration lacks credentials or authorization, report `CONFIG_REQUIRED` or `AUTHORIZATION_REQUIRED` rather than simulating a successful lookup.

2. **Epistemic Boundaries**:
   - Phone numbering-plan metadata (carrier/circle) is **not** subscriber identity.
   - Vehicle registration plate syntax/jurisdiction is **not** a live registration lookup and **not** a physical location.
   - Matching usernames across platforms are hypotheses, not verified cross-platform identity links.
   - A camera location or sighting is **not** vehicle GPS telemetry or proof of driver identity.

3. **Security, Privacy & Authorization**:
   - Strictly prohibit arbitrary port/IP scanning, guessing RTSP endpoints, or enumerating unsecured cameras.
   - Camera feeds and footage must originate exclusively from official open-data catalogs, published APIs, or explicitly authorized investigator uploads.
   - All external media fetches, URLs, and feeds must strictly pass `is_safe_media_url` and SSRF validation (blocking `127.0.0.1`, RFC1918, link-local `169.254.169.254`, and cloud metadata).

---

## 2. Universal Investigation Workflow

The investigation engine operates through a single, unified clue-to-clue pipeline:

```
[Clue Input] ──> [Target Validation & Normalization]
                     │
                     ▼
                 [Provider Routing & Permission Check]
                     │
                     ▼
                 [Parallel Provider Execution]
                     │
                     ▼
                 [Result & Evidence Normalization]
                     │
                     ▼
                 [Entity & Media Extraction]
                     │
                     ▼
                 [Persistent Storage (Mongo + Neo4j)]
                     │
                     ▼
                 [Bounded Pivot Discovery & Execution]
```

### Bounded Pivoting & Limits
- **Depth**: Maximum 2 recursive hops by default.
- **Deduplication**: Idempotency keys based on `(investigation_id, target_type, target_value)`.
- **Parent-Child Discovery**: Preserve exact intermediate evidence chains rather than directly linking every secondary clue to the root anchor.

---

## 3. Vehicle & Camera Intelligence Standards

### Vehicle Registration
- Syntax & format validation determines jurisdictional authority (e.g., state/RTO codes for Indian plates).
- Live VAHAN/mParivahan queries require active authorized credentials. In their absence, clearly display `CONFIG_REQUIRED`.
- Never present registration jurisdiction as a physical vehicle location.

### Camera Evidence & ANPR
- **Ingestion**: Validate format, duration, codec, file size, hash, and case authorization before processing.
- **ANPR Pipeline**:
  1. Frame sampling at bounded intervals (e.g., 1 frame per second).
  2. Vehicle and license-plate candidate localization.
  3. OCR extraction with confidence scoring.
  4. Jurisdiction-aware plate normalization.
  5. Candidate matching against target with explicit states:
     - `NO_MATCH`
     - `POSSIBLE_MATCH`
     - `CANDIDATE_MATCH`
     - `HUMAN_CONFIRMED`
     - `HUMAN_REJECTED`
     - `INCONCLUSIVE`
- **Location & Timeline**:
  - Store discrete camera observations with camera ID, coordinates (if published), timecode, timestamp, and review state.
  - Never fabricate a continuous route from disconnected camera detections.

---

## 4. First-Class Media Pipeline

- Images and Videos must be exposed immediately on every search and saved investigation.
- Media items persist in MongoDB (`record.media`) and synchronize with Neo4j.
- Supported media: profile avatars, news hero images, authentic YouTube video thumbnails, and YouTube community post attachments (`backstageImageRenderer`).

---

## 5. Investigator UI Navigation Standard

Keep primary sidebar navigation strictly focused:
1. **Search** (`/search`)
2. **Investigations** (`/investigations`)

Within search results and investigation details, maintain the 8 core unified sections:
- **Overview**
- **All Results**
- **Profiles**
- **Images**
- **Videos**
- **News & Intelligence**
- **Locations & Timeline**
- **Relationships & Evidence**

---

## 6. Testing & Quality Requirements

Before merging any changes:
- Run backend pytest suites (`pytest tests/`).
- Run frontend type check (`npm --prefix frontend run typecheck`).
- Run frontend production build (`npm --prefix frontend run build`).
- Verify tenant isolation, scoped graph queries, and zero data leakage across cases.
