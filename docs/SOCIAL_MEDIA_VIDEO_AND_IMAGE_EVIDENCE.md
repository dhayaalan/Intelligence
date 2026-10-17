# Sential Intelligence — Social Media, Video, and Image Evidence Architecture

**Document Version**: 2.0.0  
**Date**: October 17, 2026  
**Status**: Realization Complete & Verified  

---

## 1. Social Media Evidence Model

Every social post extracted across Bluesky, YouTube, Telegram, Reddit, and Mastodon conforms to the universal schema:

```json
{
  "id": "yt_dQw4w9WgXcQ",
  "platform": "YOUTUBE",
  "author": "RickAstleyVEVO",
  "author_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
  "text": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
  "created_at": "2009-10-25T06:57:33Z",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "views_count": 1400000000,
  "likes_count": 16000000,
  "media_urls": [
    "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
  ],
  "channel_name": "RickAstleyVEVO",
  "entities": ["Rick Astley", "Music"],
  "credibility_score": null
}
```

---

## 2. Key Media Integrity Guarantees

1. **Per-Post Media Association**:
   Each thumbnail and image is strictly bound to its parent post via `media_urls`. The frontend and backend never reuse an image from one post for another, nor do they assume that a post thumbnail represents the account owner's personal portrait.
2. **Authentic Timestamps**:
   Publication timestamps (`created_at`) reflect actual observation or upload timestamps from the platform API. When a timestamp is unavailable, it is preserved as `null` or formatted as `Date unavailable` in the UI—never synthesized using `datetime.utcnow()`.
3. **Temporal Filtering**:
   The investigation workspace supports temporal filtering for:
   - Last 7 days
   - Last 30 days
   - Last 3 months
   - Last 6 months
   - Last 12 months
   - Last 3 years
   - Last 5 years
   - Custom date range
4. **YouTube Video & Channel Evidence**:
   - Resolves canonical video IDs from watch URLs, short links, or direct IDs.
   - Queries official YouTube Data API when configured, or resolves authentic oEmbed metadata.
   - If transcripts are unavailable, marks status as `TRANSCRIPT_UNAVAILABLE` rather than hallucinating transcript dialogue.
   - A channel is attributed to a person only when corroborated by cryptographic, biographical, or official verified link evidence.

