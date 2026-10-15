import os
import re
import time
import httpx
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus, EntityPayload, EntityType
from app.module_sdk.sdk import ModuleSDK

logger = logging.getLogger("sential.osint.sec_edgar")

# In-memory cache for SEC company tickers to avoid repeated downloads
_SEC_TICKERS_CACHE: Dict[str, Dict[str, Any]] = {}
_SEC_TICKERS_LAST_FETCH = 0.0
SEC_USER_AGENT = "SentialIntelligencePlatform/2.0 (investigations@sential.org)"


async def get_sec_tickers_map() -> Dict[str, Dict[str, Any]]:
    """Fetches and caches SEC company tickers and CIK mappings."""
    global _SEC_TICKERS_CACHE, _SEC_TICKERS_LAST_FETCH
    now = time.time()
    if _SEC_TICKERS_CACHE and (now - _SEC_TICKERS_LAST_FETCH) < 86400:
        return _SEC_TICKERS_CACHE

    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": SEC_USER_AGENT}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                tickers_map: Dict[str, Dict[str, Any]] = {}
                for item in data.values():
                    cik_str = str(item.get("cik_str", "")).zfill(10)
                    ticker = str(item.get("ticker", "")).upper().strip()
                    title = str(item.get("title", "")).strip()
                    entry = {"cik": cik_str, "ticker": ticker, "title": title}
                    if ticker:
                        tickers_map[ticker] = entry
                    if title:
                        tickers_map[title.lower()] = entry
                _SEC_TICKERS_CACHE = tickers_map
                _SEC_TICKERS_LAST_FETCH = now
                logger.info(f"Loaded {len(_SEC_TICKERS_CACHE)} SEC company ticker entries into memory.")
    except Exception as e:
        logger.warning(f"Could not fetch SEC tickers mapping: {e}")
    return _SEC_TICKERS_CACHE


