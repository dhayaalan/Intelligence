# Sential Platform — Comprehensive Tool & Provider Inventory

This document is the verified migration inventory of all **335 OSINT tools/platforms** and **33 Threat Intelligence engines** recovered from `saas_platform` and operational in Sential.

## Summary Metrics

- **Total Integrated Tools / Providers**: 368
- **OSINT Capabilities / Providers**: 335 (Requirement: 300+)
- **Threat Intelligence Capabilities / Providers**: 33 (Requirement: 33)
- **Primary Database**: MongoDB (`sential_db`)
- **Architecture**: Pluggable Provider Registry with Zero Core Coupling

---

## 1. Threat Intelligence Scanning Engines (33 Engines)

### 1. OpenAPI & API Documentation Discovery Engine

- **Tool Name**: OpenAPI & API Documentation Discovery Engine
- **Tool ID**: `openapi_discovery`
- **Category**: API_DISCOVERY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/openapi_discovery_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `url, domain, subdomain, hostname`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `openapi_schema_parsing, swagger_extraction, api_endpoint_enumeration, auth_scheme_detection`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `30.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 2. ASNMap Network Boundary Engine

- **Tool Name**: ASNMap Network Boundary Engine
- **Tool ID**: `asnmap`
- **Category**: ATTACK_SURFACE
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/asnmap_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, ip, asn, cidr`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `asn_lookup, cidr_mapping, org_prefix_discovery, bgp_routing`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `20.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 3. CDN & WAF Edge Inspection Engine

- **Tool Name**: CDN & WAF Edge Inspection Engine
- **Tool ID**: `cdncheck`
- **Category**: ATTACK_SURFACE
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/cdncheck_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, ip, url`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `cdn_detection, waf_fingerprinting, origin_ip_masking_check`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `15.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 4. DNSx Resolution & CDNCheck Engine

- **Tool Name**: DNSx Resolution & CDNCheck Engine
- **Tool ID**: `dnsx`
- **Category**: ATTACK_SURFACE
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/dnsx_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, ip, asn`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `fast_resolution, wildcard_filtering, cdn_detection, asn_lookup, ptr_reverse`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `15.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 5. OWASP Amass Attack Surface Engine

- **Tool Name**: OWASP Amass Attack Surface Engine
- **Tool ID**: `amass`
- **Category**: ATTACK_SURFACE
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/amass_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, asn, cidr, ip_range`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `subdomain_enumeration, asn_mapping, infrastructure_graphing, whois_recon`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `45.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 6. Subfinder Passive Subdomain Engine

- **Tool Name**: Subfinder Passive Subdomain Engine
- **Tool ID**: `subfinder`
- **Category**: ATTACK_SURFACE
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/subfinder_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, organization`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `passive_subdomains, ct_log_parsing, dns_aggregation, source_attribution`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `20.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 7. Uncover Exposure Search Aggregator

- **Tool Name**: Uncover Exposure Search Aggregator
- **Tool ID**: `uncover`
- **Category**: ATTACK_SURFACE
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/uncover_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, ip, asn, organization`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `shodan_query, censys_query, fofa_query, exposure_mapping`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `15.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 8. Prowler Cloud Security Posture Engine

- **Tool Name**: Prowler Cloud Security Posture Engine
- **Tool ID**: `prowler`
- **Category**: CLOUD_SECURITY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/prowler_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `cloud_account, kubernetes_cluster, domain`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `cloud_posture_assessment, cis_benchmarks, iam_security_audit, storage_encryption_audit`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `45.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 9. ScoutSuite Cloud Auditor

- **Tool Name**: ScoutSuite Cloud Auditor
- **Tool ID**: `scoutsuite`
- **Category**: CLOUD_SECURITY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/scoutsuite_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `cloud_account, domain`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `cloud_api_audit, iam_policy_analysis, s3_bucket_exposure, security_group_audit`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `40.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 10. Semgrep SAST Code Security Engine

- **Tool Name**: Semgrep SAST Code Security Engine
- **Tool ID**: `semgrep`
- **Category**: CODE_SECURITY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/semgrep_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `repository, source_code, domain`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `sast_code_audit, owasp_top_10_code_rules, framework_security_checks, taint_tracking`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `45.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 11. Trivy Container & IaC Security Engine

- **Tool Name**: Trivy Container & IaC Security Engine
- **Tool ID**: `trivy`
- **Category**: CONTAINER_SECURITY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/trivy_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `container_image, container, repository, domain`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `container_image_scan, sbom_generation, iac_misconfiguration, dependency_cve_scan`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `40.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 12. Katana Next-Gen Web Crawler

- **Tool Name**: Katana Next-Gen Web Crawler
- **Tool ID**: `katana`
- **Category**: CRAWLER
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/katana_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, url`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `deep_crawl, javascript_parsing, form_discovery, endpoint_extraction`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `20.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 13. OWASP ZAP Spider & AJAX Crawler Engine

- **Tool Name**: OWASP ZAP Spider & AJAX Crawler Engine
- **Tool ID**: `zap_spider`
- **Category**: CRAWLER
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/zap_spider_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `url, domain, subdomain, hostname`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `traditional_spider, ajax_spider, spa_crawling, form_discovery, zap_automation_framework`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `30.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 14. Web Application Crawler & Spider Engine

- **Tool Name**: Web Application Crawler & Spider Engine
- **Tool ID**: `web_crawler`
- **Category**: CRAWLER
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/web_crawler_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `url, domain, subdomain, hostname`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `recursive_crawling, form_extraction, parameter_discovery, scope_enforcement, js_endpoint_extraction`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `30.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 15. DNS Intelligence & Enumeration Engine

- **Tool Name**: DNS Intelligence & Enumeration Engine
- **Tool ID**: `dns_intelligence`
- **Category**: DNS
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/dns_intelligence_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, hostname`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `a_record, aaaa_record, mx_lookup, ns_lookup, txt_inspection, spf_dmarc_analysis, subdomain_resolution`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `30.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 16. Wazuh Endpoint CTI & Vulnerability Engine

- **Tool Name**: Wazuh Endpoint CTI & Vulnerability Engine
- **Tool ID**: `wazuh`
- **Category**: ENDPOINT_SECURITY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/wazuh_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `endpoint, host, ip`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `endpoint_inventory, package_cve_correlation, host_compliance_audit`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `25.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 17. HTTP / HTTPS Web Discovery Engine

- **Tool Name**: HTTP / HTTPS Web Discovery Engine
- **Tool ID**: `http_discovery`
- **Category**: HTTP
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/http_discovery_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, hostname, ip, url`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `http_probing, redirect_validation, security_headers_audit, cookie_flags, robots_txt, sitemap_xml`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `30.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 18. HTTPX Web Surface Prober

- **Tool Name**: HTTPX Web Surface Prober
- **Tool ID**: `httpx`
- **Category**: HTTP
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/httpx_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, url, ip`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `status_codes, header_analysis, technology_probing, tls_metadata, redirect_chains`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `12.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 19. Host Discovery & Network Reachability Engine

- **Tool Name**: Host Discovery & Network Reachability Engine
- **Tool ID**: `host_discovery`
- **Category**: NETWORK
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/host_discovery_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `ip, ip_range, hostname, domain`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `host_discovery, reachability_probe, nmap_integration`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `30.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 20. Masscan Enterprise High-Speed Engine

- **Tool Name**: Masscan Enterprise High-Speed Engine
- **Tool ID**: `masscan`
- **Category**: PORT_SERVICE
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/masscan_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `ip, ip_range, cidr`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `high_speed_port_scan, cidr_enumeration, banner_grab`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `30.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 21. Naabu Fast Port Discovery Engine

- **Tool Name**: Naabu Fast Port Discovery Engine
- **Tool ID**: `naabu`
- **Category**: PORT_SERVICE
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/naabu_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, ip, ip_range, host`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `fast_port_scan, syn_probing, top_ports, rate_limiting`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `15.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 22. Port & Service Fingerprinting Engine

- **Tool Name**: Port & Service Fingerprinting Engine
- **Tool ID**: `port_service_discovery`
- **Category**: PORT_SERVICE
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/port_service_discovery_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `ip, ip_range, hostname, domain`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `tcp_port_discovery, service_fingerprint, banner_grabbing, tls_detection`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `30.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 23. Gitleaks Secret & Token Scanner

- **Tool Name**: Gitleaks Secret & Token Scanner
- **Tool ID**: `gitleaks`
- **Category**: SECRET_DISCOVERY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/gitleaks_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `repository, source_code, domain, url`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `secret_detection, token_entropy_analysis, credential_leak_audit`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `30.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 24. Application & Technology Fingerprinting Engine

- **Tool Name**: Application & Technology Fingerprinting Engine
- **Tool ID**: `tech_detection`
- **Category**: TECHNOLOGY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/tech_detection_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, hostname, url, ip`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `server_fingerprint, framework_detection, cms_detection, cdn_waf_identification, version_extraction`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `30.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 25. Threat Intelligence & CVE Correlation Engine

