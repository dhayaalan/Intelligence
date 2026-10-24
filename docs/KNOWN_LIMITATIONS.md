# Known Limitations & Operational Boundaries

This document defines the strict legal, architectural, and operational constraints governing the Sential Intelligence Platform. All users and automated workflows must operate within these boundaries.

---

## 1. Tool-Specific Operational Limitations

### A. Shodan
- **Port and Service Census Only**: Shodan indexes publicly exposed network services, banners, open ports, and protocol responses.
- **NOT an Arbitrary CCTV Stream Engine**: Shodan is not a global surveillance search engine that automatically supplies arbitrary live CCTV video feeds. Live RTSP or HTTP video streaming is only possible if an authorized, exposed camera device responds on a discovered port with reachable credentials.
- **API Quotas**: Query credits and scan credits are strictly enforced by Shodan. Free tier users are limited to the keyless InternetDB API (`internetdb.shodan.io`), which returns open ports, CPEs, hostnames, and known CVEs without banner details.

### B. Google Dorks
- **Lead Generation, NOT Confirmed Evidence**: Dork search results represent leads for investigator verification, not verified facts.
- **No Automated Scraping / CAPTCHA Bypassing**: To comply with Google's Terms of Service and anti-bot protections, web-scope dorks are generated as analyst browser search URLs rather than aggressively scraped headlessly.
- **News RSS Scope**: Automated execution is restricted to legitimate Google News RSS XML feeds. Public web scraping that risks IP blacklisting or Cloudflare challenge triggers is intentionally prohibited.

### C. theHarvester
- **Target Restriction**: theHarvester exclusively targets public domain names. IP addresses, person names, and phone numbers are rejected.
- **Passive Sources by Default**: Default execution utilizes passive certificate transparency logs (`crtsh`, `certspotter`) to prevent accidental unauthorized active probing.
- **Command Injection Safeguards**: Direct shell execution is strictly prohibited; all commands execute with `shell=False` or via the isolated HTTP worker microservice.

### D. SpiderFoot
- **Target Authorization Required**: SpiderFoot must never be aimed at unauthorized third-party infrastructure. The platform prohibits scanning loopback (`127.0.0.1`), local hostnames, and RFC 1918 private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
- **Scan Duration**: Comprehensive SpiderFoot scans can require several minutes to hours. In-process HTTP request handlers must never block on full scan completions; jobs run asynchronously with periodic status polling.

### E. Maltego
- **Desktop Runtime Prerequisite**: Maltego Desktop is an analyst client application that cannot be executed headlessly inside a web browser.
- **Integration Boundary**: Sential supports Maltego through RFC-4180 CSV export files formatted for Maltego's Table Import Wizard, and transform handler definitions. It does not replace the analyst's Maltego Commercial / Community license.

---

## 2. Vehicle Intelligence & Owner Privacy Boundaries

- **No Scraping of Restricted Vehicle Owner Registries**: Sential strictly respects data privacy regulations (DPDP Act, GDPR). The platform **never** scrapes protected government vehicle databases (e.g. Parivahan Sewa, VAHAN, DVLA, state DMVs) for private citizen identity records.
- **Attribution vs Ownership**: Vehicle plate analysis provides administrative jurisdiction, Regional Transport Office (RTO) code attribution (e.g. Telangana `TS09` -> Khairatabad RTO), and syntax validation.
- **Authorized Gateway Requirement**: Live registration details, vehicle make/model verification, and registered ownership inquiries require an authorized, government-issued API gateway credential configured in `.env`.
- **NHTSA Global VIN Registry**: Keyless NHTSA decoding applies exclusively to 17-character VINs for vehicles manufactured or imported into North America and global reporting manufacturers. It does not return personal owner identities.

---

## 3. Media Ingestion & Computer Vision Constraints

- **ML Inference is Probabilistic**: Vehicle candidate detection and OCR readings are probabilistic model inferences, **never confirmed evidentiary facts**. Every sighting must be marked as `CANDIDATE_MATCH` until verified by an authorized investigator (`HUMAN_CONFIRMED`).
- **Separated Confidence Metrics**: Plate detection confidence (object localization) and OCR confidence (character decoding) are reported separately. A high detection confidence does not guarantee accurate character decoding under motion blur or low lighting.
- **Temporal Tracking Deduplication**: Multiple detections of the same plate across consecutive frames within a 5-second window are merged under a unified `temporal_track_id` to prevent artificial inflation of vehicle sightings.
- **SSRF Protections on RTSP/Video Streams**: User-supplied camera URLs and RTSP feeds are validated to prevent Server-Side Request Forgery. Feeds pointing to internal AWS/GCP metadata endpoints (`169.254.169.254`) or localhost services are immediately blocked.
