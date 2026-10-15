# Sential Threat Intelligence & Security Scanner Engines (33 Total)

All 33 Threat Intelligence engines recovered and running under `ThreatIntelligenceModule`.

| # | Engine ID | Engine Name | Category | Targets | Mode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `openapi_discovery` | **OpenAPI & API Documentation Discovery Engine** | API_DISCOVERY | `url,domain,subdomain,hostname` | `PASSIVE / SAFE` |
| 2 | `asnmap` | **ASNMap Network Boundary Engine** | ATTACK_SURFACE | `domain,ip,asn,cidr` | `PASSIVE / SAFE` |
| 3 | `cdncheck` | **CDN & WAF Edge Inspection Engine** | ATTACK_SURFACE | `domain,subdomain,ip,url` | `PASSIVE / SAFE` |
| 4 | `crtsh` | **Certificate Transparency CT-Log Engine** | ATTACK_SURFACE | `domain,url` | `PASSIVE / SAFE` |
| 5 | `dnsx` | **DNSx Resolution & CDNCheck Engine** | ATTACK_SURFACE | `domain,subdomain,ip,asn` | `PASSIVE / SAFE` |
| 6 | `amass` | **OWASP Amass Attack Surface Engine** | ATTACK_SURFACE | `domain,asn,cidr,ip_range` | `PASSIVE / SAFE` |
| 7 | `subfinder` | **Subfinder Passive Subdomain Engine** | ATTACK_SURFACE | `domain,subdomain,organization` | `PASSIVE / SAFE` |
| 8 | `uncover` | **Uncover Exposure Search Aggregator** | ATTACK_SURFACE | `domain,subdomain,ip,asn,organization` | `PASSIVE / SAFE` |
| 9 | `prowler` | **Prowler Cloud Security Posture Engine** | CLOUD_SECURITY | `cloud_account,kubernetes_cluster,domain` | `PASSIVE / SAFE` |
| 10 | `scoutsuite` | **ScoutSuite Cloud Auditor** | CLOUD_SECURITY | `cloud_account,domain` | `PASSIVE / SAFE` |
| 11 | `semgrep` | **Semgrep SAST Code Security Engine** | CODE_SECURITY | `repository,source_code,domain` | `PASSIVE / SAFE` |
| 12 | `trivy` | **Trivy Container & IaC Security Engine** | CONTAINER_SECURITY | `container_image,container,repository,domain` | `PASSIVE / SAFE` |
| 13 | `katana` | **Katana Next-Gen Web Crawler** | CRAWLER | `domain,subdomain,url` | `PASSIVE / SAFE` |
| 14 | `zap_spider` | **OWASP ZAP Spider & Application Crawler** | CRAWLER | `url,domain,subdomain,hostname` | `PASSIVE / SAFE` |
| 15 | `web_crawler` | **Web Application Crawler & Spider Engine** | CRAWLER | `url,domain,subdomain,hostname` | `PASSIVE / SAFE` |
| 16 | `dns_intelligence` | **DNS Intelligence & Enumeration Engine** | DNS | `domain,subdomain,hostname` | `PASSIVE / SAFE` |
| 17 | `wazuh` | **Wazuh Endpoint CTI & Vulnerability Engine** | ENDPOINT_SECURITY | `endpoint,host,ip` | `PASSIVE / SAFE` |
| 18 | `http_discovery` | **HTTP / HTTPS Web Discovery Engine** | HTTP | `domain,subdomain,hostname,ip,url` | `PASSIVE / SAFE` |
| 19 | `httpx` | **HTTPX Web Surface Prober** | HTTP | `domain,subdomain,url,ip` | `PASSIVE / SAFE` |
| 20 | `host_discovery` | **Host Discovery & Network Reachability Engine** | NETWORK | `ip,ip_range,hostname,domain` | `PASSIVE / SAFE` |
| 21 | `masscan` | **Masscan Enterprise High-Speed Engine** | PORT_SERVICE | `ip,ip_range,cidr` | `PASSIVE / SAFE` |
| 22 | `naabu` | **Naabu Fast Port Discovery Engine** | PORT_SERVICE | `domain,subdomain,ip,ip_range,host` | `PASSIVE / SAFE` |
| 23 | `port_service_discovery` | **Port & Service Fingerprinting Engine** | PORT_SERVICE | `ip,ip_range,hostname,domain` | `PASSIVE / SAFE` |
| 24 | `gitleaks` | **Gitleaks Secret & Token Scanner** | SECRET_DISCOVERY | `repository,source_code,domain,url` | `PASSIVE / SAFE` |
| 25 | `tech_detection` | **Application & Technology Fingerprinting Engine** | TECHNOLOGY | `domain,subdomain,hostname,url,ip` | `PASSIVE / SAFE` |
| 26 | `ioc_feed` | **Global IOC & Threat Intelligence Feed (AlienVault OTX / URLhaus / AbuseIPDB)** | THREAT_INTEL | `ip,domain,hash,url` | `PASSIVE / SAFE` |
| 27 | `greynoise_community` | **GreyNoise Community** | THREAT_INTEL | `ip,ipv4` | `PASSIVE / SAFE` |
| 28 | `threat_intelligence_correlation` | **Threat Intelligence & CVE Correlation Engine** | THREAT_INTEL | `domain,subdomain,ip,url,hash,email,cve,hostname,username,person,keyword,organization,ioc` | `PASSIVE / SAFE` |
| 29 | `threatfox` | **abuse.ch ThreatFox IOC Intelligence** | THREAT_INTEL | `ip,domain,url,hash,ioc` | `PASSIVE / SAFE` |
| 30 | `tls_certificate` | **TLS & Certificate Intelligence Engine** | TLS | `domain,subdomain,hostname,ip,url` | `PASSIVE / SAFE` |
| 31 | `testssl` | **testssl.sh Cryptographic Security Engine** | TLS | `domain,subdomain,ip,url` | `PASSIVE / SAFE` |
| 32 | `vulnerability_intel` | **CVE, EPSS & CISA KEV Vulnerability Intelligence** | VULNERABILITY | `cve,domain,ip` | `PASSIVE / SAFE` |
| 33 | `nvd_cve` | **NIST National Vulnerability Database (NVD) CVE API 2.0** | VULNERABILITY | `cve,keyword,software` | `PASSIVE / SAFE` |
| 34 | `nuclei` | **Nuclei Vulnerability & Exposure Scanner** | VULNERABILITY | `domain,subdomain,url,ip` | `PASSIVE / SAFE` |
| 35 | `zap_active_scan` | **OWASP ZAP Active Vulnerability Assessment Engine** | VULNERABILITY | `url,domain,subdomain,hostname,ip` | `PASSIVE / SAFE` |
| 36 | `openvas` | **OpenVAS / Greenbone Infrastructure Vulnerability Engine** | VULNERABILITY | `ip,ip_range,host,cidr` | `PASSIVE / SAFE` |
| 37 | `wapiti` | **Wapiti Web Vulnerability Scanner** | VULNERABILITY | `url,domain,web_application` | `PASSIVE / SAFE` |
| 38 | `dalfox` | **Dalfox Parameter & XSS Analyzer** | WEB_SECURITY | `domain,subdomain,url` | `PASSIVE / SAFE` |
| 39 | `nikto` | **Nikto Web Server Security Scanner** | WEB_SECURITY | `domain,subdomain,url,ip` | `PASSIVE / SAFE` |