class SECEDGARProvider(ProviderAdapter):
    """
    Official US Securities and Exchange Commission (SEC) EDGAR Provider.
    Queries authoritative SEC company submissions, CIK corporate directories,
    former legal names, SIC industry classifications, and recent public filings (10-K, 10-Q, 8-K).
    Adheres strictly to SEC Fair Access guidelines with compliant User-Agent headers.
    """

    @property
    def provider_id(self) -> str:
        return "sec_edgar"

    @property
    def name(self) -> str:
        return "US SEC EDGAR Official Corporate Filings & CIK API"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def category(self) -> str:
        return "FINANCIAL_INTEL"

    @property
    def supported_targets(self) -> List[str]:
        return ["organization", "domain", "general"]

    @property
    def timeout_seconds(self) -> float:
        return 10.0

    async def health_check(self) -> HealthCheckResult:
        try:
            headers = {"User-Agent": SEC_USER_AGENT}
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    "https://data.sec.gov/submissions/CIK0000320193.json",
                    headers=headers
                )
                if res.status_code == 200:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.HEALTHY,
                        message="US SEC EDGAR API operational and compliant",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                elif res.status_code == 429:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.DEGRADED,
                        message="SEC EDGAR rate limit encountered (HTTP 429)",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                return HealthCheckResult(
                    status=ModuleHealthStatus.DEGRADED,
                    message=f"SEC EDGAR returned HTTP {res.status_code}",
                    latency_ms=100.0
                )
        except Exception as e:
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                message=f"SEC EDGAR health check notice: {str(e)}",
                latency_ms=0.0
            )

    async def _resolve_cik(self, query: str) -> Optional[str]:
        clean = query.strip()
        # Direct CIK number
        if clean.isdigit():
            return clean.zfill(10)
        if clean.upper().startswith("CIK") and clean[3:].strip().isdigit():
            return clean[3:].strip().zfill(10)

        # Lookup in tickers map
        tickers_map = await get_sec_tickers_map()
        query_upper = clean.upper()
        if query_upper in tickers_map:
            return tickers_map[query_upper]["cik"]

        query_lower = clean.lower()
        if query_lower in tickers_map:
            return tickers_map[query_lower]["cik"]

        # Partial substring matching in title
        for key, val in tickers_map.items():
            if len(clean) >= 3 and (clean.lower() in key or key in clean.lower()):
                return val["cik"]

        return None

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        query = request.query.strip()
        if not query:
            return ProviderResponse(
                provider_id=self.provider_id,
                status="skipped",
                duration_ms=0.0,
                error="Empty corporate search target."
            )

        cik = await self._resolve_cik(query)
        if not cik:
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="not_found",
                duration_ms=duration,
                raw_data={
                    "target": query,
                    "count": 0,
                    "records": [],
                    "message": f"No SEC EDGAR CIK mapping discovered for target '{query}'."
                }
            )

        padded_cik = cik.zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{padded_cik}.json"
        headers = {"User-Agent": SEC_USER_AGENT}

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
                res = await client.get(url, headers=headers)
                duration = round((time.time() - start_time) * 1000, 2)

                if res.status_code == 429:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error="SEC EDGAR rate limit exceeded (HTTP 429). Maximum 10 req/sec enforced."
                    )
                elif res.status_code == 404:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="not_found",
                        duration_ms=duration,
                        raw_data={
                            "target": query,
                            "cik": padded_cik,
                            "count": 0,
                            "records": [],
                            "message": f"CIK {padded_cik} not found in SEC EDGAR submission records."
                        }
                    )
                elif res.status_code >= 400:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error=f"SEC EDGAR returned HTTP {res.status_code}."
                    )

                sec_json = res.json()
                legal_name = sec_json.get("name", query)
                sic = sec_json.get("sic")
                sic_desc = sec_json.get("sicDescription")
                tickers = sec_json.get("tickers", [])
                exchanges = sec_json.get("exchanges", [])
                state_inc = sec_json.get("stateOfIncorporation")
                fiscal_year_end = sec_json.get("fiscalYearEnd")
                business_addr = sec_json.get("addresses", {}).get("business", {})
                former_names = [f.get("name") for f in sec_json.get("formerNames", []) if f.get("name")]

                # Extract recent filings
                recent = sec_json.get("filings", {}).get("recent", {})
                forms = recent.get("form", [])
                filing_dates = recent.get("filingDate", [])
                report_dates = recent.get("reportDate", [])
                accessions = recent.get("accessionNumber", [])
                doc_descs = recent.get("primaryDocDescription", [])
                primary_docs = recent.get("primaryDocument", [])

                filings_list = []
                for i in range(min(10, len(forms))):
                    acc = accessions[i] if i < len(accessions) else ""
                    acc_clean = acc.replace("-", "") if acc else ""
                    doc_name = primary_docs[i] if i < len(primary_docs) else ""
                    doc_url = (
                        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_clean}/{doc_name}"
                        if acc_clean and doc_name
                        else f"https://www.sec.gov/edgar/browse/?CIK={padded_cik}"
                    )
                    filings_list.append({
                        "form": forms[i] if i < len(forms) else "",
                        "filing_date": filing_dates[i] if i < len(filing_dates) else None,
                        "report_date": report_dates[i] if i < len(report_dates) else None,
                        "accession_number": acc,
                        "description": doc_descs[i] if i < len(doc_descs) else "",
                        "document_url": doc_url
                    })

                record = {
                    "cik": padded_cik,
                    "legal_name": legal_name,
                    "tickers": tickers,
                    "exchanges": exchanges,
                    "sic": sic,
                    "sic_description": sic_desc,
                    "state_of_incorporation": state_inc,
                    "fiscal_year_end": fiscal_year_end,
                    "business_address": business_addr,
                    "former_names": former_names,
                    "recent_filings": filings_list,
                    "filings_count": len(filings_list),
                    "canonical_url": f"https://www.sec.gov/edgar/browse/?CIK={padded_cik}",
                    "source": "US Securities and Exchange Commission (SEC) EDGAR"
                }

                entity = EntityPayload(
                    type=EntityType.ORGANIZATION,
                    value=legal_name,
                    confidence=0.99,
                    sources=[self.provider_id],
                    metadata={
                        "cik": padded_cik,
                        "tickers": tickers,
                        "sic": sic,
                        "sic_description": sic_desc,
                        "state_of_incorporation": state_inc,
                        "former_names": former_names,
                        "source": "US SEC EDGAR",
                        "canonical_url": record["canonical_url"],
                        "match_type": "CONFIRMED_REGULATORY_IDENTITY"
                    }
                )

                ev = ModuleSDK.create_evidence(
                    source="US Securities and Exchange Commission (SEC) EDGAR",
                    provider=self.provider_id,
                    module="osint",
                    raw_data={
                        "cik": padded_cik,
                        "legal_name": legal_name,
                        "recent_filings": filings_list[:5]
                    },
                    reference=f"Target: {query} (CIK: {padded_cik})"
                )

                return ProviderResponse(
                    provider_id=self.provider_id,
                    status="success",
                    duration_ms=duration,
                    raw_data={
                        "target": query,
                        "cik": padded_cik,
                        "record": record,
                        "records": [record],
                        "count": 1,
                        "entities": [entity.dict()],
                        "evidence": [ev.dict() if hasattr(ev, "dict") else ev]
                    }
                )

        except httpx.TimeoutException:
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error="SEC EDGAR API request timed out."
            )
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"SEC EDGAR query failed for '{query}': {e}")
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error=f"SEC EDGAR query error: {str(e)}"
            )
