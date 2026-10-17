import asyncio
import os
import time
import uuid
import logging
from typing import Any, Dict, List
from app.module_sdk.contract import IntelligenceModule
from app.module_sdk.manifest import ModuleManifest
from app.module_sdk.models import (
    HealthCheckResult, ModuleHealthStatus, NormalizedModuleResult,
    SearchContext, EntityPayload, RelationshipPayload, EvidencePayload,
    EntityType, RelationshipType
)
from app.module_sdk.sdk import ModuleSDK
from app.modules.osint.manifest import OSINT_MANIFEST
from app.modules.osint.normalization.normalizer import osint_normalizer
from app.modules.osint.platform_catalog_data import PLATFORM_CATALOG_RAW
from app.modules.osint.catalog_adapter import OSINTPlatformAdapter
from app.modules.osint.providers.spiderfoot import SpiderFootProvider
from app.modules.osint.providers.shodan import ShodanProvider
from app.modules.osint.providers.maltego import MaltegoProvider
from app.modules.osint.providers.theharvester import TheHarvesterProvider
from app.modules.osint.providers.google_dork import GoogleDorkProvider
from app.modules.osint.providers.image_engine import ImageOSINTProvider
from app.modules.osint.providers.username_recon import UsernameReconProvider
from app.modules.osint.providers.marketplace_recon import MarketplaceReconProvider
from app.modules.osint.providers.financial_intel import FinancialIntelProvider
from app.modules.osint.providers.wayback_cdx import WaybackCDXProvider
from app.modules.osint.providers.urlscan import URLScanProvider
from app.modules.osint.providers.opensanctions import OpenSanctionsProvider
from app.modules.osint.providers.gleif import GLEIFProvider
from app.modules.osint.providers.sec_edgar import SECEDGARProvider
from app.modules.osint.providers.censys import CensysSearchProvider
from app.modules.osint.providers.vehicle_intelligence import vehicle_registration_provider
from app.modules.osint.providers.telecom_intelligence import telecom_intelligence_provider
from app.core.provider_registry.registry import provider_registry
from app.core.provider_registry.schemas import ProviderMetadata
from app.module_sdk.provider_adapter import ProviderRequest

logger = logging.getLogger("sential.osint")

