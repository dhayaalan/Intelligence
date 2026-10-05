# Provider Inventory

All tools operate as **Providers** within modules, implementing the standard `ProviderAdapter` interface.

| Provider ID | Parent Module | Status | Health Status | Primary Inputs | Normalized Output Entities | Timeout |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `spiderfoot` | `osint` | Active | `HEALTHY` | domain, ip, email | subdomains, ips, emails, tech | 15s |
| `shodan` | `osint` | Active | `HEALTHY` / `NOT_CONFIGURED` | ip, domain | ports, vulnerabilities, org | 10s |
| `maltego` | `osint` | Active | `HEALTHY` | domain, email | transform relationships | 10s |
| `theharvester` | `osint` | Active | `HEALTHY` | domain, email | public emails, hosts | 10s |
| `google_dork` | `osint` | Active | `HEALTHY` | domain, org | search exposure findings | 10s |
| `image_osint` | `osint` | Active | `HEALTHY` | image URL / upload | geolocation, EXIF, hashes | 10s |
| `username_recon` | `osint` | Active | `HEALTHY` | username | social profiles across 40+ platforms | 12s |
| `dns_intel` | `threat_intelligence` | Active | `HEALTHY` | domain, subdomain | A, AAAA, MX, NS, TXT | 10s |
| `host_discovery`| `threat_intelligence` | Active | `HEALTHY` | domain, ip | host alive, CDN, ASN | 10s |
| `service_discovery`| `threat_intelligence`| Active | `HEALTHY` | ip, domain | open ports, services | 10s |
| `tls_inspector`| `threat_intelligence` | Active | `HEALTHY` | domain, ip | certificates, SAN, TLS ciphers | 10s |
| `zap_scanner` | `threat_intelligence` | Active | `HEALTHY` / `NOT_CONFIGURED` | url, domain | CWE alerts, missing headers | 15s |
| `vulnerability_intel`| `threat_intelligence`| Active | `HEALTHY` | domain, ip, cve | CVE IDs, CVSS score, EPSS | 10s |
| `ioc_feed` | `threat_intelligence` | Active | `HEALTHY` | ip, domain, hash | threat score, malware families | 10s |
| `web_crawler` | `threat_intelligence` | Active | `HEALTHY` | url, domain | endpoints, forms, APIs | 15s |
| `example_verifier`| `example_intelligence`| Active | `HEALTHY` | domain, ip, email | verified entity records | 5s |
