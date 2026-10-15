import os
import time
import httpx
import logging
from typing import Any, Dict, List, Optional
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus, EntityPayload, EntityType
from app.module_sdk.sdk import ModuleSDK

logger = logging.getLogger("sential.osint.opensanctions")


class OpenSanctionsProvider(ProviderAdapter):
    """
    OpenSanctions International Sanctions, PEP, and Watchlists Provider.
    Queries the OpenSanctions API to screen persons, companies, and vessels against
    consolidated global sanction regimes (OFAC, EU, UN, UK), political exposure registers,
    and criminal watchlists.
    """

    @property
    def provider_id(self) -> str:
        return "opensanctions"

    @property
    def name(self) -> str:
        return "OpenSanctions Global Watchlists & PEP Screening"

    @property
    def version(self) -> str:
        return "1.1.0"

    @property
    def timeout_seconds(self) -> float:
        return 8.0

    async def health_check(self) -> HealthCheckResult:
        try:
            headers = {"User-Agent": "SentialIntelligence/1.0"}
            api_key = os.getenv("OPENSANCTIONS_API_KEY")
            if api_key:
                headers["Authorization"] = f"ApiKey {api_key}"

            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(
                    "https://api.opensanctions.org/search/default",
                    params={"q": "Putin", "limit": 1},
                    headers=headers
                )
                if res.status_code == 200:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.HEALTHY,
                        message="OpenSanctions API is online and responsive",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                elif res.status_code == 429:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.DEGRADED,
                        message="OpenSanctions rate limit encountered",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                return HealthCheckResult(
                    status=ModuleHealthStatus.DEGRADED,
                    message=f"OpenSanctions returned HTTP {res.status_code}",
                    latency_ms=100.0
                )
        except Exception as e:
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                message=f"OpenSanctions health notice: {str(e)}",
                latency_ms=0.0
            )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        query = request.query.strip()
        if not query or len(query) < 2:
            return ProviderResponse(
                provider_id=self.provider_id,
                status="skipped",
                duration_ms=0.0,
                error="Query too short for sanctions screening (minimum 2 characters required)."
            )

        headers = {"User-Agent": "SentialIntelligence/1.0"}
        api_key = os.getenv("OPENSANCTIONS_API_KEY") or request.config.get("api_key")
        if api_key:
            headers["Authorization"] = f"ApiKey {api_key}"

        records: List[Dict[str, Any]] = []
        entities: List[Dict[str, Any]] = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
                resp = await client.get(
                    "https://api.opensanctions.org/search/default",
                    params={"q": query, "limit": 10},
                    headers=headers
                )
                duration = round((time.time() - start_time) * 1000, 2)

                if resp.status_code == 429:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error="OpenSanctions rate limit exceeded (HTTP 429). Please retry or provide OPENSANCTIONS_API_KEY."
                    )
                elif resp.status_code in (401, 403):
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error=f"OpenSanctions authentication required or key invalid (HTTP {resp.status_code})."
                    )
                elif resp.status_code >= 400:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error=f"OpenSanctions returned HTTP {resp.status_code}."
                    )

                data = resp.json()
                results = data.get("results", [])
                for item in results:
                    caption = item.get("caption") or query
                    schema = item.get("schema", "LegalEntity")
                    datasets = item.get("datasets", [])
                    properties = item.get("properties", {})
                    topics = properties.get("topics", [])
                    countries = properties.get("country", []) or properties.get("jurisdiction", [])
                    raw_score = item.get("score")  # Do NOT assign arbitrary 0.85!

                    # Map schema to proper EntityType
                    schema_lower = schema.lower()
                    if schema_lower in ("person", "individual"):
                        ent_type = EntityType.PERSON
                    elif schema_lower in ("cryptoaddress", "cryptowallet"):
                        ent_type = EntityType.CRYPTO_ADDRESS
                    elif schema_lower in ("organization", "company", "legalentity", "bank"):
                        ent_type = EntityType.ORGANIZATION
                    else:
                        ent_type = EntityType.ORGANIZATION

                    is_sanctioned = any(t in ("sanction", "debarment") for t in topics)
                    is_pep = any("pep" in str(t).lower() for t in topics)

                    record = {
                        "id": item.get("id"),
                        "caption": caption,
                        "schema": schema,
                        "datasets": datasets,
                        "topics": topics,
                        "countries": countries,
                        "score": raw_score,
                        "first_seen": item.get("first_seen"),
                        "last_seen": item.get("last_seen"),
                        "sanctioned": is_sanctioned,
                        "is_pep": is_pep
                    }
                    records.append(record)

                    # Compute confidence honestly from actual provider score
                    if raw_score is not None:
                        try:
                            conf = min(0.98, max(0.20, float(raw_score)))
                        except (ValueError, TypeError):
                            conf = 0.70
                    else:
                        conf = 0.70  # Qualitative unranked score

                    entities.append(EntityPayload(
                        type=ent_type,
                        value=caption,
                        confidence=conf,
                        sources=[self.provider_id],
                        metadata={
                            "record_id": item.get("id"),
                            "schema": schema,
                            "datasets": datasets,
                            "topics": topics,
                            "countries": countries,
                            "similarity_score": raw_score,
                            "is_sanctioned": is_sanctioned,
                            "is_pep": is_pep,
                            "source": "OpenSanctions",
                            "requires_analyst_review": conf < 0.90
                        }
                    ).dict())

        except httpx.TimeoutException:
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error="OpenSanctions API request timed out."
            )
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"OpenSanctions search failed for '{query}': {e}")
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error=f"OpenSanctions query error: {str(e)}"
            )

        duration = round((time.time() - start_time) * 1000, 2)
        ev = ModuleSDK.create_evidence(
            source="OpenSanctions Watchlist & Sanctions Screener",
            provider=self.provider_id,
            module="osint",
            raw_data={
                "query": query,
                "matches_count": len(records),
                "top_matches": records[:5]
            },
            reference=f"Target: {query} (OpenSanctions API)"
        )

        return ProviderResponse(
            provider_id=self.provider_id,
            status="success",
            duration_ms=duration,
            raw_data={
                "query": query,
                "matches": records,
                "records": records,
                "count": len(records),
                "entities": entities,
                "evidence": [ev.dict() if hasattr(ev, "dict") else ev]
            }
        )