- **Tool Name**: Threat Intelligence & CVE Correlation Engine
- **Tool ID**: `threat_intelligence_correlation`
- **Category**: THREAT_INTEL
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/threat_intelligence_correlation_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, ip, url, hash, email, cve, hostname, username, person, keyword, organization, ioc`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `cve_correlation, cisa_kev_lookup, threat_actor_attribution, malware_correlation, stix_taxii_matching`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `30.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 26. TLS & Certificate Intelligence Engine

- **Tool Name**: TLS & Certificate Intelligence Engine
- **Tool ID**: `tls_certificate`
- **Category**: TLS
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/tls_certificate_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, hostname, ip, url`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `x509_parsing, san_extraction, expiration_check, issuer_validation, sha256_fingerprint`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `30.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 27. testssl.sh Cryptographic Security Engine

- **Tool Name**: testssl.sh Cryptographic Security Engine
- **Tool ID**: `testssl`
- **Category**: TLS
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/testssl_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, ip, url`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `tls_cipher_audit, weak_protocol_detection, cryptographic_vulnerabilities, forward_secrecy_check`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `35.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 28. Nuclei Vulnerability & Exposure Scanner

- **Tool Name**: Nuclei Vulnerability & Exposure Scanner
- **Tool ID**: `nuclei`
- **Category**: VULNERABILITY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/nuclei_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, url, ip`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `cve_detection, misconfiguration_checks, exposed_panels, technology_checks`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `25.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 29. OWASP ZAP Active Vulnerability Assessment Engine

- **Tool Name**: OWASP ZAP Active Vulnerability Assessment Engine
- **Tool ID**: `zap_active_scan`
- **Category**: VULNERABILITY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/zap_active_scan_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `url, domain, subdomain`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `owasp_top_10, xss_testing, sqli_detection, path_traversal, security_headers_audit, zap_active_rules`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `60.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 30. OpenVAS / Greenbone Infrastructure Vulnerability Engine

- **Tool Name**: OpenVAS / Greenbone Infrastructure Vulnerability Engine
- **Tool ID**: `openvas`
- **Category**: VULNERABILITY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/openvas_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `ip, ip_range, host, cidr`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `nvt_execution, network_vulnerability_scan, cve_correlation, cpe_identification`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `60.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 31. Wapiti Web Vulnerability Scanner

- **Tool Name**: Wapiti Web Vulnerability Scanner
- **Tool ID**: `wapiti`
- **Category**: VULNERABILITY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/wapiti_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `url, domain, web_application`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `form_injection_audit, parameter_fuzzing, xss_detection, sqli_detection, ssrf_audit`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `40.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 32. Dalfox Parameter & XSS Analyzer

- **Tool Name**: Dalfox Parameter & XSS Analyzer
- **Tool ID**: `dalfox`
- **Category**: WEB_SECURITY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/dalfox_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, url`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `parameter_analysis, reflected_xss, dom_xss, context_verification`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `20.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 33. Nikto Web Server Security Scanner

- **Tool Name**: Nikto Web Server Security Scanner
- **Tool ID**: `nikto`
- **Category**: WEB_SECURITY
- **Module**: `threat_intelligence`
- **Provider Type**: SCANNER_ENGINE
- **Implementation Location**: `backend/app/modules/threat_intelligence/engines/engines/nikto_engine.py`
- **Backend Service**: `ThreatIntelligenceModule` -> `ThreatIntelEngineAdapter`
- **Frontend Component**: Registered via Provider Registry API (`/api/v1/providers`)
- **API / CLI**: Hybrid (Native Python Async + CLI Subprocess Preflight)
- **Authentication Required**: `False` (Public Feeds / Local Scanners / Configurable API Keys)
- **Environment Variables**: `None required for core; ZAP_API_ENDPOINT, OPENAI_API_KEY optional`
- **Input Types**: `domain, subdomain, url, ip`
- **Output Types**: `NormalizedFinding`, `DiscoveredService`, `DiscoveredEndpoint`, `DiscoveredTechnology`, `Evidence`
- **Capabilities**: `server_misconfiguration, default_files, cgi_testing, insecure_methods`
- **Health Check**: Dynamic runtime via `health_check()`
- **Rate Limits**: `60/min`
- **Timeout**: `30.0s`
- **Retry**: `Exponential backoff (2 attempts)`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

---

## 2. OSINT Public Platform Probers & Deep Engines (335 Providers)

### 1. SpiderFoot Recon

- **Tool Name**: SpiderFoot Recon
- **Tool ID**: `spiderfoot`
- **Category**: AUTOMATION
- **Module**: `osint`
- **Provider Type**: DEEP_ENGINE
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/spiderfoot.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `domain, ip`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `domain, ip, subdomain`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `120/min`
- **Timeout**: `15.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 2. AniDB Anime Database

- **Tool Name**: AniDB Anime Database
- **Tool ID**: `osint_anidb_net`
- **Category**: Anime & Manga
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_anidb_net.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 3. AniList Anime & Manga

- **Tool Name**: AniList Anime & Manga
- **Tool ID**: `osint_anilist`
- **Category**: Anime & Manga
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_anilist.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 4. AniList Community Activity

- **Tool Name**: AniList Community Activity
- **Tool ID**: `osint_anilist_activity`
- **Category**: Anime & Manga
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_anilist_activity.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 5. Anime-Planet Otaku Tracker

- **Tool Name**: Anime-Planet Otaku Tracker
- **Tool ID**: `osint_anime_planet_tracker`
- **Category**: Anime & Manga
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_anime_planet_tracker.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 6. Kitsu Anime Tracker

- **Tool Name**: Kitsu Anime Tracker
- **Tool ID**: `osint_kitsu`
- **Category**: Anime & Manga
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_kitsu.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 7. MangaUpdates (Baka-Updates)

- **Tool Name**: MangaUpdates (Baka-Updates)
- **Tool ID**: `osint_mangaupdates`
- **Category**: Anime & Manga
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_mangaupdates.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 8. MyAnimeList

- **Tool Name**: MyAnimeList
- **Tool ID**: `osint_myanimelist`
- **Category**: Anime & Manga
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_myanimelist.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 9. MyAnimeList Favorites

- **Tool Name**: MyAnimeList Favorites
- **Tool ID**: `osint_myanimelist_favorites`
- **Category**: Anime & Manga
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_myanimelist_favorites.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 10. VNDB Visual Novel Database

- **Tool Name**: VNDB Visual Novel Database
- **Tool ID**: `osint_vndb_org`
- **Category**: Anime & Manga
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_vndb_org.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 11. Bear Blog Minimalist

- **Tool Name**: Bear Blog Minimalist
- **Tool ID**: `osint_bear_blog`
- **Category**: Blogging
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bear_blog.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 12. Mataroa Minimalist Blog

- **Tool Name**: Mataroa Minimalist Blog
- **Tool ID**: `osint_mataroa_blog`
- **Category**: Blogging
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_mataroa_blog.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 13. AO3 Published Works

- **Tool Name**: AO3 Published Works
- **Tool ID**: `osint_archiveofourown_works`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_archiveofourown_works.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 14. Archive of Our Own (AO3)

- **Tool Name**: Archive of Our Own (AO3)
- **Tool ID**: `osint_archiveofourown`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_archiveofourown.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 15. BookCrossing Book Tracker

- **Tool Name**: BookCrossing Book Tracker
- **Tool ID**: `osint_bookcrossing_books`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bookcrossing_books.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 16. BookWyrm (Fediverse Books)

- **Tool Name**: BookWyrm (Fediverse Books)
- **Tool ID**: `osint_bookwyrm_fediverse`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bookwyrm_fediverse.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 17. FanFiction.Net Stories

- **Tool Name**: FanFiction.Net Stories
- **Tool ID**: `osint_fanfiction_net`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_fanfiction_net.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 18. Goodreads Book Catalog

- **Tool Name**: Goodreads Book Catalog
- **Tool ID**: `osint_goodreads`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_goodreads.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 19. Hardcover Book Tracker

- **Tool Name**: Hardcover Book Tracker
- **Tool ID**: `osint_hardcover_books`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hardcover_books.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 20. LibraryThing

- **Tool Name**: LibraryThing
- **Tool ID**: `osint_librarything`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_librarything.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 21. Open Library (Internet Archive)

- **Tool Name**: Open Library (Internet Archive)
- **Tool ID**: `osint_openlibrary`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_openlibrary.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 22. Royal Road Web Fiction

- **Tool Name**: Royal Road Web Fiction
- **Tool ID**: `osint_royalroad`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_royalroad.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 23. The StoryGraph Books

- **Tool Name**: The StoryGraph Books
- **Tool ID**: `osint_storygraph`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_storygraph.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 24. Wattpad Stories & Books

- **Tool Name**: Wattpad Stories & Books
- **Tool ID**: `osint_wattpad`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_wattpad.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 25. Webtoon Comics & Creators

- **Tool Name**: Webtoon Comics & Creators
- **Tool ID**: `osint_webtoons`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_webtoons.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 26. Webtoons Comic Series

- **Tool Name**: Webtoons Comic Series
- **Tool ID**: `osint_webtoons_series`
- **Category**: Books & Literature
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_webtoons_series.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 27. 365Chess

