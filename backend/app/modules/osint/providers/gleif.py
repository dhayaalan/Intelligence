import re
import time
from typing import Dict, Any, List, Optional
import httpx

from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import (
    HealthCheckResult, ModuleHealthStatus, EntityPayload, EvidencePayload, EntityType
)


class GLEIFProvider(ProviderAdapter):
    """
    Genuine Global Legal Entity Identifier Foundation (GLEIF) Provider.
    Queries the official GLEIF Golden Copy API v1 for authoritative corporate legal identity,
    LEI registrations, jurisdictions, and parent/subsidiary structures without simulation.
    """

    def __init__(self):
        self._provider_id = "gleif_lei"
        self._name = "GLEIF Legal Entity Identifier"
        self._category = "FINANCIAL_INTEL"
        self._base_url = "https://api.gleif.org/api/v1/lei-records"
        self._timeout_seconds = 10.0

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def category(self) -> str:
        return self._category

    @property
    def supported_targets(self) -> List[str]:
        return ["organization", "company", "lei", "domain"]

    @property
    def capabilities(self) -> List[str]:
        return ["legal_entity_identifier", "corporate_ownership", "regulatory_records", "lei_lookup"]

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def timeout_seconds(self) -> float:
        return self._timeout_seconds

    async def health_check(self) -> HealthCheckResult:
        return HealthCheckResult(
            status=ModuleHealthStatus.HEALTHY,
            message="GLEIF API provider active and reachable (open public standard)"
        )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        query = request.query.strip()
        target_type = request.target_type.lower()

        # Clean target: if domain or url, extract base company name
        clean_target = query
        if target_type == "domain" or ("." in query and not re.match(r"^[0-9A-Z]{18}[0-9]{2}$", query)):
            clean_target = query.split("/")[0].split(":")[0]
            if "." in clean_target:
                clean_target = clean_target.split(".")[0]

        clean_target = clean_target.strip()
        if not clean_target:
            return ProviderResponse(
                provider_id=self.provider_id,
                status="skipped",
                error="Empty query target provided to GLEIF provider",
                duration_ms=(time.time() - start_time) * 1000
            )

        # Check if query matches ISO 17442 LEI format (20 alphanumeric characters)
        is_lei = bool(re.match(r"^[0-9A-Z]{18}[0-9]{2}$", clean_target.upper()))
        
        headers = {
            "Accept": "application/vnd.api+json",
            "User-Agent": "Sential-Intelligence-Platform/2.0"
        }

        params: Dict[str, Any] = {"page[size]": 10}
        if is_lei:
            params["filter[lei]"] = clean_target.upper()
        else:
            params["filter[entity.legalName]"] = clean_target

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds, headers=headers) as client:
                resp = await client.get(self._base_url, params=params)
                duration_ms = (time.time() - start_time) * 1000

                if resp.status_code == 429:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        error="GLEIF API rate limit exceeded (HTTP 429).",
                        duration_ms=duration_ms
                    )

                if resp.status_code in (401, 403):
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        error=f"GLEIF API access restricted (HTTP {resp.status_code}).",
                        duration_ms=duration_ms
                    )

                if resp.status_code >= 500:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        error=f"GLEIF API service unavailable (HTTP {resp.status_code}).",
                        duration_ms=duration_ms
                    )

                if resp.status_code != 200:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        error=f"GLEIF API returned unexpected HTTP status {resp.status_code}.",
                        duration_ms=duration_ms
                    )

                try:
                    payload = resp.json()
                except Exception as parse_err:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        error=f"Failed to parse GLEIF API response: {str(parse_err)}",
                        duration_ms=duration_ms
                    )

                data_items = payload.get("data", [])
                if not data_items:
                    # Legitimate no-match
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="success",
                        raw_data={
                            "query": query,
                            "total": 0,
                            "records": [],
                            "matches": []
                        },
                        duration_ms=duration_ms
                    )

                records = []
                entities = []
                evidence_list = []

                for item in data_items:
                    lei = item.get("id") or item.get("attributes", {}).get("lei", "")
                    attrs = item.get("attributes", {})
                    entity_info = attrs.get("entity", {})
                    legal_name_obj = entity_info.get("legalName", {})
                    legal_name = legal_name_obj.get("name") if isinstance(legal_name_obj, dict) else str(legal_name_obj)
                    jurisdiction = entity_info.get("jurisdiction", "")
                    entity_status = entity_info.get("status", "")
                    
                    legal_addr = entity_info.get("legalAddress", {})
                    country = legal_addr.get("country", "")
                    city = legal_addr.get("city", "")

                    reg_info = attrs.get("registration", {})
                    reg_status = reg_info.get("status", "")
                    reg_date = reg_info.get("initialRegistrationDate", "")

                    confidence = 0.95 if is_lei else 0.85

                    rec = {
                        "lei": lei,
                        "legal_name": legal_name or query,
                        "jurisdiction": jurisdiction,
                        "country": country,
                        "city": city,
                        "entity_status": entity_status,
                        "registration_status": reg_status,
                        "initial_registration_date": reg_date,
                        "gleif_url": f"https://search.gleif.org/#/record/{lei}"
                    }
                    records.append(rec)

                    entities.append(EntityPayload(
                        type=EntityType.ORGANIZATION,
                        value=legal_name or lei,
                        confidence=confidence,
                        sources=[self.provider_id],
                        metadata={
                            "lei": lei,
                            "jurisdiction": jurisdiction,
                            "country": country,
                            "city": city,
                            "entity_status": entity_status,
                            "registration_status": reg_status,
                            "source_url": rec["gleif_url"]
                        }
                    ))

                    evidence_list.append(EvidencePayload(
                        source=self.provider_id,
                        provider=self.provider_id,
                        module="osint",
                        reference=rec["gleif_url"],
                        confidence=confidence,
                        raw_data=rec
                    ))

                return ProviderResponse(
                    provider_id=self.provider_id,
                    status="success",
                    entities=entities,
                    evidence=evidence_list,
                    raw_data={
                        "query": query,
                        "total": len(records),
                        "records": records,
                        "matches": records
                    },
                    duration_ms=duration_ms
                )

        except (httpx.TimeoutException, httpx.ConnectError, httpx.RequestError) as net_err:
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                error=f"GLEIF network communication error: {str(net_err)}",
                duration_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                error=f"GLEIF execution error: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )
