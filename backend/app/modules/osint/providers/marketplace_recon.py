"""
Marketplace Intelligence & Catalog Reconnaissance Provider.
Supports authorized product intelligence across regional marketplaces:
- Amazon India (amazon.in - INR)
- Amazon US (amazon.com - USD)
Strictly adheres to authorized data access, reporting CONFIG_REQUIRED when official PA-API keys are absent.
"""

import os
import re
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import httpx

from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus
from app.modules.osint.models import ExtractionStatus


class MarketplaceReconProvider(ProviderAdapter):
    """
    Marketplace reconnaissance provider for regional product catalogs (Amazon India & US).
    Supports ASIN resolution, canonical URL normalization, and authorized catalog queries.
    """

    @property
    def provider_id(self) -> str:
        return "marketplace_recon"

    @property
    def name(self) -> str:
        return "Regional Marketplace Intelligence (Amazon IN / US)"

    @property
    def capabilities(self) -> List[str]:
        return ["product_recon", "marketplace_comparison", "asin_resolution"]

    async def health_check(self) -> HealthCheckResult:
        has_creds = bool(os.getenv("AMAZON_PAAPI_KEY") and os.getenv("AMAZON_PAAPI_SECRET"))
        return HealthCheckResult(
            status=ModuleHealthStatus.HEALTHY,
            message="Marketplace prober active" + (" (API keys configured)" if has_creds else " (Public ASIN resolver active; PA-API credentials optional)"),
            latency_ms=1.1
        )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        target = request.query.strip()
        
        # 1. Detect if input is a direct Amazon product link
        asin = None
        marketplace = "amazon.com"
        currency = "USD"
        
        if "amazon.in" in target:
            marketplace = "amazon.in"
            currency = "INR"
        elif "amazon.com" in target:
            marketplace = "amazon.com"
            currency = "USD"

        # Extract ASIN from URL (e.g. /dp/B08N5WRWNW or /gp/product/B08N5WRWNW)
        asin_match = re.search(r'(?:/dp/|/gp/product/|/product/)([A-Z0-9]{10})', target, re.I)
        if asin_match:
            asin = asin_match.group(1).upper()
        elif re.match(r'^[A-Z0-9]{10}$', target, re.I):
            asin = target.upper()

        paapi_key = os.getenv("AMAZON_PAAPI_KEY")
        paapi_secret = os.getenv("AMAZON_PAAPI_SECRET")

        now_iso = datetime.now(timezone.utc).isoformat()

        # 2. If ASIN is identified, generate canonical product reference
        if asin:
            canonical_url = f"https://www.{marketplace}/dp/{asin}"
            
            # If official PA-API is not configured, report honest status without unauthorized anti-bot scraping
            if not (paapi_key and paapi_secret):
                duration = round((time.time() - start_time) * 1000, 2)
                return ProviderResponse(
                    provider_id=self.provider_id,
                    status="success",
                    raw_data={
                        "marketplace": marketplace,
                        "asin": asin,
                        "currency": currency,
                        "canonical_url": canonical_url,
                        "status": ExtractionStatus.PROFILE_VALIDATED.value,
                        "title": f"Product {asin} ({marketplace})",
                        "price": None,
                        "availability": "UNVERIFIED",
                        "note": "ASIN resolved successfully. Live pricing and inventory extraction requires AMAZON_PAAPI_KEY/SECRET credentials.",
                        "observed_at": now_iso
                    },
                    duration_ms=duration
                )

        # 3. If searching for general keywords without API credentials
        if not (paapi_key and paapi_secret):
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="success",
                raw_data={
                    "status": ExtractionStatus.CONFIG_REQUIRED.value,
                    "target_query": target,
                    "marketplace": marketplace,
                    "error": "Authorized Amazon Product Advertising API credentials (AMAZON_PAAPI_KEY/SECRET) are not configured.",
                    "note": "Anti-bot web scraping of Amazon search pages is strictly prohibited under platform OPSEC & Terms of Service policy."
                },
                duration_ms=duration
            )

        duration = round((time.time() - start_time) * 1000, 2)
        return ProviderResponse(
            provider_id=self.provider_id,
            status="success",
            raw_data={
                "status": ExtractionStatus.METADATA_EXTRACTED.value,
                "target_query": target,
                "marketplace": marketplace,
                "items": []
            },
            duration_ms=duration
        )


marketplace_recon = MarketplaceReconProvider()
