# Sential Threat Intelligence & Security Scanner Engines (33 Total)

All 33 Threat Intelligence engines recovered and running under `ThreatIntelligenceModule`.

| # | Engine ID | Engine Name | Category | Targets | Mode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `openapi_discovery` | **OpenAPI & API Documentation Discovery Engine** | API_DISCOVERY | `url,domain,subdomain,hostname` | `PASSIVE / SAFE` |
| 2 | `asnmap` | **ASNMap Network Boundary Engine** | ATTACK_SURFACE | `domain,ip,asn,cidr` | `PASSIVE / SAFE` |
| 3 | `cdncheck` | **CDN & WAF Edge Inspection Engine** | ATTACK_SURFACE | `domain,subdomain,ip,url` | `PASSIVE / SAFE` |
| 4 | `dnsx` | **DNSx Resolution & CDNCheck Engine** | ATTACK_SURFACE | `domain,subdomain,ip,asn` | `PASSIVE / SAFE` |
| 5 | `amass` | **OWASP Amass Attack Surface Engine** | ATTACK_SURFACE | `domain,asn,cidr,ip_range` | `PASSIVE / SAFE` |
| 6 | `subfinder` | **Subfinder Passive Subdomain Engine** | ATTACK_SURFACE | `domain,subdomain,organization` | `PASSIVE / SAFE` |
| 7 | `uncover` | **Uncover Exposure Search Aggregator** | ATTACK_SURFACE | `domain,subdomain,ip,asn,organization` | `PASSIVE / SAFE` |
| 8 | `prowler` | **Prowler Cloud Security Posture Engine** | CLOUD_SECURITY | `cloud_account,kubernetes_cluster,domain` | `PASSIVE / SAFE` |
| 9 | `scoutsuite` | **ScoutSuite Cloud Auditor** | CLOUD_SECURITY | `cloud_account,domain` | `PASSIVE / SAFE` |
| 10 | `semgrep` | **Semgrep SAST Code Security Engine** | CODE_SECURITY | `repository,source_code,domain` | `PASSIVE / SAFE` |
| 11 | `trivy` | **Trivy Container & IaC Security Engine** | CONTAINER_SECURITY | `container_image,container,repository,domain` | `PASSIVE / SAFE` |
| 12 | `katana` | **Katana Next-Gen Web Crawler** | CRAWLER | `domain,subdomain,url` | `PASSIVE / SAFE` |
| 13 | `zap_spider` | **OWASP ZAP Spider & AJAX Crawler Engine** | CRAWLER | `url,domain,subdomain,hostname` | `PASSIVE / SAFE` |
| 14 | `web_crawler` | **Web Application Crawler & Spider Engine** | CRAWLER | `url,domain,subdomain,hostname` | `PASSIVE / SAFE` |
| 15 | `dns_intelligence` | **DNS Intelligence & Enumeration Engine** | DNS | `domain,subdomain,hostname` | `PASSIVE / SAFE` |
| 16 | `wazuh` | **Wazuh Endpoint CTI & Vulnerability Engine** | ENDPOINT_SECURITY | `endpoint,host,ip` | `PASSIVE / SAFE` |
| 17 | `http_discovery` | **HTTP / HTTPS Web Discovery Engine** | HTTP | `domain,subdomain,hostname,ip,url` | `PASSIVE / SAFE` |
| 18 | `httpx` | **HTTPX Web Surface Prober** | HTTP | `domain,subdomain,url,ip` | `PASSIVE / SAFE` |
| 19 | `host_discovery` | **Host Discovery & Network Reachability Engine** | NETWORK | `ip,ip_range,hostname,domain` | `PASSIVE / SAFE` |
| 20 | `masscan` | **Masscan Enterprise High-Speed Engine** | PORT_SERVICE | `ip,ip_range,cidr` | `PASSIVE / SAFE` |
| 21 | `naabu` | **Naabu Fast Port Discovery Engine** | PORT_SERVICE | `domain,subdomain,ip,ip_range,host` | `PASSIVE / SAFE` |
| 22 | `port_service_discovery` | **Port & Service Fingerprinting Engine** | PORT_SERVICE | `ip,ip_range,hostname,domain` | `PASSIVE / SAFE` |
| 23 | `gitleaks` | **Gitleaks Secret & Token Scanner** | SECRET_DISCOVERY | `repository,source_code,domain,url` | `PASSIVE / SAFE` |
| 24 | `tech_detection` | **Application & Technology Fingerprinting Engine** | TECHNOLOGY | `domain,subdomain,hostname,url,ip` | `PASSIVE / SAFE` |
| 25 | `threat_intelligence_correlation` | **Threat Intelligence & CVE Correlation Engine** | THREAT_INTEL | `domain,subdomain,ip,url,hash,email,cve,hostname,username,person,keyword,organization,ioc` | `PASSIVE / SAFE` |
| 26 | `tls_certificate` | **TLS & Certificate Intelligence Engine** | TLS | `domain,subdomain,hostname,ip,url` | `PASSIVE / SAFE` |
| 27 | `testssl` | **testssl.sh Cryptographic Security Engine** | TLS | `domain,subdomain,ip,url` | `PASSIVE / SAFE` |
| 28 | `nuclei` | **Nuclei Vulnerability & Exposure Scanner** | VULNERABILITY | `domain,subdomain,url,ip` | `PASSIVE / SAFE` |
| 29 | `zap_active_scan` | **OWASP ZAP Active Vulnerability Assessment Engine** | VULNERABILITY | `url,domain,subdomain` | `PASSIVE / SAFE` |
| 30 | `openvas` | **OpenVAS / Greenbone Infrastructure Vulnerability Engine** | VULNERABILITY | `ip,ip_range,host,cidr` | `PASSIVE / SAFE` |
| 31 | `wapiti` | **Wapiti Web Vulnerability Scanner** | VULNERABILITY | `url,domain,web_application` | `PASSIVE / SAFE` |
| 32 | `dalfox` | **Dalfox Parameter & XSS Analyzer** | WEB_SECURITY | `domain,subdomain,url` | `PASSIVE / SAFE` |
| 33 | `nikto` | **Nikto Web Server Security Scanner** | WEB_SECURITY | `domain,subdomain,url,ip` | `PASSIVE / SAFE` |
