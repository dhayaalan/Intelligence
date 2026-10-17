# Provider Capabilities, Coverage & Truthful Status Architecture

## 1. Executive Summary

Sential integrates specialized intelligence engines spanning OSINT, Threat Intelligence, Social Media Intelligence, News Intelligence, Vehicle Intelligence, and Geospatial Intelligence.

In accordance with strict forensic standards:
1. **Zero Fake Findings**: When credentials or public records are absent, providers declare `CONFIG_REQUIRED` or `SUCCESS_EMPTY`. They never synthesize placeholder people, fake names, or imaginary registrations.
2. **Deterministic Classification**: Identifiers (phones, emails, plates) are categorized deterministically and resolved against authoritative syntax and registry specs.
3. **Truthful Telemetry**: The Collection Completeness Index (CCI) measures real coverage rather than simulated completeness.

---

## 2. Intelligence Module & Provider Matrix

| Module | Provider ID | Type | Capabilities | Real Data Sources / Lawful Boundary |
| :--- | :--- | :--- | :--- | :--- |
| **OSINT** | `telecom_intelligence` | Deep Engine | Phone normalization, carrier detection, country/region routing | Google `phonenumbers` offline metadata library; lawful subscriber lookup requires `TELECOM_LOOKUP_API_KEY` |
| **OSINT** | `vehicle_intelligence` | Deep Engine | Plate syntax validation, issuing jurisdiction inference | Regional plate syntax specifications (US, UK DVLA, India VAHAN, EU); live title registry requires `DMV_API_KEY` |
| **OSINT** | `shodan` | Commercial API | Host open ports, banners, SSL certificates | Shodan REST API via `SHODAN_API_KEY` |
| **OSINT** | `censys` | Commercial API | TLS certificates, IPv4 host fingerprints | Censys Search API via `CENSYS_API_ID` & `CENSYS_API_SECRET` |
| **OSINT** | `theharvester` | Prober Engine | Public search engine domain indexing | Bing, DuckDuckGo, Baidu public search |
| **OSINT** | `spiderfoot` | Prober Engine | Multi-source OSINT aggregation | SpiderFoot open-source reconnaissance engine |
| **OSINT** | `image_osint` | Media Engine | EXIF metadata, camera make/model, GPS tags | Python `Pillow` EXIF extraction |
| **OSINT** | `platform_probers` (329 sites) | Prober Engine | Public account profile presence checks | HTTP status verification against WhatsMyName public catalog |
| **Social Media** | `youtube` | Media Engine | Video metadata, playable embed, subtitle tracks | YouTube oEmbed API, YouTube Data API v3; zero synthetic transcripts |
| **Social Media** | `reddit` | Social Engine | Public subreddit threads, user posts | Public Reddit JSON API |
| **Social Media** | `bluesky` | Social Engine | AT Protocol public post streams | Bluesky public indexing API |
| **Social Media** | `telegram` | Messaging Engine | Public channel messages & metadata | Telegram public web channel previews |
| **Threat Intel** | `alienvault_otx` | Threat Feed | Pulses, IOCs, IP/Domain reputation | AlienVault OTX REST API |
| **Threat Intel** | `threatminer` | Threat Feed | Passive DNS, URI samples, malware hashes | ThreatMiner API |
| **Threat Intel** | `urlscan` | Threat Feed | DOM snapshots, TLS certificates, IP routing | URLScan.io API |
| **Threat Intel** | `virustotal` | Threat Feed | File hashes, detection engine ratios | VirusTotal v3 API |
| **Geo Intel** | `geo_parsers` | Ingestion Engine | JSON, CSV, GPX, KML boundary validation | ISO/RFC standards; WGS84 range `[-90, 90]`, `[-180, 180]` |
| **News Intel** | `news_engine` | Media Engine | RSS feeds, news wire discovery, fact extraction | RSS/Atom feeds, DuckDuckGo News |

---

## 3. Truthful Status Hierarchy & Investigator Guidance

When an investigator queries an entity, provider telemetry is reflected honestly in the investigation snapshot and pipeline trace:

```
┌──────────────────────────────────────────────────────────┐
│ Provider Execution Statuses                              │
├─────────────────┬────────────────────────────────────────┤
│ SUCCESS         │ Verified records discovered and mapped │
│ SUCCESS_EMPTY   │ Authoritative check completed; 0 found │
│ CONFIG_REQUIRED │ Live lawful registry credentials absent│
│ AUTH_REQUIRED   │ Active user session required           │
│ RATE_LIMITED    │ Upstream API quota reached             │
│ DEGRADED        │ Upstream provider timeout / connection │
└─────────────────┴────────────────────────────────────────┘
```

### Subscriber Registry & Commercial Feeds Handling
- **Telecom**: When an investigator enters `+14155552671`, the platform extracts valid E.164 formatting (`+14155552671`), country (`United States`), and carrier (`Twilio`). The subscriber name is reported as `CONFIG_REQUIRED` with the explanation:
  > *"Lawful subscriber registration lookup requires authorized telecommunications gateway credentials (TELECOM_LOOKUP_API_KEY). Synthetic personal identity records are strictly prohibited."*
- **Vehicle Plates**: When an investigator enters `MH12AB1234`, the platform validates the format, attributes the jurisdiction to `Maharashtra, India`, and sets `live_registration_record="CONFIG_REQUIRED"`. The owner name is NEVER hallucinated.

---

## 4. Collection Completeness Index (CCI)

The platform computes the **Collection Completeness Index (CCI)** for every search:
$$\text{CCI} = \left( \frac{\text{Successful Modules}}{\text{Total Modules Attempted}} \right) \times 100\%$$

- **High Assurance ($\ge 90\%$)**: All attempted intelligence modules returned verified responses.
- **Moderate Assurance ($60\% - 89\%$)**: Majority of sources responded; non-critical modules degraded or empty.
- **Partial Coverage ($< 60\%$)**: Key sources were unconfigured, restricted, or rate-limited. Investigators are alerted to missing configuration.