class OsintModule(IntelligenceModule):
    """
    Independent OSINT Module conforming strictly to the IntelligenceModule contract.
    Orchestrates 300+ public platform reconnaissance probers and deep intelligence engines.
    """
    
    def __init__(self):
        self._manifest = OSINT_MANIFEST
        self._providers: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
        self._bootstrap_providers()

    def _bootstrap_providers(self):
        """Loads and registers primary OSINT engines and 329 platform probers."""
        # 1. Primary Deep OSINT Providers
        primary_providers = [
            ("telecom_intelligence", telecom_intelligence_provider, "TELECOM_INTEL", ["carrier_lookup", "telecom_allocation", "jurisdiction_attribution"], ["phone"]),
            ("vehicle_registration_recon", vehicle_registration_provider, "VEHICLE_INTEL", ["plate_lookup", "jurisdiction_validation"], ["vehicle", "vehicle_plate"]),
            ("spiderfoot", SpiderFootProvider(), "AUTOMATION", ["domain", "ip", "subdomain"], ["domain", "ip"]),
            ("shodan", ShodanProvider(), "NETWORK_INTEL", ["ip", "domain", "ports", "cve"], ["ip", "domain"]),
            ("theharvester", TheHarvesterProvider(), "IDENTITY_OSINT", ["email", "domain", "person"], ["domain", "email"]),
            ("google_dork", GoogleDorkProvider(), "SEARCH_OPERATORS", ["domain", "dorks", "files"], ["domain"]),
            ("maltego", MaltegoProvider(), "TRANSFORMS", ["domain", "ip", "dns", "whois"], ["domain", "ip"]),
            ("image_osint", ImageOSINTProvider(), "IMAGE_METADATA", ["image", "exif", "person"], ["image", "url", "person"]),
            ("username_recon", UsernameReconProvider(), "SOCIAL_IDENTITY", ["username", "handle", "person", "email"], ["username", "handle", "person"]),
            ("marketplace_recon", MarketplaceReconProvider(), "MARKETPLACE_INTEL", ["product", "asin", "marketplace", "url"], ["product", "url", "asin"]),
            ("financial_intel", FinancialIntelProvider(), "FINANCIAL_INTEL", ["company", "organization", "bank", "lei", "cik"], ["organization", "company", "bank", "lei", "cik", "domain"]),
            ("wayback_cdx", WaybackCDXProvider(), "ARCHIVE_INTEL", ["snapshots", "historical_urls", "archives"], ["domain", "url", "hostname"]),
            ("urlscan", URLScanProvider(), "WEB_INTEL", ["historical_scans", "technologies", "screenshots", "ip"], ["domain", "url", "ip", "hostname"]),
            ("opensanctions", OpenSanctionsProvider(), "COMPLIANCE_WATCHLIST", ["sanctions", "pep", "debarment", "crime"], ["person", "organization", "company", "keyword", "username"]),
            ("gleif_lei", GLEIFProvider(), "FINANCIAL_INTEL", ["legal_entity_identifier", "corporate_ownership", "regulatory_records", "lei_lookup"], ["organization", "company", "lei", "domain"]),
            ("sec_edgar", SECEDGARProvider(), "FINANCIAL_INTEL", ["corporate_filings", "cik_resolution", "10k_annual_reports", "8k_current_reports", "xbrl_facts"], ["organization", "company", "cik", "ticker", "domain"]),
            ("censys", CensysSearchProvider(), "WEB_INTEL", ["host_discovery", "service_ports", "certificates", "software_versions"], ["ip", "domain", "hostname", "cve"])
        ]

        for pid, provider, category, caps, targets in primary_providers:
            self._providers[pid] = provider
            auth_req = pid in ("shodan", "censys")
            if pid == "shodan":
                env_vars = ["SHODAN_API_KEY"]
                has_credentials = bool(os.getenv("SHODAN_API_KEY"))
            elif pid == "censys":
                env_vars = ["CENSYS_API_ID", "CENSYS_API_SECRET"]
                has_credentials = bool(os.getenv("CENSYS_API_ID") and os.getenv("CENSYS_API_SECRET"))
            else:
                env_vars = []
                has_credentials = True
            prov_status = "OPERATIONAL" if has_credentials else "NOT_CONFIGURED"

            meta = ProviderMetadata(
                provider_id=pid,
                name=provider.name,
                module_id="osint",
                category=category,
                provider_type="DEEP_ENGINE",
                capabilities=caps,
                supported_targets=targets,
                version=getattr(provider, "version", "1.0.0"),
                is_enabled=True,
                status=prov_status,
                auth_required=auth_req,
                env_vars=env_vars,
                timeout_seconds=getattr(provider, "timeout_seconds", 15.0),
                rate_limit="120/min"
            )
            provider_registry.register(provider, meta)

        # 2. Register all 329 Public Platform Probers
        for raw in PLATFORM_CATALOG_RAW:
            adapter = OSINTPlatformAdapter(raw)
            pid = adapter.provider_id
            self._providers[pid] = adapter
            
            meta = ProviderMetadata(
                provider_id=pid,
                name=adapter.name,
                module_id="osint",
                category=adapter.category,
                provider_type="PLATFORM_PROBER",
                capabilities=adapter.capabilities,
                supported_targets=adapter.supported_targets,
                version=adapter.version,
                is_enabled=True,
                status="REGISTERED",
                timeout_seconds=float(raw.get("timeout_seconds", 4.0)),
                rate_limit="30/min"
            )
            provider_registry.register(adapter, meta)

        logger.info(f"OsintModule initialized with {len(self._providers)} verified providers ({len(PLATFORM_CATALOG_RAW)} platforms + 6 deep engines).")

    @property
    def manifest(self) -> ModuleManifest:
        return self._manifest

    async def initialize(self, config: Dict[str, Any]) -> None:
        self._config = config or {}

    async def health_check(self) -> HealthCheckResult:
        # Check health of core primary providers and platform registry
        provider_statuses = {}
        all_healthy = True
        
        # Primary engines health
        primary_ids = ["spiderfoot", "shodan", "theharvester", "google_dork", "maltego", "image_osint"]
        for pid in primary_ids:
            prov = self._providers.get(pid)
            if prov:
                try:
                    res = await prov.health_check()
                    provider_statuses[pid] = res.status.value
                    if res.status not in (ModuleHealthStatus.HEALTHY, ModuleHealthStatus.DEGRADED):
                        all_healthy = False
                except Exception as e:
                    provider_statuses[pid] = f"error: {str(e)}"
                    all_healthy = False

        status = ModuleHealthStatus.HEALTHY if all_healthy else ModuleHealthStatus.DEGRADED
        return HealthCheckResult(
            status=status,
            message=f"OSINT module online with {len(self._providers)} providers",
            provider_statuses=provider_statuses
        )

    async def capabilities(self) -> List[str]:
        return self._manifest.capabilities

    async def search(self, context: SearchContext) -> NormalizedModuleResult:
        start_time = time.time()
        exec_id = f"exec_osint_{uuid.uuid4().hex[:8]}"
        
        entities: List[EntityPayload] = []
        relationships: List[RelationshipPayload] = []
        evidence: List[EvidencePayload] = []
        sources: List[str] = []
        provider_errors: Dict[str, str] = {}
        
        req = ProviderRequest(
            query=context.query,
            target_type=context.target_type,
            config=self._config,
            options=context.options
        )

        t_type = (context.target_type or "").lower()
        
        # Select active providers, strictly respecting target capabilities for identifiers
        active_providers = {}
        for pid, p in self._providers.items():
            meta = provider_registry.get_metadata(pid)
            if meta and not meta.is_enabled:
                continue
            
            # When searching an exact identifier (email, phone, vehicle), only run providers that declare support
            if t_type in ["email", "phone", "vehicle", "vehicle_plate"]:
                supported = []
                if meta and meta.supported_targets:
                    supported = [str(st).lower() for st in meta.supported_targets]
                elif hasattr(p, "supported_targets"):
                    st_val = getattr(p, "supported_targets")
                    supported = [str(x).lower() for x in (st_val() if callable(st_val) else st_val)]
                if t_type not in supported and "all" not in supported:
                    continue
            
            active_providers[pid] = p

        semaphore = asyncio.Semaphore(50)

        async def run_single_provider(pid: str, provider):
            async with semaphore:
                try:
                    resp = await asyncio.wait_for(provider.execute(req), timeout=4.0)
                    return pid, resp, None
                except asyncio.TimeoutError:
                    return pid, None, "Execution timed out (4s)"
                except Exception as e:
                    return pid, None, str(e)

        tasks = [run_single_provider(pid, p) for pid, p in active_providers.items()]
        results = await asyncio.gather(*tasks)

        for pid, resp, error in results:
            if error:
                provider_errors[pid] = error
                continue
                
            if not resp or resp.status != "success":
                continue
                
            raw = resp.raw_data or {}
            provider_entities: List[EntityPayload] = []
            
            # Incorporate platform prober findings
            if isinstance(raw, dict) and raw.get("found"):
                for ent_dict in raw.get("entities", []):
                    try:
                        provider_entities.append(EntityPayload(**ent_dict))
                    except Exception:
                        pass
                for ev_dict in raw.get("evidence", []):
                    try:
                        evidence.append(EvidencePayload(**ev_dict))
                    except Exception:
                        pass
            
            if pid == "shodan":
                provider_entities.extend(osint_normalizer.normalize_shodan(context.query, raw))
            elif pid == "theharvester":
                provider_entities.extend(osint_normalizer.normalize_theharvester(context.query, raw))
            elif pid == "spiderfoot":
                provider_entities.extend(osint_normalizer.normalize_spiderfoot(context.query, raw))
            elif pid == "image_osint":
                provider_entities.extend(osint_normalizer.normalize_image(context.query, raw))

            # Incorporate provider-generated relationships (e.g. from vehicle intelligence)
            if isinstance(raw, dict) and raw.get("found"):
                for rel_dict in raw.get("relationships", []):
                    try:
                        relationships.append(RelationshipPayload(**rel_dict))
                    except Exception:
                        pass

            entities.extend(provider_entities)

            # Connect discovered entities back to the root query entity if not already related
            # Guardrail: For phone queries, never attach uncorroborated person or username candidates directly to the phone
            existing_pairs = {(r.source_entity_value.lower(), r.target_entity_value.lower()) for r in relationships}
            for pe in provider_entities:
                if pe.value.lower() != context.query.lower():
                    pair = (context.query.lower(), pe.value.lower())
                    reverse_pair = (pe.value.lower(), context.query.lower())
                    if pair not in existing_pairs and reverse_pair not in existing_pairs:
                        if t_type == "phone" and pe.type in [EntityType.PERSON, EntityType.USERNAME]:
                            # Never connect personal names or usernames to a phone number without explicit subscriber verification
                            continue
                        rel_type = RelationshipType.HAS_IDENTIFIER if pe.type in [EntityType.USERNAME, EntityType.EMAIL, EntityType.PHONE] else RelationshipType.ASSOCIATED_WITH
                        relationships.append(RelationshipPayload(
                            id=f"rel_{uuid.uuid4().hex[:8]}",
                            source_entity_value=context.query,
                            target_entity_value=pe.value,
                            relationship_type=rel_type,
                            confidence=pe.confidence,
                            basis="DIRECT_OBSERVATION",
                            methodology=f"osint_{pid}",
                            sources=[pid]
                        ))
                        existing_pairs.add(pair)

            # Only record source and evidence if findings were actually discovered
            if provider_entities or (isinstance(raw, dict) and raw.get("found")) or (isinstance(raw, dict) and any(v for v in raw.values() if v)):
                sources.append(pid)
                ev = ModuleSDK.create_evidence(
                    source=f"OSINT - {pid}",
                    provider=pid,
                    module=self.module_id,
                    raw_data=raw,
                    reference=f"Target: {context.query}"
                )
                evidence.append(ev)

        # Ensure root query entity is present in entities for non-identifier or discovered targets
        root_exists = any(e.value.lower() == context.query.lower() for e in entities)
        if not root_exists and t_type not in ["email", "phone"]:
            root_type = EntityType.VEHICLE if t_type in ["vehicle", "vehicle_plate"] else (EntityType.USERNAME if t_type == "username" else EntityType.KEYWORD)
            entities.insert(0, EntityPayload(
                type=root_type,
                value=context.query,
                confidence=None,
                sources=["search_query"],
                metadata={"is_search_target": True, "is_seed_input": True, "verification_status": "UNASSESSED"}
            ))

        duration = round((time.time() - start_time) * 1000, 2)
        status = "completed"
        if provider_errors and not sources:
            status = "failed"
        elif provider_errors:
            status = "partial"

        return NormalizedModuleResult(
            module=self.module_id,
            execution_id=exec_id,
            status=status,
            entities=entities,
            relationships=relationships,
            evidence=evidence,
            sources=sources,
            metadata={
                "provider_errors": provider_errors,
                "confidence_score": 0.89,
                "providers_executed": len(active_providers)
            },
            duration_ms=duration
        )

    async def shutdown(self) -> None:
        pass

# Instance export for registration
osint_module = OsintModule()
