# Provider Coverage, Capabilities, and Authorization Inventory

## 1. Overview & Verification Standards

A provider is not considered functional simply because its name appears in a manifest, catalog, or user interface. Sential enforces a strict distinction between:

1. **Provider Health**: Whether the service endpoint or adapter is technically reachable and responsive.
2. **Provider Authorization**: Whether the current deployment or investigator possesses valid API credentials and lawful authority to execute a specific query.
3. **Source Information Availability**: Whether the underlying public or authorized source legitimately exposes the requested information.

---

## 2. Standardized Provider Execution Statuses

The platform enforces truthful execution states across all adapters:

| Status Code | Meaning | Example Scenario |
| :--- | :--- | :--- |
| **`SUCCESS`** | Query succeeded and discovered relevant, verified records. | Real RSS article found; WHOIS registration retrieved. |
| **`SUCCESS_EMPTY`** | Query completed cleanly without error, but no matching records exist. | Username query checked against platform and returned 404 Not Found. |
| **`PARTIAL`** | Query returned results, but some fields or records were truncated. | Search engine returned top 5 results before encountering per-query ceiling. |
| **`FAILED`** | Network error, DNS resolution timeout, or unhandled 5xx exception. | Upstream server timed out after 10 seconds. |
| **`CONFIG_REQUIRED`** | Adapter requires an API key or configuration token that is missing. | Shodan, Censys, or VirusTotal API key not configured in environment. |
| **`AUTH_REQUIRED`** | Query requires active investigator credentials or session cookies. | Private platform API requiring investigator OAuth token. |
| **`RATE_LIMITED`** | Upstream provider responded with HTTP 429 Too Many Requests. | GitHub or Reddit public rate limit exceeded. |
| **`RESTRICTED`** | Source is legally or policy-restricted; unauthenticated access prohibited. | DMV vehicle owner registry; private social media profile. |
| **`NOT_FOUND`** | Requested identifier does not exist on the queried service. | Nonexistent email on mailbox verification server. |
| **`SKIPPED`** | Provider was bypassed because it does not support the query type. | Skipping DNS resolution for a phone number clue. |

---

## 3. Module & Provider Inventory Matrix

### 3.1 OSINT Module (`osint`)
| Provider ID | Declared Capabilities | Auth Requirement | Live Coverage Status |
| :--- | :--- | :--- | :--- |
| `username_recon` | Username profile existence across 50+ platforms | Public HTTP / Permitted endpoints | **Verified Live** (Reddit, GitHub, Mastodon, HackerNews, Telegram public) |
| `email_recon` | Mailbox MX syntax & domain lookup | Public DNS | **Verified Live** |
| `phone_recon` | ITU-T E.164 parsing, carrier & region detection | Offline ITU metadata | **Verified Live** |
| `vehicle_registration_recon` | Jurisdiction plate syntax validation | DMV API Token (`CONFIG_REQUIRED` if absent) | **Verified Local Syntax**; live state DMV requires lawful credential |
| `dns_recon` | A, AAAA, CNAME, MX, TXT, NS record lookup | Public DNS | **Verified Live** |
| `whois_recon` | RDAP / WHOIS registration data | Public RDAP | **Verified Live** |

### 3.2 Threat Intelligence Module (`threat_intelligence`)
| Provider ID | Declared Capabilities | Auth Requirement | Live Coverage Status |
| :--- | :--- | :--- | :--- |
| `passive_dns` | Historical DNS resolution | Public / Free tier | **Verified Live** |
| `asn_lookup` | BGP ASN, routing prefixes, CIDR | Public WHOIS / IPinfo | **Verified Live** |
| `ssl_certificate` | TLS certificate transparency logs (crt.sh) | Public crt.sh | **Verified Live** |
| `shodan_recon` | Port scanning, service banners, IoT telemetry | `SHODAN_API_KEY` | `CONFIG_REQUIRED` when key unconfigured |
| `vulnerability_scanner` | Active port probe, banner grab | Lawful Scope Permit Required | Restricted to permitted lab scope (`scanme.nmap.org`) |

### 3.3 News Intelligence Module (`news_intelligence`)
| Provider ID | Declared Capabilities | Auth Requirement | Live Coverage Status |
| :--- | :--- | :--- | :--- |
| `rss_aggregator` | Multi-wire RSS feed aggregation across 40+ global outlets | Public RSS XML | **Verified Live** (AP, Reuters, BBC, DW, France24, The Hindu, etc.) |
| `article_extractor` | HTML readability parsing, OpenGraph lead images | Public HTTP | **Verified Live** |
| `semantic_search` | Hybrid lexical/semantic topical retrieval | Local embedding engine | **Verified Live** |
| `media_forensics` | Image/video perceptual hashing, duplicate detection | Local PIL / hash | **Verified Live** |

### 3.4 Social Media Intelligence Module (`social_media_intelligence`)
| Provider ID | Declared Capabilities | Auth Requirement | Live Coverage Status |
| :--- | :--- | :--- | :--- |
| `youtube_collector` | Video microdata, authentic upload date, channel ID | Public HTML microdata | **Verified Live** (Never fabricates subtitles) |
| `reddit_collector` | Public subreddits, user post history | Public JSON endpoints | **Verified Live** |
| `mastodon_collector` | Fediverse public posts, user profile | Public ActivityPub API | **Verified Live** |
| `bluesky_collector` | Public AT Protocol posts, author profiles | Public ATProto API | **Verified Live** |
| `telegram_collector` | Public channel previews, message text | Public t.me web preview | **Verified Live** |
| `meta_graph_collector` | Public Facebook/Instagram pages | Meta Graph API v21.0 Token | `CONFIG_REQUIRED` when token unconfigured |

### 3.5 Geospatial Intelligence Module (`geo_intelligence`)
| Provider ID | Declared Capabilities | Auth Requirement | Live Coverage Status |
| :--- | :--- | :--- | :--- |
| `authorized_file_ingest` | JSON, CSV, GPX, KML location history parsing | Investigator Upload | **Verified Live** |
| `exif_metadata_extractor` | WGS84 coordinates from media EXIF | Local image analysis | **Verified Live** |
| `incident_geocoder` | Nominal coordinates for place names | Local Gazetter | **Verified Live** |
| `ip_approximate_resolver` | City/ISP approximate POP location | Local GeoIP database | **Verified Live** (Explicitly marked approximate) |