- **Tool Name**: 365Chess
- **Tool ID**: `osint_365chess`
- **Category**: Chess
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_365chess.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 28. Chess Tempo

- **Tool Name**: Chess Tempo
- **Tool ID**: `osint_chesstempo`
- **Category**: Chess
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_chesstempo.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 29. Chess.com

- **Tool Name**: Chess.com
- **Tool ID**: `osint_chess_com`
- **Category**: Chess
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_chess_com.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 30. Chess.com Tournament History

- **Tool Name**: Chess.com Tournament History
- **Tool ID**: `osint_chess_com_tournaments`
- **Category**: Chess
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_chess_com_tournaments.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 31. Chessable

- **Tool Name**: Chessable
- **Tool ID**: `osint_chessable`
- **Category**: Chess
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_chessable.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 32. English Chess Federation (ECF)

- **Tool Name**: English Chess Federation (ECF)
- **Tool ID**: `osint_ecf_chess_ratings`
- **Category**: Chess
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_ecf_chess_ratings.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 33. FIDE International Chess Federation

- **Tool Name**: FIDE International Chess Federation
- **Tool ID**: `osint_fide_profile`
- **Category**: Chess
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_fide_profile.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 34. GameKnot Chess

- **Tool Name**: GameKnot Chess
- **Tool ID**: `osint_gameknot`
- **Category**: Chess
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_gameknot.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 35. Lichess

- **Tool Name**: Lichess
- **Tool ID**: `osint_lichess`
- **Category**: Chess
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_lichess.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 36. Lichess Games & Puzzles

- **Tool Name**: Lichess Games & Puzzles
- **Tool ID**: `osint_lichess_activity`
- **Category**: Chess
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_lichess_activity.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 37. RedHotPawn Chess

- **Tool Name**: RedHotPawn Chess
- **Tool ID**: `osint_redhotpawn`
- **Category**: Chess
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_redhotpawn.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 38. US Chess Federation (USCF)

- **Tool Name**: US Chess Federation (USCF)
- **Tool ID**: `osint_uschess_ratings`
- **Category**: Chess
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_uschess_ratings.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 39. Buy Me a Coffee

- **Tool Name**: Buy Me a Coffee
- **Tool ID**: `osint_buymeacoffee`
- **Category**: Creator & Media
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_buymeacoffee.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 40. Dailymotion

- **Tool Name**: Dailymotion
- **Tool ID**: `osint_dailymotion`
- **Category**: Creator & Media
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_dailymotion.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 41. Ko-fi Support Creators

- **Tool Name**: Ko-fi Support Creators
- **Tool ID**: `osint_kofi`
- **Category**: Creator & Media
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_kofi.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 42. Patreon Creator

- **Tool Name**: Patreon Creator
- **Tool ID**: `osint_patreon`
- **Category**: Creator & Media
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_patreon.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 43. Patreon Membership Tiers

- **Tool Name**: Patreon Membership Tiers
- **Tool ID**: `osint_patreon_tiers`
- **Category**: Creator & Media
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_patreon_tiers.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 44. Rumble Video

- **Tool Name**: Rumble Video
- **Tool ID**: `osint_rumble`
- **Category**: Creator & Media
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_rumble.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 45. Vimeo Cinema Portfolio

- **Tool Name**: Vimeo Cinema Portfolio
- **Tool ID**: `osint_vimeo_portfolio_showcase`
- **Category**: Creator & Media
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_vimeo_portfolio_showcase.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 46. Vimeo Video Showcase

- **Tool Name**: Vimeo Video Showcase
- **Tool ID**: `osint_vimeo`
- **Category**: Creator & Media
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_vimeo.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 47. YouTube Channel

- **Tool Name**: YouTube Channel
- **Tool ID**: `osint_youtube`
- **Category**: Creator & Media
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_youtube.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 48. YouTube Creator Posts

- **Tool Name**: YouTube Creator Posts
- **Tool ID**: `osint_youtube_community_tab`
- **Category**: Creator & Media
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_youtube_community_tab.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 49. Etherscan ENS Name / Account

- **Tool Name**: Etherscan ENS Name / Account
- **Tool ID**: `osint_etherscan_name`
- **Category**: Crypto & Web3
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_etherscan_name.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 50. Farcaster Warpcast Web3

- **Tool Name**: Farcaster Warpcast Web3
- **Tool ID**: `osint_farcaster_warpcast`
- **Category**: Crypto & Web3
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_farcaster_warpcast.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 51. Foundation Web3 Creator

- **Tool Name**: Foundation Web3 Creator
- **Tool ID**: `osint_foundation_app_art`
- **Category**: Crypto & Web3
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_foundation_app_art.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 52. Magic Eden Solana NFT

- **Tool Name**: Magic Eden Solana NFT
- **Tool ID**: `osint_magic_eden_solana`
- **Category**: Crypto & Web3
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_magic_eden_solana.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 53. Mirror.xyz Web3 Publishing

- **Tool Name**: Mirror.xyz Web3 Publishing
- **Tool ID**: `osint_mirror_xyz`
- **Category**: Crypto & Web3
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_mirror_xyz.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 54. OpenSea NFT Marketplace

- **Tool Name**: OpenSea NFT Marketplace
- **Tool ID**: `osint_opensea`
- **Category**: Crypto & Web3
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_opensea.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 55. Rarible Community NFT

- **Tool Name**: Rarible Community NFT
- **Tool ID**: `osint_rarible`
- **Category**: Crypto & Web3
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_rarible.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 56. SuperRare Curated Digital Art

- **Tool Name**: SuperRare Curated Digital Art
- **Tool ID**: `osint_superrare_nft`
- **Category**: Crypto & Web3
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_superrare_nft.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 57. Zora Web3 Network

- **Tool Name**: Zora Web3 Network
- **Tool ID**: `osint_zora_creator`
- **Category**: Crypto & Web3
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_zora_creator.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 58. ArtStation Portfolio

- **Tool Name**: ArtStation Portfolio
- **Tool ID**: `osint_artstation`
- **Category**: Design & Art
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_artstation.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 59. Behance Portfolio (Adobe)

- **Tool Name**: Behance Portfolio (Adobe)
- **Tool ID**: `osint_behance`
- **Category**: Design & Art
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_behance.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 60. Cara Art & Portfolio

- **Tool Name**: Cara Art & Portfolio
- **Tool ID**: `osint_cara_artists`
- **Category**: Design & Art
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_cara_artists.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 61. Cara Creator Gallery

- **Tool Name**: Cara Creator Gallery
- **Tool ID**: `osint_cara_app_gallery`
- **Category**: Design & Art
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_cara_app_gallery.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 62. DeviantArt Studio

- **Tool Name**: DeviantArt Studio
- **Tool ID**: `osint_deviantart`
- **Category**: Design & Art
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_deviantart.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 63. Dribbble Designers

- **Tool Name**: Dribbble Designers
- **Tool ID**: `osint_dribbble`
- **Category**: Design & Art
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_dribbble.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 64. Ello Art Community

- **Tool Name**: Ello Art Community
- **Tool ID**: `osint_ello_co`
- **Category**: Design & Art
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_ello_co.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 65. Mastodon Art Community

- **Tool Name**: Mastodon Art Community
- **Tool ID**: `osint_mastodon_art_gallery`
- **Category**: Design & Art
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_mastodon_art_gallery.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 66. AtCoder

- **Tool Name**: AtCoder
- **Tool ID**: `osint_atcoder`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_atcoder.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 67. Bitbucket Cloud

- **Tool Name**: Bitbucket Cloud
- **Tool ID**: `osint_bitbucket`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bitbucket.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 68. Bugcrowd Hall of Fame

- **Tool Name**: Bugcrowd Hall of Fame
- **Tool ID**: `osint_bugcrowd_hall_of_fame`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bugcrowd_hall_of_fame.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 69. Bugcrowd Security Researcher

- **Tool Name**: Bugcrowd Security Researcher
- **Tool ID**: `osint_bugcrowd`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bugcrowd.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 70. CTFtime Competitive Security

- **Tool Name**: CTFtime Competitive Security
- **Tool ID**: `osint_ctftime`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_ctftime.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 71. CTFtime Team Association

- **Tool Name**: CTFtime Team Association
- **Tool ID**: `osint_ctftime_teams`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_ctftime_teams.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 72. CodePen

- **Tool Name**: CodePen
- **Tool ID**: `osint_codepen`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_codepen.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 73. Codeberg Git

- **Tool Name**: Codeberg Git
- **Tool ID**: `osint_codeberg`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_codeberg.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 74. Codeforces

- **Tool Name**: Codeforces
- **Tool ID**: `osint_codeforces`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_codeforces.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 75. Coderwall

- **Tool Name**: Coderwall
- **Tool ID**: `osint_coderwall`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_coderwall.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 76. Codewars

- **Tool Name**: Codewars
- **Tool ID**: `osint_codewars`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_codewars.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 77. DataCamp Data Scientist

- **Tool Name**: DataCamp Data Scientist
- **Tool ID**: `osint_datacamp_learn`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_datacamp_learn.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 78. Dev.to Community

- **Tool Name**: Dev.to Community
- **Tool ID**: `osint_devto`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_devto.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 79. DockerHub

