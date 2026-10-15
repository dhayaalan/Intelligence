import os
import re
import time
import httpx
import logging
from typing import Any, Dict, List, Optional
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus, EntityPayload, EntityType
from app.module_sdk.sdk import ModuleSDK

logger = logging.getLogger("sential.threat_intel.nvd")

CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)


class NVDVulnerabilityProvider(ProviderAdapter):
    """
    NIST National Vulnerability Database (NVD) CVE API 2.0 Provider.
    Queries official NIST API for authoritative CVSS v3.1/v2 metrics, CWE classifications,
    vulnerability descriptions, and official vendor advisories.
    Works keylessly (rate-limited by IP) or with NVD_API_KEY.
    """

    @property
    def provider_id(self) -> str:
        return "nvd_cve"

    @property
    def name(self) -> str:
        return "NIST National Vulnerability Database (NVD) CVE API 2.0"

    @property
    def version(self) -> str:
        return "2.1.0"

    @property
    def timeout_seconds(self) -> float:
        return 10.0

    async def health_check(self) -> HealthCheckResult:
        try:
            api_key = os.getenv("NVD_API_KEY")
            headers = {"User-Agent": "SentialIntelligence/1.0"}
            if api_key:
                headers["apiKey"] = api_key

            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    "https://services.nvd.nist.gov/rest/json/cves/2.0",
                    params={"cveId": "CVE-2021-44228"},
                    headers=headers
                )
                if res.status_code == 200:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.HEALTHY,
                        message="NIST NVD CVE API 2.0 is operational",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                elif res.status_code == 429:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.DEGRADED,
                        message="NVD API rate limit encountered",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                return HealthCheckResult(
                    status=ModuleHealthStatus.DEGRADED,
                    message=f"NVD API returned HTTP {res.status_code}",
                    latency_ms=100.0
                )
        except Exception as e:
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                message=f"NVD API health notice: {str(e)}",
                latency_ms=0.0
            )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        query = request.query.strip()
        if not query:
            return ProviderResponse(
                provider_id=self.provider_id,
                status="skipped",
                duration_ms=0.0,
                error="Empty vulnerability query."
            )

        api_key = os.getenv("NVD_API_KEY") or request.config.get("api_key")
        headers = {"User-Agent": "SentialIntelligence/1.0"}
        if api_key:
            headers["apiKey"] = api_key

        match = CVE_PATTERN.search(query)
        if match:
            cve_id = match.group(0).upper()
            params = {"cveId": cve_id}
        else:
            params = {"keywordSearch": query, "resultsPerPage": 10}

        cves_found: List[Dict[str, Any]] = []
        entities: List[Dict[str, Any]] = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
                resp = await client.get(
                    "https://services.nvd.nist.gov/rest/json/cves/2.0",
                    params=params,
                    headers=headers
                )
                duration = round((time.time() - start_time) * 1000, 2)

                if resp.status_code == 429:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error="NIST NVD rate limit exceeded (HTTP 429). Please retry or provide NVD_API_KEY."
                    )
                elif resp.status_code in (401, 403):
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error=f"NIST NVD access restricted or invalid API key (HTTP {resp.status_code})."
                    )
                elif resp.status_code >= 400:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error=f"NIST NVD returned HTTP {resp.status_code}."
                    )

                data = resp.json()
                vulnerabilities = data.get("vulnerabilities", [])
                for entry in vulnerabilities:
                    cve = entry.get("cve", {})
                    cid = cve.get("id")
                    if not cid:
                        continue

                    # Extract English description
                    descriptions = cve.get("descriptions", [])
                    desc_text = ""
                    for d in descriptions:
                        if d.get("lang") == "en":
                            desc_text = d.get("value", "")
                            break
                    if not desc_text and descriptions:
                        desc_text = descriptions[0].get("value", "")

                    # Extract CVSS Metrics without inventing severity
                    metrics = cve.get("metrics", {})
                    score = None
                    severity = None
                    vector = None

                    if "cvssMetricV31" in metrics and metrics["cvssMetricV31"]:
                        metric_item = metrics["cvssMetricV31"][0].get("cvssData", {})
                        score = metric_item.get("baseScore")
                        severity = metric_item.get("baseSeverity")
                        vector = metric_item.get("vectorString")
                    elif "cvssMetricV30" in metrics and metrics["cvssMetricV30"]:
                        metric_item = metrics["cvssMetricV30"][0].get("cvssData", {})
                        score = metric_item.get("baseScore")
                        severity = metric_item.get("baseSeverity")
                        vector = metric_item.get("vectorString")
                    elif "cvssMetricV2" in metrics and metrics["cvssMetricV2"]:
                        metric_item = metrics["cvssMetricV2"][0].get("cvssData", {})
                        score = metric_item.get("baseScore")
                        severity = metrics["cvssMetricV2"][0].get("baseSeverity")
                        vector = metric_item.get("vectorString")

                    # Extract CWEs
                    cwes = []
                    for weakness in cve.get("weaknesses", []):
                        for wd in weakness.get("description", []):
                            val = wd.get("value")
                            if val and val != "NVD-CWE-noinfo" and val not in cwes:
                                cwes.append(val)

                    # Extract References
                    refs = [r.get("url") for r in cve.get("references", []) if r.get("url")][:5]

                    rec = {
                        "cve_id": cid,
                        "published": cve.get("published"),
                        "last_modified": cve.get("lastModified"),
                        "description": desc_text,
                        "cvss_score": score,
                        "severity": severity,
                        "cvss_vector": vector,
                        "cwes": cwes,
                        "references": refs,
                        "source": "NIST NVD"
                    }
                    cves_found.append(rec)

                    # Entity display label
                    sev_label = severity if severity else "UNSPECIFIED"
                    score_label = f"CVSS {score}" if score is not None else "Score: N/A"

                    entities.append(EntityPayload(
                        type=EntityType.VULNERABILITY,
                        value=f"{cid} - {sev_label} ({score_label})",
                        confidence=0.98,
                        sources=[self.provider_id],
                        metadata={
                            "cve_id": cid,
                            "cvss_score": score,
                            "severity": severity,
                            "cvss_vector": vector,
                            "cwes": cwes,
                            "description": desc_text[:300] if desc_text else "",
                            "source": "NIST National Vulnerability Database",
                            "references": refs,
                            "is_verified_cve": True
                        }
                    ).dict())

        except httpx.TimeoutException:
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error="NIST NVD API request timed out."
            )
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"NIST NVD query failed for '{query}': {e}")
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error=f"NVD query error: {str(e)}"
            )

        duration = round((time.time() - start_time) * 1000, 2)
        ev = ModuleSDK.create_evidence(
            source="NIST National Vulnerability Database (NVD)",
            provider=self.provider_id,
            module="threat_intelligence",
            raw_data={
                "query": query,
                "cves_count": len(cves_found),
                "cves": cves_found[:5]
            },
            reference=f"Target: {query} (NIST NVD API 2.0)"
        )

        return ProviderResponse(
            provider_id=self.provider_id,
            status="success",
            duration_ms=duration,
            raw_data={
                "query": query,
                "cves": cves_found,
                "vulnerabilities": cves_found,
                "count": len(cves_found),
                "entities": entities,
                "evidence": [ev.dict() if hasattr(ev, "dict") else ev]
            }
        )
