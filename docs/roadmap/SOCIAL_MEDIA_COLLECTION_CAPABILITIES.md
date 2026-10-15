# Social Media Intelligence Collection Capabilities

## 1. Overview
The Social Media Intelligence module orchestrates resilient multi-platform collection across public decentralized and centralized social networks. All operations enforce rate-limit detection, automated jittered backoff, circuit-breaker isolation, and zero-fake-data honesty.

---

## 2. Platform Capabilities & Access Models

| Platform | Access Model | Target Support | Pagination & Rate Limiting | Extraction Fidelity |
|---|---|---|---|---|
| **Bluesky** | Public XRPC Directory (`public.api.bsky.app`) | Keyword searches, Author feeds | Cursor-based continuation; HTTP 429 adaptive backoff | Full posts, avatars, handles, timestamps, likes, reposts |
| **Telegram** | Public Web Preview (`t.me/s/{channel}`) | Public broadcast channels | Message ID stepping; Anti-scraping detection | Factual messages, view counts, forward references |
| **Reddit** | Public JSON Endpoints (`reddit.com/search.json`) | Subreddits, post queries, user overviews | `after` token pagination; Strict 1 req/sec pacing | Post titles, selftext, upvotes, comment counts |
| **Mastodon** | Decentralized Public REST API (`mastodon.social/api/v2/search`) | Public fediverse statuses, tags | ID-based cursors; Rate-limit headers inspected | Status content, account avatars, boosts, favorites |
| **YouTube** | Public Ingestion & Subtitle Extractor | Video IDs, URLs, query searches | Safe metadata extraction; VTT caption parsing | Title, description, view/like metrics, time-stamped subtitles |
| **Instagram** | Meta Graph API (`/v18.0/ig_hashtag_search`) + Public OG Resolver | Public post permalinks, authorized business hashtags | Requires `INSTAGRAM_ACCESS_TOKEN` for API; Public OpenGraph resolver for URLs | Captions, likes, media URLs, timestamps; `CONFIG_REQUIRED` when unauthenticated |
| **Facebook** | Meta Graph API (`/v18.0/{page_id}/feed`) + Public OG Resolver | Public page feeds, public post permalinks | Requires `FACEBOOK_ACCESS_TOKEN` for API; Public OpenGraph resolver for URLs | Page messages, permalinks, shares, media; `CONFIG_REQUIRED` when unauthenticated |

---

## 3. Lawful Access and OPSEC Enforcement
- **No Login-Wall Bypasses**: The platform never employs credentials or headless browser hacks to breach private user accounts or restricted groups.
- **Fail-Closed Reporting**: When an access token is absent, the platform records `CONFIG_REQUIRED` rather than fabricating simulated posts or silently failing.
- **Input Validation**: Empty queries or missing target parameters abort cleanly with empty results rather than selecting random channels.