- **Tool Name**: DockerHub
- **Tool ID**: `osint_dockerhub`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_dockerhub.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 80. Exercism

- **Tool Name**: Exercism
- **Tool ID**: `osint_exercism`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_exercism.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 81. GitHub

- **Tool Name**: GitHub
- **Tool ID**: `osint_github`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_github.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 82. GitHub Repositories Showcase

- **Tool Name**: GitHub Repositories Showcase
- **Tool ID**: `osint_github_repositories`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_github_repositories.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 83. GitLab

- **Tool Name**: GitLab
- **Tool ID**: `osint_gitlab`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_gitlab.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 84. GitLab Public Projects

- **Tool Name**: GitLab Public Projects
- **Tool ID**: `osint_gitlab_projects`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_gitlab_projects.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 85. Glitch Coding

- **Tool Name**: Glitch Coding
- **Tool ID**: `osint_glitch`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_glitch.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 86. Hack The Box

- **Tool Name**: Hack The Box
- **Tool ID**: `osint_hackthebox`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hackthebox.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 87. HackerEarth Developer

- **Tool Name**: HackerEarth Developer
- **Tool ID**: `osint_hackerearth`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hackerearth.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 88. HackerNews

- **Tool Name**: HackerNews
- **Tool ID**: `osint_hackernews`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hackernews.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 89. HackerOne Bug Bounty

- **Tool Name**: HackerOne Bug Bounty
- **Tool ID**: `osint_hackerone`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hackerone.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 90. HackerOne Public Directory

- **Tool Name**: HackerOne Public Directory
- **Tool ID**: `osint_hackerone_hackers`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hackerone_hackers.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 91. HackerRank

- **Tool Name**: HackerRank
- **Tool ID**: `osint_hackerrank`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hackerrank.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 92. Hashnode Tech Blog

- **Tool Name**: Hashnode Tech Blog
- **Tool ID**: `osint_hashnode`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hashnode.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 93. Hugging Face AI

- **Tool Name**: Hugging Face AI
- **Tool ID**: `osint_huggingface`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_huggingface.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 94. Intigriti Ethical Hackers

- **Tool Name**: Intigriti Ethical Hackers
- **Tool ID**: `osint_intigriti`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_intigriti.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 95. Intigriti Leaderboard Rank

- **Tool Name**: Intigriti Leaderboard Rank
- **Tool ID**: `osint_intigriti_leaderboard`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_intigriti_leaderboard.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 96. JSFiddle

- **Tool Name**: JSFiddle
- **Tool ID**: `osint_jsfiddle`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_jsfiddle.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 97. Kaggle AI & Data

- **Tool Name**: Kaggle AI & Data
- **Tool ID**: `osint_kaggle`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_kaggle.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 98. LeetCode

- **Tool Name**: LeetCode
- **Tool ID**: `osint_leetcode`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_leetcode.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 99. Observable HQ

- **Tool Name**: Observable HQ
- **Tool ID**: `osint_observable`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_observable.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 100. Open Hub (Black Duck)

- **Tool Name**: Open Hub (Black Duck)
- **Tool ID**: `osint_openhub`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_openhub.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 101. Pastebin

- **Tool Name**: Pastebin
- **Tool ID**: `osint_pastebin`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_pastebin.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 102. Replit

- **Tool Name**: Replit
- **Tool ID**: `osint_replit`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_replit.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 103. Root-Me Challenges Solved

- **Tool Name**: Root-Me Challenges Solved
- **Tool ID**: `osint_root_me_stats`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_root_me_stats.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 104. Root-Me Hacking Challenges

- **Tool Name**: Root-Me Hacking Challenges
- **Tool ID**: `osint_root_me`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_root_me.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 105. Scrimba Coding

- **Tool Name**: Scrimba Coding
- **Tool ID**: `osint_scrimba`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_scrimba.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 106. SourceForge

- **Tool Name**: SourceForge
- **Tool ID**: `osint_sourceforge`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_sourceforge.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 107. SourceHut Software Forge

- **Tool Name**: SourceHut Software Forge
- **Tool ID**: `osint_sourcehut`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_sourcehut.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 108. Stack Exchange Network

- **Tool Name**: Stack Exchange Network
- **Tool ID**: `osint_stackexchange`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_stackexchange.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 109. Topcoder

- **Tool Name**: Topcoder
- **Tool ID**: `osint_topcoder`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_topcoder.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 110. TryHackMe Cyber Labs

- **Tool Name**: TryHackMe Cyber Labs
- **Tool ID**: `osint_tryhackme`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_tryhackme.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 111. Ubuntu Launchpad

- **Tool Name**: Ubuntu Launchpad
- **Tool ID**: `osint_launchpad`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_launchpad.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 112. WeChall Challenge Profiles

- **Tool Name**: WeChall Challenge Profiles
- **Tool ID**: `osint_wechall_profiles`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_wechall_profiles.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 113. WeChall Challenge Sites

- **Tool Name**: WeChall Challenge Sites
- **Tool ID**: `osint_wechall`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_wechall.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 114. freeCodeCamp

- **Tool Name**: freeCodeCamp
- **Tool ID**: `osint_freecodecamp`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_freecodecamp.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 115. picoCTF Learning Platform

- **Tool Name**: picoCTF Learning Platform
- **Tool ID**: `osint_picoctf`
- **Category**: Developer & Tech
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_picoctf.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 116. Brilliant.org STEM

- **Tool Name**: Brilliant.org STEM
- **Tool ID**: `osint_brilliant_org`
- **Category**: Education
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_brilliant_org.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 117. Codecademy Learner

- **Tool Name**: Codecademy Learner
- **Tool ID**: `osint_codecademy`
- **Category**: Education
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_codecademy.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 118. Khan Academy

- **Tool Name**: Khan Academy
- **Tool ID**: `osint_khan_academy`
- **Category**: Education
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_khan_academy.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 119. Quizlet Flashcards

- **Tool Name**: Quizlet Flashcards
- **Tool ID**: `osint_quizlet`
- **Category**: Education
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_quizlet.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 120. Scratch (MIT Media Lab)

- **Tool Name**: Scratch (MIT Media Lab)
- **Tool ID**: `osint_scratch_mit`
- **Category**: Education
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_scratch_mit.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 121. SoloLearn Mobile Coding

- **Tool Name**: SoloLearn Mobile Coding
- **Tool ID**: `osint_sololearn`
- **Category**: Education
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_sololearn.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 122. Team Treehouse Coding

- **Tool Name**: Team Treehouse Coding
- **Tool ID**: `osint_treehouse_team`
- **Category**: Education
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_treehouse_team.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 123. TypeRacer Typist

- **Tool Name**: TypeRacer Typist
- **Tool ID**: `osint_typeracer`
- **Category**: Education
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_typeracer.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 124. edX Online Courses

- **Tool Name**: edX Online Courses
- **Tool ID**: `osint_edx_org`
- **Category**: Education
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_edx_org.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 125. Criticker Movie Ratings

- **Tool Name**: Criticker Movie Ratings
- **Tool ID**: `osint_criticker_films`
- **Category**: Film & TV
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_criticker_films.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 126. Letterboxd Film Diary

- **Tool Name**: Letterboxd Film Diary
- **Tool ID**: `osint_letterboxd`
- **Category**: Film & TV
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_letterboxd.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 127. Letterboxd Film Lists

- **Tool Name**: Letterboxd Film Lists
- **Tool ID**: `osint_letterboxd_lists`
- **Category**: Film & TV
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_letterboxd_lists.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 128. Serializd TV Series Diary

- **Tool Name**: Serializd TV Series Diary
- **Tool ID**: `osint_serializd_tv`
- **Category**: Film & TV
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_serializd_tv.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 129. TV Time Series Tracker

- **Tool Name**: TV Time Series Tracker
- **Tool ID**: `osint_tv_time_watch`
- **Category**: Film & TV
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_tv_time_watch.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 130. TheMovieDB (TMDB)

- **Tool Name**: TheMovieDB (TMDB)
- **Tool ID**: `osint_tmdb_movies`
- **Category**: Film & TV
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_tmdb_movies.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 131. Trakt.tv History Stream

- **Tool Name**: Trakt.tv History Stream
- **Tool ID**: `osint_trakt_history_user`
- **Category**: Film & TV
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_trakt_history_user.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 132. Trakt.tv TV & Movie Tracker

- **Tool Name**: Trakt.tv TV & Movie Tracker
- **Tool ID**: `osint_trakt_tv`
- **Category**: Film & TV
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_trakt_tv.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 133. AVS Forum Home Theater

- **Tool Name**: AVS Forum Home Theater
- **Tool ID**: `osint_avsforum_hometheater`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_avsforum_hometheater.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 134. Amino Communities

- **Tool Name**: Amino Communities
- **Tool ID**: `osint_amino_apps`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_amino_apps.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 135. Bogleheads Financial Forum

- **Tool Name**: Bogleheads Financial Forum
- **Tool ID**: `osint_bogleheads_invest`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bogleheads_invest.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 136. Discourse Foundation

- **Tool Name**: Discourse Foundation
- **Tool ID**: `osint_discourse_org_community`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_discourse_org_community.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 137. Discourse Meta Community

- **Tool Name**: Discourse Meta Community
- **Tool ID**: `osint_discourse_meta`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_discourse_meta.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 138. Lemmy.ml Open Discussion

- **Tool Name**: Lemmy.ml Open Discussion
- **Tool ID**: `osint_lemmy_ml_community`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_lemmy_ml_community.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 139. Lemmy.world Fediverse Forum

- **Tool Name**: Lemmy.world Fediverse Forum
- **Tool ID**: `osint_lemmy_world`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_lemmy_world.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 140. Linus Tech Tips Forum

- **Tool Name**: Linus Tech Tips Forum
- **Tool ID**: `osint_linustech_community`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_linustech_community.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 141. Lobste.rs Computing

- **Tool Name**: Lobste.rs Computing
- **Tool ID**: `osint_lobsters`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_lobsters.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 142. Overclock.net Hardware PC

- **Tool Name**: Overclock.net Hardware PC
- **Tool ID**: `osint_overclock_hardware`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_overclock_hardware.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 143. Product Hunt

- **Tool Name**: Product Hunt
- **Tool ID**: `osint_producthunt`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_producthunt.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 144. Quora Q&A

- **Tool Name**: Quora Q&A
- **Tool ID**: `osint_quora`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_quora.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 145. Slashdot

- **Tool Name**: Slashdot
- **Tool ID**: `osint_slashdot`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_slashdot.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 146. Tom's Hardware PC Builder

- **Tool Name**: Tom's Hardware PC Builder
- **Tool ID**: `osint_tomshardware_pc`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_tomshardware_pc.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 147. XDA Developers Forum

- **Tool Name**: XDA Developers Forum
- **Tool ID**: `osint_xda_developers`
- **Category**: Forums & Communities
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_xda_developers.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 148. Apex Legends Tracker

- **Tool Name**: Apex Legends Tracker
- **Tool ID**: `osint_apex_tracker_stats`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_apex_tracker_stats.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 149. Armor Games

- **Tool Name**: Armor Games
- **Tool ID**: `osint_armorgames`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_armorgames.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 150. BoardGameGeek

- **Tool Name**: BoardGameGeek
- **Tool ID**: `osint_boardgamegeek`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_boardgamegeek.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 151. BoardGameGeek Collection

- **Tool Name**: BoardGameGeek Collection
- **Tool ID**: `osint_boardgamegeek_collection_user`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_boardgamegeek_collection_user.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 152. CurseForge Creator Studio

- **Tool Name**: CurseForge Creator Studio
- **Tool ID**: `osint_curseforge_creators`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_curseforge_creators.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 153. CurseForge Mods & Addons

- **Tool Name**: CurseForge Mods & Addons
- **Tool ID**: `osint_curseforge`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_curseforge.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 154. Destiny Tracker Guardian

- **Tool Name**: Destiny Tracker Guardian
- **Tool ID**: `osint_destiny_tracker`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_destiny_tracker.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 155. Dotabuff

- **Tool Name**: Dotabuff
- **Tool ID**: `osint_dotabuff`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_dotabuff.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 156. FACEIT Esports

- **Tool Name**: FACEIT Esports
- **Tool ID**: `osint_faceit`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_faceit.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 157. Fortnite Tracker Player

- **Tool Name**: Fortnite Tracker Player
- **Tool ID**: `osint_fortnite_tracker_stats`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_fortnite_tracker_stats.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 158. GOG Galaxy

- **Tool Name**: GOG Galaxy
- **Tool ID**: `osint_gog`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_gog.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 159. Game Jolt

- **Tool Name**: Game Jolt
- **Tool ID**: `osint_gamejolt`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_gamejolt.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 160. GameFAQs Walkthroughs & Boards

- **Tool Name**: GameFAQs Walkthroughs & Boards
- **Tool ID**: `osint_gamefaqs_guides`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_gamefaqs_guides.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 161. GeoGuessr Explorer

- **Tool Name**: GeoGuessr Explorer
- **Tool ID**: `osint_geoguessr`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_geoguessr.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 162. HLTV Counter-Strike Hub

- **Tool Name**: HLTV Counter-Strike Hub
- **Tool ID**: `osint_hltv_esports`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hltv_esports.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 163. Habbo Hotel Community

- **Tool Name**: Habbo Hotel Community
- **Tool ID**: `osint_habbo_hotel`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_habbo_hotel.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 164. Hypixel Minecraft Network

- **Tool Name**: Hypixel Minecraft Network
- **Tool ID**: `osint_hypixel_player`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hypixel_player.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 165. IGN Boards Gamers

- **Tool Name**: IGN Boards Gamers
- **Tool ID**: `osint_ign_boards_gamer`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_ign_boards_gamer.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 166. Itch.io Developer Logs

- **Tool Name**: Itch.io Developer Logs
- **Tool ID**: `osint_itch_io_devlog`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_itch_io_devlog.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 167. Itch.io Indie Games

- **Tool Name**: Itch.io Indie Games
- **Tool ID**: `osint_itch_io`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_itch_io.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 168. Kongregate

- **Tool Name**: Kongregate
- **Tool ID**: `osint_kongregate`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_kongregate.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 169. ModDB

- **Tool Name**: ModDB
- **Tool ID**: `osint_moddb`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_moddb.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 170. Modrinth Open Source Mods

- **Tool Name**: Modrinth Open Source Mods
- **Tool ID**: `osint_modrinth`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_modrinth.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 171. Modrinth Released Mods

- **Tool Name**: Modrinth Released Mods
- **Tool ID**: `osint_modrinth_author_mods`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_modrinth_author_mods.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 172. NameMC Minecraft

- **Tool Name**: NameMC Minecraft
- **Tool ID**: `osint_namemc_minecraft`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_namemc_minecraft.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 173. NameMC Server Profile

- **Tool Name**: NameMC Server Profile
- **Tool ID**: `osint_namemc_server_staff`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_namemc_server_staff.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 174. Newgrounds Creator

- **Tool Name**: Newgrounds Creator
- **Tool ID**: `osint_newgrounds`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_newgrounds.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 175. Nexus Mods

- **Tool Name**: Nexus Mods
- **Tool ID**: `osint_nexusmods`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_nexusmods.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 176. OP.GG League of Legends

- **Tool Name**: OP.GG League of Legends
- **Tool ID**: `osint_op_gg`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_op_gg.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 177. Old School RuneScape Hiscores

- **Tool Name**: Old School RuneScape Hiscores
- **Tool ID**: `osint_runescape_hiscores`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_runescape_hiscores.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 178. Planet Minecraft

- **Tool Name**: Planet Minecraft
- **Tool ID**: `osint_planetminecraft`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_planetminecraft.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 179. Planet Minecraft World Maps

- **Tool Name**: Planet Minecraft World Maps
- **Tool ID**: `osint_planetminecraft_maps`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_planetminecraft_maps.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 180. Pokemon Showdown

- **Tool Name**: Pokemon Showdown
- **Tool ID**: `osint_pokemon_showdown`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_pokemon_showdown.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 181. Rainbow Six Siege Tracker

- **Tool Name**: Rainbow Six Siege Tracker
- **Tool ID**: `osint_r6tracker_stats`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_r6tracker_stats.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 182. Retro Gamer Zone

- **Tool Name**: Retro Gamer Zone
- **Tool ID**: `osint_retro_achieve_forum`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_retro_achieve_forum.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 183. RetroAchievements

- **Tool Name**: RetroAchievements
- **Tool ID**: `osint_retroachievements`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_retroachievements.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 184. Roblox Player

- **Tool Name**: Roblox Player
- **Tool ID**: `osint_roblox`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_roblox.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 185. Rocket League Tracker

- **Tool Name**: Rocket League Tracker
- **Tool ID**: `osint_rocketleague_stats`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_rocketleague_stats.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 186. Rolimons Roblox Trader

- **Tool Name**: Rolimons Roblox Trader
- **Tool ID**: `osint_roblox_trade`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_roblox_trade.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 187. Speedrun Game Guides

- **Tool Name**: Speedrun Game Guides
- **Tool ID**: `osint_speedrun_guides_author`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_speedrun_guides_author.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 188. Speedrun.com

- **Tool Name**: Speedrun.com
- **Tool ID**: `osint_speedrun_com`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_speedrun_com.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 189. SpigotMC Minecraft Dev

- **Tool Name**: SpigotMC Minecraft Dev
- **Tool ID**: `osint_spigotmc`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_spigotmc.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 190. SpigotMC Plugin Author

- **Tool Name**: SpigotMC Plugin Author
- **Tool ID**: `osint_spigotmc_plugins`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_spigotmc_plugins.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 191. Start.gg Esports Tournaments

- **Tool Name**: Start.gg Esports Tournaments
- **Tool ID**: `osint_smash_gg_start`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_smash_gg_start.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 192. Steam Badges & Level

- **Tool Name**: Steam Badges & Level
- **Tool ID**: `osint_steam_badges_showcase`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_steam_badges_showcase.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 193. Steam Community

