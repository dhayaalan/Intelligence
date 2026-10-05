# Module Inventory

Sential Platform isolates intelligence domains into independent modules conforming to the `IntelligenceModule` contract.

| Module ID | Name | Status | Capabilities | Registered Providers |
| :--- | :--- | :--- | :--- | :--- |
| **`osint`** | Open Source Intelligence | **ENABLED** | `person_search`, `domain_search`, `email_search`, `username_search`, `ip_search`, `image_search` | SpiderFoot, Shodan, Maltego, theHarvester, Google Dork, Image OSINT, Username Recon |
| **`threat_intelligence`** | Threat Intelligence | **ENABLED** | `dns`, `host_discovery`, `service_discovery`, `vulnerability_scan`, `ioc_lookup`, `web_security` | DNS Intel, Host Discovery, Service Discovery, ZAP Scanner, Vulnerability Intel, IOC Feed, TLS Inspector, Web Crawler |
| **`example_intelligence`** | Example Intelligence (Plugin) | **EXTENSIBLE** | `search`, `enrichment` | Example Verifier Provider |

## Future Module Extensibility Pipeline

The architecture is designed to support future modules seamlessly:
* `vulnerability_intelligence` (Dedicated deep CVE/Exploit lifecycle)
* `dark_web` (Tor / I2P / Breach forums)
* `digital_forensics` (Disk / Memory / Artifact analysis)
* `geospatial` (Satellite / Location / Geofencing)
* `identity_intelligence` (Breach credential tracking)
* `financial_intelligence` (Corporate ownership / SEC filings)
* `social_intelligence` (Social graph analysis)

No Core Platform modification is required to introduce any of these modules.
