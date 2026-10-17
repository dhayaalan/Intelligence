# Sential Intelligence — Provider Capabilities, Authentication & Access Terms

**Document Version**: 2.0.0  
**Date**: October 17, 2026  
**Status**: Audited and Operational  

---

## 1. Provider Capabilities & Access Classification

| Module | Provider ID | Target Type | Access Mode | Auth / Credential Required | Public / Authorized Scope | Operational State |
|---|---|---|---|---|---|---|
| **OSINT** | `telecom_intelligence` | `phone` | Public ITU-T / Optional Subscriber API | None for ITU-T; `NUMVERIFY_API_KEY` / `TWILIO_LOOKUP_API_KEY` for live subscriber | Public numbering plan; carrier allocation | Operational (Carrier/Jurisdiction). Live subscriber reports `CONFIG_REQUIRED` when key absent. |
| **OSINT** | `username_recon` | `username` | Public Web Probers (WhatsMyName, Sherlock) | None | Public account profile presence across 352 platforms | Operational. |
| **OSINT** | `vehicle_intelligence` | `vehicle`, `vehicle_plate` | Regex + Regional Transport Registry Mapping | None for syntax/RTO; Gov API key for live ownership | Public administrative RTO mapping | Operational. RTO attribution active; personal owner never fabricated. |
| **OSINT** | `theharvester` | `domain` | Search Engine Harvester | Optional Search API keys | Public search engine results | Operational. |
| **OSINT** | `spiderfoot` | `domain`, `ip` | Open-Source Recon Framework | Optional Threat Feeds | Public OSINT sources | Operational. |
| **Threat Intelligence** | `passive_dns` | `domain`, `ip` | Passive DNS Feeds / Resolvers | None | Public DNS records & historical resolutions | Operational. |
| **Threat Intelligence** | `cert_transparency` | `domain` | crt.sh / Public CT Logs | None | Public TLS Certificate Transparency | Operational. |
| **Threat Intelligence** | `shodan_recon` | `ip`, `domain` | Shodan Internet Scanner API | `SHODAN_API_KEY` | Public banner data | Operational when key configured; graceful fallback. |
| **Threat Intelligence** | `urlscan_prober` | `url`, `domain` | urlscan.io Public API | `URLSCAN_API_KEY` (optional) | Public website scans | Operational. |
| **Social Media** | `youtube` | `username`, `keyword`, `video_id` | YouTube oEmbed & Official Data API v3 | `YOUTUBE_API_KEY` (optional) | Public video metadata, channels, thumbnails | Operational. Strict zero synthetic transcripts. |
| **Social Media** | `bluesky` | `username`, `keyword` | AT Protocol Public API | None | Public posts, author profiles, timestamps | Operational. |
| **Social Media** | `telegram` | `username`, `channel` | Public Channel Web Preview | None | Public broadcast channel messages | Operational. |
| **Social Media** | `reddit` | `username`, `subreddit`, `keyword` | Public JSON API | Optional Reddit API client | Public posts and threads | Operational. |
| **Social Media** | `mastodon` | `username`, `instance` | ActivityPub Public API | None | Public federated statuses | Operational. |
| **News Intelligence** | `news_search_engine` | `keyword`, `entity`, `location` | Global Wire Feeds & RSS Aggregation | Optional News API keys | Public news publications, articles, wire stories | Operational. Disambiguation active. |
| **Geo Intelligence** | `geo_service` | `location`, `coordinates`, `file` | Ingestion (CSV, GeoJSON, GPX, KML) | None | Authorized personal/case location files | Operational. Strict coordinate boundary & temporal window enforcement. |

---

## 2. Epistemic Verification and Ethical Safeguards

1. **Lawful Subscriber Safeguard**:
   ITU-T E.164 telecommunications plan validation establishes carrier allocation and regional jurisdiction. It does not supply subscriber names. The platform reports `CONFIG_REQUIRED` when subscriber APIs are unconfigured, rather than guessing names from carrier prefixes.
2. **Zero Synthetic Transcripts**:
   YouTube intelligence only returns transcripts if legitimately available via official or public subtitles. If unavailable, it sets `transcript_status="TRANSCRIPT_UNAVAILABLE"`. It never fabricates fictional transcripts.
3. **Passive vs Active Scanning**:
   Threat intelligence defaults strictly to passive reconnaissance (passive DNS, CT logs, whois). Active network port scanning requires explicit, documented scope permits.
4. **No Fabricated Travel Routes**:
   Geo intelligence records discrete, evidence-backed observations with temporal uncertainties. It never connects disconnected points into fictional movement routes.