- **Tool Name**: Steam Community
- **Tool ID**: `osint_steam`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_steam.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 194. Steam Inventory Showcase

- **Tool Name**: Steam Inventory Showcase
- **Tool ID**: `osint_steam_inventory_showcase`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_steam_inventory_showcase.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 195. Tibia MMORPG

- **Tool Name**: Tibia MMORPG
- **Tool ID**: `osint_tibia_char`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_tibia_char.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 196. Tracker Network (Tracker.gg)

- **Tool Name**: Tracker Network (Tracker.gg)
- **Tool ID**: `osint_tracker_gg`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_tracker_gg.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 197. Valorant Tracker Agent

- **Tool Name**: Valorant Tracker Agent
- **Tool ID**: `osint_valorant_tracker_stats`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_valorant_tracker_stats.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 198. Vimm's Lair Gaming

- **Tool Name**: Vimm's Lair Gaming
- **Tool ID**: `osint_vimm_lair`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_vimm_lair.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 199. Warframe Market Trader

- **Tool Name**: Warframe Market Trader
- **Tool ID**: `osint_warframe_market_trader`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_warframe_market_trader.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 200. osu! Beatmap Mapper

- **Tool Name**: osu! Beatmap Mapper
- **Tool ID**: `osint_osu_beatmap_creators`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_osu_beatmap_creators.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 201. osu! Rhythm Game

- **Tool Name**: osu! Rhythm Game
- **Tool ID**: `osint_osu_game`
- **Category**: Gaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_osu_game.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 202. Couchsurfing Travel

- **Tool Name**: Couchsurfing Travel
- **Tool ID**: `osint_couchsurfing`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_couchsurfing.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 203. FlightAware Aviation

- **Tool Name**: FlightAware Aviation
- **Tool ID**: `osint_flightaware`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_flightaware.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 204. Flightradar24 Aviation Feeders

- **Tool Name**: Flightradar24 Aviation Feeders
- **Tool ID**: `osint_flightradar24`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_flightradar24.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 205. FlyerTalk Frequent Flyer

- **Tool Name**: FlyerTalk Frequent Flyer
- **Tool ID**: `osint_flyertalk_travel`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_flyertalk_travel.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 206. Geocaching Global GPS Hunt

- **Tool Name**: Geocaching Global GPS Hunt
- **Tool ID**: `osint_geocaching`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_geocaching.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 207. Hackaday Hardware & Engineering

- **Tool Name**: Hackaday Hardware & Engineering
- **Tool ID**: `osint_hackaday`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hackaday.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 208. Hackster.io Hardware Projects

- **Tool Name**: Hackster.io Hardware Projects
- **Tool ID**: `osint_hackster_io`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hackster_io.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 209. Instructables DIY

- **Tool Name**: Instructables DIY
- **Tool ID**: `osint_instructables`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_instructables.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 210. Instructables Makers Contest

- **Tool Name**: Instructables Makers Contest
- **Tool ID**: `osint_instructables_makers`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_instructables_makers.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 211. Printables (Prusa Research)

- **Tool Name**: Printables (Prusa Research)
- **Tool ID**: `osint_printables`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_printables.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 212. Ravelry Fiber Arts

- **Tool Name**: Ravelry Fiber Arts
- **Tool ID**: `osint_ravelry_knitting`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_ravelry_knitting.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 213. Thingiverse 3D Models

- **Tool Name**: Thingiverse 3D Models
- **Tool ID**: `osint_thingiverse`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_thingiverse.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 214. Thingiverse Maker Collections

- **Tool Name**: Thingiverse Maker Collections
- **Tool ID**: `osint_thingiverse_collections`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_thingiverse_collections.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 215. TripAdvisor Traveler

- **Tool Name**: TripAdvisor Traveler
- **Tool ID**: `osint_tripadvisor_reviews`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_tripadvisor_reviews.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 216. Untappd Craft Beer Social

- **Tool Name**: Untappd Craft Beer Social
- **Tool ID**: `osint_untappd`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_untappd.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 217. Vivino Wine Community

- **Tool Name**: Vivino Wine Community
- **Tool ID**: `osint_vivino`
- **Category**: Hobbies & Lifestyle
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_vivino.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 218. theHarvester OSINT Engine

- **Tool Name**: theHarvester OSINT Engine
- **Tool ID**: `theharvester`
- **Category**: IDENTITY_OSINT
- **Module**: `osint`
- **Provider Type**: DEEP_ENGINE
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/theharvester.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `domain, email`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `email, domain, person`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `120/min`
- **Timeout**: `15.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 219. Visual Intelligence & EXIF Engine

- **Tool Name**: Visual Intelligence & EXIF Engine
- **Tool ID**: `image_osint`
- **Category**: IMAGE_METADATA
- **Module**: `osint`
- **Provider Type**: DEEP_ENGINE
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/image_osint.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `image, url, person`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `image, exif, person`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `120/min`
- **Timeout**: `15.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 220. Duolingo Language Learner

- **Tool Name**: Duolingo Language Learner
- **Tool ID**: `osint_duolingo`
- **Category**: Language Learning
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_duolingo.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 221. Memrise Vocabulary

- **Tool Name**: Memrise Vocabulary
- **Tool ID**: `osint_memrise`
- **Category**: Language Learning
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_memrise.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 222. Beacons.ai Creator Bio

- **Tool Name**: Beacons.ai Creator Bio
- **Tool ID**: `osint_beacons_ai`
- **Category**: Link in Bio
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_beacons_ai.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 223. Bento.me Personal Bio

- **Tool Name**: Bento.me Personal Bio
- **Tool ID**: `osint_bento_me`
- **Category**: Link in Bio
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bento_me.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 224. Bio.link Creator Page

- **Tool Name**: Bio.link Creator Page
- **Tool ID**: `osint_bio_link`
- **Category**: Link in Bio
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bio_link.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 225. Linktree External Destinations

- **Tool Name**: Linktree External Destinations
- **Tool ID**: `osint_linktree_socials`
- **Category**: Link in Bio
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_linktree_socials.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 226. Linktree Link-in-Bio

- **Tool Name**: Linktree Link-in-Bio
- **Tool ID**: `osint_linktree`
- **Category**: Link in Bio
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_linktree.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 227. Snipfeed Monetization

- **Tool Name**: Snipfeed Monetization
- **Tool ID**: `osint_snipfeed`
- **Category**: Link in Bio
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_snipfeed.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 228. Taplink Bio Links

- **Tool Name**: Taplink Bio Links
- **Tool ID**: `osint_taplink_cc`
- **Category**: Link in Bio
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_taplink_cc.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 229. Kick Live Streaming

- **Tool Name**: Kick Live Streaming
- **Tool ID**: `osint_kick_streaming`
- **Category**: Live Streaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_kick_streaming.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 230. Kick VOD Recordings

- **Tool Name**: Kick VOD Recordings
- **Tool ID**: `osint_kick_vods`
- **Category**: Live Streaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_kick_vods.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 231. Twitch Interactive

- **Tool Name**: Twitch Interactive
- **Tool ID**: `osint_twitch`
- **Category**: Live Streaming
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_twitch.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 232. Creative Market Assets

- **Tool Name**: Creative Market Assets
- **Tool ID**: `osint_creative_market`
- **Category**: Marketplaces & Commerce
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_creative_market.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 233. Envato Market (ThemeForest)

- **Tool Name**: Envato Market (ThemeForest)
- **Tool ID**: `osint_envato_market`
- **Category**: Marketplaces & Commerce
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_envato_market.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 234. Etsy Handmade Marketplace

- **Tool Name**: Etsy Handmade Marketplace
- **Tool ID**: `osint_etsy_shop`
- **Category**: Marketplaces & Commerce
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_etsy_shop.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 235. Fiverr Freelance Services

- **Tool Name**: Fiverr Freelance Services
- **Tool ID**: `osint_fiverr`
- **Category**: Marketplaces & Commerce
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_fiverr.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 236. Freelancer.com Talent

- **Tool Name**: Freelancer.com Talent
- **Tool ID**: `osint_freelancer_pro`
- **Category**: Marketplaces & Commerce
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_freelancer_pro.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 237. Gumroad Digital Store

- **Tool Name**: Gumroad Digital Store
- **Tool ID**: `osint_gumroad`
- **Category**: Marketplaces & Commerce
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_gumroad.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 238. Redbubble Independent Artists

- **Tool Name**: Redbubble Independent Artists
- **Tool ID**: `osint_redbubble_shop`
- **Category**: Marketplaces & Commerce
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_redbubble_shop.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 239. Society6 Art & Decor

- **Tool Name**: Society6 Art & Decor
- **Tool ID**: `osint_society6_home`
- **Category**: Marketplaces & Commerce
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_society6_home.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 240. Stan Store Creator Shop

- **Tool Name**: Stan Store Creator Shop
- **Tool ID**: `osint_stan_store`
- **Category**: Marketplaces & Commerce
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_stan_store.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 241. TeePublic Artist Store

- **Tool Name**: TeePublic Artist Store
- **Tool ID**: `osint_teepublic_design`
- **Category**: Marketplaces & Commerce
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_teepublic_design.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 242. Telegram Messenger

