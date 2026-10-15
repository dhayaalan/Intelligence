import re
import time
import httpx
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus
from app.modules.osint.models import ExtractionStatus

logger = logging.getLogger("sential.osint.financial")

# Strict privacy boundary guard patterns: forbid personal banking records, credentials, OTPs, PINs, card numbers
PRIVATE_FINANCIAL_PATTERNS = [
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),                     # Credit / Debit card numbers (13-19 digits)
    re.compile(r"\b(?:cvv|cvc|pin|otp|password|passwd)\b", re.I), # Security credentials
    re.compile(r"\b(?:personal\s+balance|account\s+balance|bank\s+login|internet\s+banking\s+password)\b", re.I),
    re.compile(r"\b(?:routing\s+number\s+pin|atm\s+pin)\b", re.I),
]


class FinancialIntelProvider(ProviderAdapter):
    """
    Financial-Sector, Banking-Institution, and Corporate OSINT Provider.
    Extracts public disclosures, official Legal Entity Identifiers (GLEIF LEI),
    and public SEC EDGAR filings for banks and corporate entities.
    Strictly enforces a privacy boundary prohibiting any personal financial data extraction.
    """

    @property
    def provider_id(self) -> str:
        return "financial_intel"

    @property
    def name(self) -> str:
        return "Corporate, Banking & Financial OSINT (GLEIF / SEC EDGAR)"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def timeout_seconds(self) -> float:
        return 12.0

    async def health_check(self) -> HealthCheckResult:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(
                    "https://api.gleif.org/api/v1/lei-records?page[size]=1",
                    headers={"User-Agent": "SentialIntelligence/1.0 (investigator@sential.org)"}
                )
                if res.status_code in [200, 301, 302]:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.HEALTHY,
                        message="GLEIF LEI and SEC EDGAR public registries operational",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                return HealthCheckResult(
                    status=ModuleHealthStatus.DEGRADED,
                    message=f"GLEIF returned HTTP {res.status_code}",
                    latency_ms=100.0
                )
        except Exception as e:
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                message=f"Financial registry health check notice: {str(e)}",
                latency_ms=0.0
            )

    def _violates_privacy_boundary(self, query: str) -> Optional[str]:
        """Detect attempts to query private personal financial records or credentials."""
        for pattern in PRIVATE_FINANCIAL_PATTERNS:
            if pattern.search(query):
                return (
                    "Strict Financial Privacy Guardrail: Unauthorized extraction of private personal financial records, "
                    "banking credentials, PINs, OTPs, card numbers, or personal account balances is strictly prohibited "
                    "under institutional OSINT compliance boundaries."
                )
        return None

    async def _query_gleif(self, query: str) -> List[Dict[str, Any]]:
        """Query official Global Legal Entity Identifier Foundation (GLEIF) registry."""
        results = []
        is_lei_code = len(query.strip()) == 20 and query.strip().isalnum()
        url = (
            f"https://api.gleif.org/api/v1/lei-records/{query.strip().upper()}"
            if is_lei_code
            else f"https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]={httpx.URL(query.strip())}&page[size]=3"
        )
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(url, headers={"User-Agent": "SentialIntelligence/1.0 (investigator@sential.org)"})
                if res.status_code == 200:
                    payload = res.json()
                    records = [payload.get("data")] if is_lei_code else payload.get("data", [])
                    for rec in records:
                        if not rec:
                            continue
                        attrs = rec.get("attributes", {})
                        entity = attrs.get("entity", {})
                        reg = attrs.get("registration", {})
                        legal_addr = entity.get("legalAddress", {})
                        hq_addr = entity.get("headquartersAddress", {})

                        results.append({
                            "lei": attrs.get("lei") or rec.get("id"),
                            "legal_name": entity.get("legalName", {}).get("name"),
                            "status": reg.get("status"),
                            "legal_jurisdiction": entity.get("jurisdiction"),
                            "entity_category": entity.get("category"),
                            "legal_form": entity.get("legalForm", {}).get("name"),
                            "registered_address": {
                                "city": legal_addr.get("city"),
                                "country": legal_addr.get("country"),
                                "postal_code": legal_addr.get("postalCode"),
                                "lines": legal_addr.get("addressLines", [])
                            },
                            "headquarters_address": {
                                "city": hq_addr.get("city"),
                                "country": hq_addr.get("country"),
                                "postal_code": hq_addr.get("postalCode")
                            },
                            "registration_authority": entity.get("registrationAuthority", {}).get("registrationAuthorityID"),
                            "managing_lou": reg.get("managingLou"),
                            "next_renewal_date": reg.get("nextRenewalDate"),
                            "source": "GLEIF (Global Legal Entity Identifier Foundation)",
                            "canonical_url": f"https://search.gleif.org/#/record/{attrs.get('lei') or rec.get('id')}"
                        })
        except Exception as e:
            logger.warning(f"GLEIF query notice for {query}: {e}")
        return results

    async def _query_sec_edgar(self, query: str) -> List[Dict[str, Any]]:
        """Query official SEC EDGAR database for public securities filings and company disclosures."""
        filings_data = []
        clean = query.strip()
        # If query is numeric CIK or starts with CIK
        cik = clean.upper().replace("CIK", "").strip() if clean.upper().startswith("CIK") or clean.isdigit() else None
        if cik and len(cik) <= 10:
            padded_cik = cik.zfill(10)
            url = f"https://data.sec.gov/submissions/CIK{padded_cik}.json"
            try:
                headers = {"User-Agent": "SentialIntelligence investigator@sential.org"}
                async with httpx.AsyncClient(timeout=8.0) as client:
                    res = await client.get(url, headers=headers)
                    if res.status_code == 200:
                        sec_json = res.json()
                        recent_filings = sec_json.get("filings", {}).get("recent", {})
                        forms = recent_filings.get("form", [])[:5]
                        filing_dates = recent_filings.get("filingDate", [])[:5]
                        accessions = recent_filings.get("accessionNumber", [])[:5]

                        filings_list = []
                        for f_idx in range(min(5, len(forms))):
                            acc_clean = accessions[f_idx].replace("-", "") if f_idx < len(accessions) else ""
                            filings_list.append({
                                "form": forms[f_idx],
                                "filing_date": filing_dates[f_idx] if f_idx < len(filing_dates) else None,
                                "accession_number": accessions[f_idx] if f_idx < len(accessions) else None,
                                "document_url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_clean}/"
                            })

                        filings_data.append({
                            "cik": padded_cik,
                            "entity_name": sec_json.get("name"),
                            "tickers": sec_json.get("tickers", []),
                            "exchanges": sec_json.get("exchanges", []),
                            "sic": sec_json.get("sic"),
                            "sic_description": sec_json.get("sicDescription"),
                            "state_of_incorporation": sec_json.get("stateOfIncorporation"),
                            "fiscal_year_end": sec_json.get("fiscalYearEnd"),
                            "business_address": sec_json.get("addresses", {}).get("business", {}),
                            "recent_filings": filings_list,
                            "source": "US SEC EDGAR (Electronic Data Gathering, Analysis, and Retrieval)",
                            "canonical_url": f"https://www.sec.gov/edgar/browse/?CIK={padded_cik}"
                        })
            except Exception as e:
                logger.warning(f"SEC EDGAR query notice for {query}: {e}")
        return filings_data

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        query = request.query.strip()
        t_type = request.target_type.lower()
        now = datetime.now(timezone.utc).isoformat()

        # 1. Privacy Boundary Check
        privacy_violation = self._violates_privacy_boundary(query)
        if privacy_violation:
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="rejected",
                raw_data={
                    "error": privacy_violation,
                    "target": query,
                    "extraction_status": ExtractionStatus.ACCESS_RESTRICTED.value,
                    "privacy_violation": True,
                    "fetched_at": now
                },
                duration_ms=duration
            )

        # 2. Public Institutional Intelligence Extraction
        gleif_records = await self._query_gleif(query)
        sec_records = await self._query_sec_edgar(query)

        has_data = bool(gleif_records or sec_records)
        extraction_status = ExtractionStatus.METADATA_EXTRACTED if has_data else ExtractionStatus.NOT_FOUND

        duration = round((time.time() - start_time) * 1000, 2)
        return ProviderResponse(
            provider_id=self.provider_id,
            status="success" if has_data else "not_found",
            raw_data={
                "target": query,
                "target_type": t_type,
                "extraction_status": extraction_status.value,
                "legal_entity_identifiers": gleif_records,
                "sec_corporate_filings": sec_records,
                "privacy_boundary_enforced": True,
                "sources_queried": [
                    "GLEIF Legal Entity Identifier Registry",
                    "US SEC EDGAR Public Filings Database"
                ],
                "fetched_at": now
            },
            duration_ms=duration
        )
