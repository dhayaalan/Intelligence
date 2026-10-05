# Provider Integrations

## 1. OSINT Providers

| Provider | ID | Collection Scope | Fallback / Isolation |
| :--- | :--- | :--- | :--- |
| **SpiderFoot** | `spiderfoot` | Automated multi-source recon, subdomains, whois | Socket and heuristic fallbacks |
| **Shodan** | `shodan` | Port discovery, banners, CVEs, ASN routing | Try/except caught; does not fail OSINT |
| **Maltego** | `maltego` | Transform pivots (DNS to IP, IP to Org) | Local transform graph logic |
| **theHarvester** | `theharvester` | Search exposure emails, subdomains, hosts | Search engine scraping logic |
| **Google Dork** | `google_dork` | Sensitive filetype and index leakage detection | Dork pattern evaluation |

## 2. Threat Intelligence Providers

| Provider | ID | Collection Scope | Fallback / Isolation |
| :--- | :--- | :--- | :--- |
| **DNS Intel** | `dns_intel` | A, NS, MX, TXT, SPF, DMARC records | Local system DNS resolution |
| **Host Discovery** | `host_discovery` | Host responsiveness and CDN detection | Origin probe heuristics |
| **Service Discovery**| `service_discovery`| TCP port probing and service banner verification | Non-blocking socket connect |
| **ZAP Scanner** | `zap_scanner` | OWASP Top 10 web alert headers and CWE items | Header inspection adapter |
| **Vulnerability Intel**| `vulnerability_intel`| CVE matching and EPSS exploitation scores | NVD local lookup |
| **IOC Feed** | `ioc_feed` | Malicious IP/domain threat scores & malware families | Threat intelligence feed scoring |