- **Tool Name**: Telegram Messenger
- **Tool ID**: `osint_telegram`
- **Category**: Messaging
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_telegram.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 243. Audiomack Hip-Hop & Music

- **Tool Name**: Audiomack Hip-Hop & Music
- **Tool ID**: `osint_audiomack`
- **Category**: Music
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_audiomack.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 244. Audius Decentralized Music

- **Tool Name**: Audius Decentralized Music
- **Tool ID**: `osint_audius_music`
- **Category**: Music
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_audius_music.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 245. Bandcamp Artist

- **Tool Name**: Bandcamp Artist
- **Tool ID**: `osint_bandcamp`
- **Category**: Music
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bandcamp.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 246. Bandcamp Discography & Vinyl

- **Tool Name**: Bandcamp Discography & Vinyl
- **Tool ID**: `osint_bandcamp_discography`
- **Category**: Music
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bandcamp_discography.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 247. Discogs Vinyl & CD Database

- **Tool Name**: Discogs Vinyl & CD Database
- **Tool ID**: `osint_discogs_community`
- **Category**: Music
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_discogs_community.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 248. Last.fm Music Scrobbler

- **Tool Name**: Last.fm Music Scrobbler
- **Tool ID**: `osint_last_fm`
- **Category**: Music
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_last_fm.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 249. Last.fm Top Artists Telemetry

- **Tool Name**: Last.fm Top Artists Telemetry
- **Tool ID**: `osint_last_fm_top_artists`
- **Category**: Music
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_last_fm_top_artists.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 250. Mixcloud DJ & Radio

- **Tool Name**: Mixcloud DJ & Radio
- **Tool ID**: `osint_mixcloud`
- **Category**: Music
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_mixcloud.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 251. ReverbNation Indie Artists

- **Tool Name**: ReverbNation Indie Artists
- **Tool ID**: `osint_reverbnation`
- **Category**: Music
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_reverbnation.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 252. Smule Social Karaoke

- **Tool Name**: Smule Social Karaoke
- **Tool ID**: `osint_smule`
- **Category**: Music
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_smule.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 253. SoundCloud Music

- **Tool Name**: SoundCloud Music
- **Tool ID**: `osint_soundcloud`
- **Category**: Music
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_soundcloud.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 254. SoundCloud Track Catalog

- **Tool Name**: SoundCloud Track Catalog
- **Tool ID**: `osint_soundcloud_tracks`
- **Category**: Music
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_soundcloud_tracks.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 255. Shodan Intelligence

- **Tool Name**: Shodan Intelligence
- **Tool ID**: `shodan`
- **Category**: NETWORK_INTEL
- **Module**: `osint`
- **Provider Type**: DEEP_ENGINE
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/shodan.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `ip, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `ip, domain, ports, cve`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `120/min`
- **Timeout**: `15.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 256. Substack Newsletter

- **Tool Name**: Substack Newsletter
- **Tool ID**: `osint_substack`
- **Category**: Newsletters
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_substack.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 257. Substack Newsletter Archive

- **Tool Name**: Substack Newsletter Archive
- **Tool ID**: `osint_substack_archive`
- **Category**: Newsletters
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_substack_archive.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 258. Debian Project Contributor

- **Tool Name**: Debian Project Contributor
- **Tool ID**: `osint_debian_contributors`
- **Category**: Open Knowledge
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_debian_contributors.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 259. Fandom (Wikia) Contributor

- **Tool Name**: Fandom (Wikia) Contributor
- **Tool ID**: `osint_fandom_wikia_contributor`
- **Category**: Open Knowledge
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_fandom_wikia_contributor.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 260. OpenStreetMap Mapper

- **Tool Name**: OpenStreetMap Mapper
- **Tool ID**: `osint_openstreetmap_mappers`
- **Category**: Open Knowledge
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_openstreetmap_mappers.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 261. Wikipedia User Page

- **Tool Name**: Wikipedia User Page
- **Tool ID**: `osint_wikipedia_users`
- **Category**: Open Knowledge
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_wikipedia_users.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 262. Ansible Galaxy

- **Tool Name**: Ansible Galaxy
- **Tool ID**: `osint_ansible_galaxy`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_ansible_galaxy.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 263. Arch Linux AUR Maintainer

- **Tool Name**: Arch Linux AUR Maintainer
- **Tool ID**: `osint_arch_aur_users`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_arch_aur_users.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 264. CPAN MetaCPAN

- **Tool Name**: CPAN MetaCPAN
- **Tool ID**: `osint_cpan`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_cpan.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 265. Clojars Clojure

- **Tool Name**: Clojars Clojure
- **Tool ID**: `osint_clojars`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_clojars.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 266. CocoaPods Apple

- **Tool Name**: CocoaPods Apple
- **Tool ID**: `osint_cocoapods`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_cocoapods.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 267. Crates.io Rust Packages

- **Tool Name**: Crates.io Rust Packages
- **Tool ID**: `osint_crates_io`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_crates_io.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 268. Fedora Linux Packager

- **Tool Name**: Fedora Linux Packager
- **Tool ID**: `osint_fedora_packagers`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_fedora_packagers.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 269. Hex.pm Erlang & Elixir

- **Tool Name**: Hex.pm Erlang & Elixir
- **Tool ID**: `osint_hex_pm`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hex_pm.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 270. Libraries.io Package Monitor

- **Tool Name**: Libraries.io Package Monitor
- **Tool ID**: `osint_libraries_io`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_libraries_io.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 271. NuGet .NET Packages

- **Tool Name**: NuGet .NET Packages
- **Tool ID**: `osint_nuget`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_nuget.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 272. Packagist Composer

- **Tool Name**: Packagist Composer
- **Tool ID**: `osint_packagist`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_packagist.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 273. Pub.dev Dart & Flutter

- **Tool Name**: Pub.dev Dart & Flutter
- **Tool ID**: `osint_pub_dev`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_pub_dev.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 274. PyPI Python Packages

- **Tool Name**: PyPI Python Packages
- **Tool ID**: `osint_pypi`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_pypi.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 275. RubyGems

- **Tool Name**: RubyGems
- **Tool ID**: `osint_rubygems`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_rubygems.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 276. npm Packages

- **Tool Name**: npm Packages
- **Tool ID**: `osint_npm`
- **Category**: Package Registries
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_npm.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 277. 500px Photography

- **Tool Name**: 500px Photography
- **Tool ID**: `osint_500px`
- **Category**: Photography
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_500px.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 278. Flickr Photography

- **Tool Name**: Flickr Photography
- **Tool ID**: `osint_flickr`
- **Category**: Photography
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_flickr.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 279. Pixelfed Art Showcase

- **Tool Name**: Pixelfed Art Showcase
- **Tool ID**: `osint_pixelfed_art_showcase`
- **Category**: Photography
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_pixelfed_art_showcase.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 280. Pixelfed Decentralized Photos

- **Tool Name**: Pixelfed Decentralized Photos
- **Tool ID**: `osint_pixelfed_social`
- **Category**: Photography
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_pixelfed_social.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 281. Unsplash High-Res Photos

- **Tool Name**: Unsplash High-Res Photos
- **Tool ID**: `osint_unsplash`
- **Category**: Photography
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_unsplash.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 282. VSCO Creative Journal

- **Tool Name**: VSCO Creative Journal
- **Tool ID**: `osint_vsco`
- **Category**: Photography
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_vsco.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 283. Buzzsprout Podcasts

- **Tool Name**: Buzzsprout Podcasts
- **Tool ID**: `osint_buzzsprout`
- **Category**: Podcasting
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_buzzsprout.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 284. Castbox Podcasts

- **Tool Name**: Castbox Podcasts
- **Tool ID**: `osint_castbox_fm`
- **Category**: Podcasting
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_castbox_fm.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 285. Podbean Podcasts

- **Tool Name**: Podbean Podcasts
- **Tool ID**: `osint_podbean`
- **Category**: Podcasting
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_podbean.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 286. Spreaker Radio

- **Tool Name**: Spreaker Radio
- **Tool ID**: `osint_spreaker`
- **Category**: Podcasting
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_spreaker.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 287. About.me Personal Splash

- **Tool Name**: About.me Personal Splash
- **Tool ID**: `osint_about_me`
- **Category**: Portfolios
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_about_me.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 288. Carrd Interactive Showcase

- **Tool Name**: Carrd Interactive Showcase
- **Tool ID**: `osint_carrd_portfolio`
- **Category**: Portfolios
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_carrd_portfolio.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 289. Carrd Responsive Sites

- **Tool Name**: Carrd Responsive Sites
- **Tool ID**: `osint_carrd_co`
- **Category**: Portfolios
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_carrd_co.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 290. ReadCV Minimalist Resume

- **Tool Name**: ReadCV Minimalist Resume
- **Tool ID**: `osint_readcv`
- **Category**: Portfolios
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_readcv.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 291. Contra Freelance Network

- **Tool Name**: Contra Freelance Network
- **Tool ID**: `osint_contra_independent`
- **Category**: Professional & Career
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_contra_independent.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 292. Peerlist Professional Network

