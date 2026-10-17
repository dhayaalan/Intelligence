# Social Media & Video Intelligence Data Integrity

## 1. Overview & Data Integrity Remediation

Social media and video intelligence must adhere to authentic forensic evidence standards. Presenting generated placeholder text as real subtitles or substituting collection time for publication time degrades investigator trust.

This document details the remediations implemented across the `social_media_intelligence` module collectors.

---

## 2. YouTube Video Intelligence Remediation

### 2.1 Elimination of Synthetic Subtitles & Transcripts
- **Previous Defect**: When video closed captions were unavailable, the collector generated a synthetic subtitle segment (`"Official broadcast recording for video item..."`) and marked it as a verified transcript track.
- **Remediation**: The synthetic generator was completely removed. When authentic subtitles cannot be extracted, the subtitle track truthfully reports `TRANSCRIPT_UNAVAILABLE`.
- **Integrity Rule**: Never fabricate spoken words or closed captions. If a transcript cannot be retrieved, the limitation must be clearly visible to the investigator.

### 2.2 Publication Date vs. Collection Timestamp
- **Previous Defect**: The collector set `published_at = datetime.utcnow()`, claiming the video was published at the exact second the platform scraped or queried it.
- **Remediation**: The collector extracts the authentic publication timestamp from YouTube page microdata (`<meta itemprop="datePublished">` or `<meta itemprop="uploadDate">`). The extraction timestamp is stored separately as `collected_at`.

### 2.3 Channel ID Resolution
- **Previous Defect**: The channel ID was derived via regex over author display name strings (e.g., `re.sub(r'[^a-zA-Z0-9]', '', author_name)`), producing fabricated channel IDs.
- **Remediation**: The channel ID is extracted from canonical URLs (`<link itemprop="url" href=".../channel/UC...">`) or schema microdata. If unavailable, it remains `None` rather than inventing an ID.

### 2.4 Metrics & Interaction Counts
- View counts, likes, and comment counts reflect genuine numbers from API or microdata responses. When unavailable, fields remain `None` and are never backfilled with plausible-looking synthetic figures.

---

## 3. Meta Graph API Migration (Facebook & Instagram)

### 3.1 Migration from Obsolete v18.0 to v21.0
- **Audit Finding**: Facebook and Instagram collectors were hardcoded to `v18.0` of the Meta Graph API, which reached end-of-life deprecation.
- **Remediation**: Migrated endpoints to configurable `META_GRAPH_API_VERSION`, defaulting to current supported `v21.0`:
  - `https://graph.facebook.com/{META_GRAPH_API_VERSION}/...`
  - Access tokens and query rate limits are validated with exponential backoff.
- **Truthful Status**: When valid `FACEBOOK_ACCESS_TOKEN` or `INSTAGRAM_ACCESS_TOKEN` is unconfigured, collectors truthfully return `CONFIG_REQUIRED` or `AUTH_REQUIRED` rather than reporting false empty success.

---

## 4. Platform Data Extraction Boundaries

| Platform | Authorized Collection Scope | Prohibited Actions | Truthful Failure State |
| :--- | :--- | :--- | :--- |
| **YouTube** | Public video metadata, thumbnails, official caption tracks, public comments. | Bypassing age gates; synthetic subtitle generation. | `TRANSCRIPT_UNAVAILABLE` |
| **Reddit** | Public subreddit posts, public thread comments, author handles. | Private subreddit scraping; banned account evasion. | `RESTRICTED` |
| **Telegram** | Public channel messages via MTProto/Bot API. | Private group infiltration; phone number scraping without consent. | `AUTH_REQUIRED` |
| **Mastodon / Bluesky** | Public AT Protocol / ActivityPub fediverse posts, author handles. | Private direct messages; unauthorized firehose dumping. | `SUCCESS_EMPTY` |
| **Instagram / Facebook** | Public business pages, public media posts via Meta Graph API v21.0. | Private profile scraping; CAPTCHA evasion; credential stuffing. | `CONFIG_REQUIRED` |
