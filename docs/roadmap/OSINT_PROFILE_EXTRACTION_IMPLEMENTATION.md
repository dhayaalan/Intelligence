# OSINT Profile Extraction Implementation Guide

## 1. Executive Summary
This document outlines the architecture, implementation patterns, and capability distinctions for OSINT Profile Extraction in the Sential Intelligence Platform. 

Previously, candidate username enumeration relied heavily on HTTP 200 presence checks, frequently applying synthetic placeholder icons (via unavatar.io and DiceBear) and misrepresenting URL discovery as enriched intelligence. The upgraded system strictly separates:
1. **Candidate Discovery (`DISCOVERED`)**: A possible URL pattern exists.
2. **Profile Existence Validation (`PROFILE_VALIDATED`)**: Remote endpoint returned HTTP 200/302 or confirmed the account handle exists on the network, without metadata parsing.
3. **Rich Metadata Extraction (`METADATA_EXTRACTED` / `PARTIAL_EXTRACTION`)**: Authentic JSON-LD, OpenGraph, or official REST API fields (bio, real profile avatar, joined date, follower metrics) were parsed and validated.

---

## 2. Supported Metadata Fields by Extraction Tier

### Tier 1: Official / Public REST JSON APIs
Platforms: GitHub, GitLab, Bluesky, Dev.to, HackerNews, Chess.com, Lichess, Codeberg, DockerHub, Speedrun.com, Reddit.
- **Identity**: Native platform ID, username, display name, verified status.
- **Biographical**: Bio, description, about text, location, website/blog links.
- **Images**: Authentic CDN-hosted avatar URLs (no synthetic fallbacks).
- **Temporal**: Account creation timestamp, last updated timestamp.
- **Statistics**: Followers, following, public repositories/gists, post/karma counts.

### Tier 2: Public Structured HTML / OpenGraph
Platforms: Steam, Medium, Substack, Twitch, YouTube, Linktree, Patreon.
- **Identity**: Cleaned `<title>` or `og:title` display names.
- **Biographical**: `<meta name="description">` or `og:description` summaries (excluding cookie/login boilerplate).
- **Images**: `og:image` or `twitter:image` only when pointing to non-placeholder user assets.

### Tier 3: Probe / Validation Only
Platforms: Static forums, gaming leaderboards, directory websites without public APIs.
- **Capability**: Confirms existence via status code and absence of 404 keywords.
- **Output**: Reports `PROFILE_VALIDATED` with `is_metadata_extracted: False`.

---

## 3. Provenance & Anti-Fabrication Principles
1. **No Synthetic Zeroes**: If a platform does not provide a follower count, the field is `None`, not `0`.
2. **No Fallback Avatars**: Synthetic avatars are prohibited from being saved as extracted evidence.
3. **Field Provenance**: Every extracted field is tagged with:
   - `source_provider`
   - `source_path` (e.g. `json.bio` vs `html.og:description`)
   - `is_inferred` (`False` for structured APIs, `True` for heuristic HTML tags)
   - `observed_at` (UTC timestamp)
   - `confidence` (0.0 to 1.0)