- **Tool Name**: Peerlist Professional Network
- **Tool ID**: `osint_peerlist`
- **Category**: Professional & Career
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_peerlist.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 293. Polywork Multidisciplinary Profile

- **Tool Name**: Polywork Multidisciplinary Profile
- **Tool ID**: `osint_polywork`
- **Category**: Professional & Career
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_polywork.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 294. Showwcase Developer Community

- **Tool Name**: Showwcase Developer Community
- **Tool ID**: `osint_showwcase_developer`
- **Category**: Professional & Career
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_showwcase_developer.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 295. Wellfound (AngelList)

- **Tool Name**: Wellfound (AngelList)
- **Tool ID**: `osint_wellfound`
- **Category**: Professional & Career
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_wellfound.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 296. Gravatar Globally Recognized Avatar

- **Tool Name**: Gravatar Globally Recognized Avatar
- **Tool ID**: `osint_gravatar`
- **Category**: Public Directories
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_gravatar.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 297. Medium Author Articles

- **Tool Name**: Medium Author Articles
- **Tool ID**: `osint_medium_stories`
- **Category**: Publishing
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_medium_stories.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 298. Medium Publication

- **Tool Name**: Medium Publication
- **Tool ID**: `osint_medium`
- **Category**: Publishing
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_medium.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 299. Vocal Media Storytellers

- **Tool Name**: Vocal Media Storytellers
- **Tool ID**: `osint_vocal_media`
- **Category**: Publishing
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_vocal_media.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 300. Write.as Thoughtful Writing

- **Tool Name**: Write.as Thoughtful Writing
- **Tool ID**: `osint_writeas_blog`
- **Category**: Publishing
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_writeas_blog.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle, domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 301. Bilibili Video & Creator

- **Tool Name**: Bilibili Video & Creator
- **Tool ID**: `osint_bilibili_tv`
- **Category**: Regional & Niche
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bilibili_tv.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 302. Douban Film & Books

- **Tool Name**: Douban Film & Books
- **Tool ID**: `osint_douban_movie`
- **Category**: Regional & Niche
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_douban_movie.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 303. Hatena Bookmark & Blog

- **Tool Name**: Hatena Bookmark & Blog
- **Tool ID**: `osint_hatena_id`
- **Category**: Regional & Niche
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_hatena_id.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 304. Qiita Japanese Tech Hub

- **Tool Name**: Qiita Japanese Tech Hub
- **Tool ID**: `osint_qiita_tech`
- **Category**: Regional & Niche
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_qiita_tech.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 305. Sina Weibo

- **Tool Name**: Sina Weibo
- **Tool ID**: `osint_weibo`
- **Category**: Regional & Niche
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_weibo.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 306. Taringa Latin America

- **Tool Name**: Taringa Latin America
- **Tool ID**: `osint_taringa`
- **Category**: Regional & Niche
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_taringa.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 307. Zenn.dev Japanese Devs

- **Tool Name**: Zenn.dev Japanese Devs
- **Tool ID**: `osint_zenn_dev_tech`
- **Category**: Regional & Niche
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_zenn_dev_tech.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 308. Zhihu Knowledge Column

- **Tool Name**: Zhihu Knowledge Column
- **Tool ID**: `osint_zhihu_column`
- **Category**: Regional & Niche
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_zhihu_column.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 309. Google Dork Recon Engine

- **Tool Name**: Google Dork Recon Engine
- **Tool ID**: `google_dork`
- **Category**: SEARCH_OPERATORS
- **Module**: `osint`
- **Provider Type**: DEEP_ENGINE
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/google_dork.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `domain`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `domain, dorks, files`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `120/min`
- **Timeout**: `15.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 310. Bluesky Directory Search

- **Tool Name**: Bluesky Directory Search
- **Tool ID**: `osint_bluesky_directory_actor`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bluesky_directory_actor.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 311. Bluesky Social

- **Tool Name**: Bluesky Social
- **Tool ID**: `osint_bluesky`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_bluesky.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 312. Cohost Social

- **Tool Name**: Cohost Social
- **Tool ID**: `osint_cohost`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_cohost.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 313. Disqus Comment Network

- **Tool Name**: Disqus Comment Network
- **Tool ID**: `osint_disqus`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_disqus.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 314. Gab Social

- **Tool Name**: Gab Social
- **Tool ID**: `osint_gab_ai`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_gab_ai.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 315. Keybase Cryptographic Identity

- **Tool Name**: Keybase Cryptographic Identity
- **Tool ID**: `osint_keybase`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_keybase.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 316. Mastodon (mastodon.social)

- **Tool Name**: Mastodon (mastodon.social)
- **Tool ID**: `osint_mastodon_social`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_mastodon_social.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 317. MeWe Social

- **Tool Name**: MeWe Social
- **Tool ID**: `osint_mewe`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_mewe.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 318. Meta Threads

- **Tool Name**: Meta Threads
- **Tool ID**: `osint_threads`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_threads.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 319. Mix Content Curation

- **Tool Name**: Mix Content Curation
- **Tool ID**: `osint_mix_com`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_mix_com.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 320. Pinterest Visual Discovery

- **Tool Name**: Pinterest Visual Discovery
- **Tool ID**: `osint_pinterest`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_pinterest.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 321. Plurk Microblogging

- **Tool Name**: Plurk Microblogging
- **Tool ID**: `osint_plurk`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_plurk.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 322. Reddit Community

- **Tool Name**: Reddit Community
- **Tool ID**: `osint_reddit`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_reddit.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 323. Snapchat Public Profile

- **Tool Name**: Snapchat Public Profile
- **Tool ID**: `osint_snapchat`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_snapchat.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 324. Tumblr Microblogging

- **Tool Name**: Tumblr Microblogging
- **Tool ID**: `osint_tumblr`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_tumblr.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 325. VKontakte (VK)

- **Tool Name**: VKontakte (VK)
- **Tool ID**: `osint_vkontakte`
- **Category**: Social Networks
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_vkontakte.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 326. AllTrails Outdoor Maps

- **Tool Name**: AllTrails Outdoor Maps
- **Tool ID**: `osint_alltrails`
- **Category**: Sports & Fitness
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_alltrails.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 327. Intervals.icu Endurance Analytics

- **Tool Name**: Intervals.icu Endurance Analytics
- **Tool ID**: `osint_intervals_icu`
- **Category**: Sports & Fitness
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_intervals_icu.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 328. Komoot Cycling & Hiking Route

- **Tool Name**: Komoot Cycling & Hiking Route
- **Tool ID**: `osint_komoot`
- **Category**: Sports & Fitness
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_komoot.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 329. Parkrun Athlete

- **Tool Name**: Parkrun Athlete
- **Tool ID**: `osint_parkrun_results`
- **Category**: Sports & Fitness
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_parkrun_results.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 330. Ride with GPS Cycling

- **Tool Name**: Ride with GPS Cycling
- **Tool ID**: `osint_ridewithgps`
- **Category**: Sports & Fitness
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_ridewithgps.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 331. Strava Athletics

- **Tool Name**: Strava Athletics
- **Tool ID**: `osint_strava`
- **Category**: Sports & Fitness
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_strava.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 332. Trailforks Mountain Biking

- **Tool Name**: Trailforks Mountain Biking
- **Tool ID**: `osint_trailforks_bike`
- **Category**: Sports & Fitness
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_trailforks_bike.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 333. Wikiloc GPS Outdoor Trails

- **Tool Name**: Wikiloc GPS Outdoor Trails
- **Tool ID**: `osint_wikiloc_gps`
- **Category**: Sports & Fitness
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_wikiloc_gps.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 334. Maltego Entity Transforms

- **Tool Name**: Maltego Entity Transforms
- **Tool ID**: `maltego`
- **Category**: TRANSFORMS
- **Module**: `osint`
- **Provider Type**: DEEP_ENGINE
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/maltego.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `domain, ip`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `domain, ip, dns, whois`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `120/min`
- **Timeout**: `15.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

### 335. PeerTube Federated Video

- **Tool Name**: PeerTube Federated Video
- **Tool ID**: `osint_peertube_tv`
- **Category**: Video
- **Module**: `osint`
- **Provider Type**: PLATFORM_PROBER
- **Implementation Location**: `backend/app/modules/osint/catalog_adapter.py` / `providers/osint_peertube_tv.py`
- **Backend Service**: `OsintModule` -> `OSINTPlatformAdapter`
- **Frontend Component**: Registered via Provider Registry API
- **API / CLI**: HTTP REST / Asynchronous HTTPX prober
- **Authentication Required**: `False` (Public read-only profiles)
- **Environment Variables**: `SHODAN_API_KEY`, `SPIDERFOOT_URL` (for primary engines only)
- **Input Types**: `username, person, identity, handle`
- **Output Types**: `Entity (Username/Person/Domain)`, `Evidence (Cryptographic SHA-256)`
- **Capabilities**: `profile_lookup, handle_detection, social_graph, account_enumeration`
- **Health Check**: Active endpoint status prober
- **Rate Limits**: `30/min`
- **Timeout**: `4.0s`
- **Retry**: `Standard HTTP retry on 503`
- **Current Status**: `HEALTHY`
- **Migration Status**: `FULLY_MIGRATED`

