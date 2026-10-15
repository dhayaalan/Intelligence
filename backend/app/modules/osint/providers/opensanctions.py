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
    OpenSanctions International Sanctions, PEP & Watchlist Screening Provider.
    Queries the OpenSanctions global API for entity matching against international sanctions,
    politically exposed persons (PEPs), crime watchlists, and debarment lists.
    Explicitly indicates match confidence and source datasets.
    """

    @property
    def provider_id(self) -> str:
        return "opensanctions"

    @property
    def name(self) -> str:
        return "OpenSanctions Global PEP, Sanctions & Watchlist Screener"

    @property
    def version(self) -> str:
        return "1.0.0"

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
                res = await client.get("https://api.opensanctions.org/search/default?q=Vladimir+Putin&limit=1", headers=headers)
                if res.status_code == 200:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.HEALTHY,
                        message="OpenSanctions API is online and screening database operational",
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
                error="Query too short for sanctions screening."
            )

        headers = {"User-Agent": "SentialIntelligence/1.0"}
        api_key = os.getenv("OPENSANCTIONS_API_KEY") or request.config.get("api_key")
        if api_key:
            headers["Authorization"] = f"ApiKey {api_key}"

        search_url = f"https://api.opensanctions.org/search/default?q={httpx.URL(query)}&limit=10"
        records: List[Dict[str, Any]] = []
        entities: List[Dict[str, Any]] = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
                resp = await client.get(search_url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("results", [])
                    for item in results:
                        caption = item.get("caption") or query
                        schema = item.get("schema", "LegalEntity")
                        datasets = item.get("datasets", [])
                        properties = item.get("properties", {})
                        topics = properties.get("topics", [])
                        countries = properties.get("country", []) or properties.get("jurisdiction", [])
                        score = item.get("score", 0.85)

                        ent_type = EntityType.PERSON if schema.lower() == "person" else EntityType.ORGANIZATION
                        record = {
                            "id": item.get("id"),
                            "caption": caption,
                            "schema": schema,
                            "datasets": datasets,
                            "topics": topics,
                            "countries": countries,
                            "score": score,
                            "first_seen": item.get("first_seen"),
                            "last_seen": item.get("last_seen"),
                            "sanctioned": "sanction" in topics,
                            "is_pep": "role.pep" in topics
                        }
                        records.append(record)

                        entities.append(EntityPayload(
                            type=ent_type,
                            value=caption,
                            confidence=min(0.95, max(0.40, float(score))),
                            sources=[self.provider_id],
                            metadata={
                                "schema": schema,
                                "datasets": datasets,
                                "topics": topics,
                                "countries": countries,
                                "score": score,
                                "sanctioned": record["sanctioned"],
                                "is_pep": record["is_pep"],
                                "source": "OpenSanctions"
                            }
                        ).dict())
        except Exception as e:
            logger.warning(f"OpenSanctions search failed for '{query}': {e}")

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
                "count": len(records),
                "entities": entities,
                "evidence": [ev.dict() if hasattr(ev, "dict") else ev]
            }
        )
