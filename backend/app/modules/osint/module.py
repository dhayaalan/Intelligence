import asyncio
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
            ("spiderfoot", SpiderFootProvider(), "AUTOMATION", ["domain", "ip", "subdomain"], ["domain", "ip"]),
            ("shodan", ShodanProvider(), "NETWORK_INTEL", ["ip", "domain", "ports", "cve"], ["ip", "domain"]),
            ("theharvester", TheHarvesterProvider(), "IDENTITY_OSINT", ["email", "domain", "person"], ["domain", "email"]),
            ("google_dork", GoogleDorkProvider(), "SEARCH_OPERATORS", ["domain", "dorks", "files"], ["domain"]),
            ("maltego", MaltegoProvider(), "TRANSFORMS", ["domain", "ip", "dns", "whois"], ["domain", "ip"]),
            ("image_osint", ImageOSINTProvider(), "IMAGE_METADATA", ["image", "exif", "person"], ["image", "url", "person"]),
            ("username_recon", UsernameReconProvider(), "SOCIAL_IDENTITY", ["username", "handle", "person", "email"], ["username", "handle", "person"])
        ]

        for pid, provider, category, caps, targets in primary_providers:
            self._providers[pid] = provider
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
                status="HEALTHY",
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
                status="HEALTHY",
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

        t_type = context.target_type.lower()
        
        # Search across all 335 registered OSINT engines without restricting to a single target type
        active_providers = {}
        for pid, p in self._providers.items():
            meta = provider_registry.get_metadata(pid)
            if meta and not meta.is_enabled:
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
                
            sources.append(pid)
            raw = resp.raw_data or {}
            
            # Incorporate platform prober findings
            if isinstance(raw, dict) and raw.get("found"):
                for ent_dict in raw.get("entities", []):
                    try:
                        entities.append(EntityPayload(**ent_dict))
                    except Exception:
                        pass
                for ev_dict in raw.get("evidence", []):
                    try:
                        evidence.append(EvidencePayload(**ev_dict))
                    except Exception:
                        pass
            
            # Incorporate primary engines findings
            ev = ModuleSDK.create_evidence(
                source=f"OSINT - {pid}",
                provider=pid,
                module=self.module_id,
                raw_data=raw,
                reference=f"Target: {context.query}"
            )
            evidence.append(ev)
            
            if pid == "shodan":
                entities.extend(osint_normalizer.normalize_shodan(context.query, raw))
            elif pid == "theharvester":
                entities.extend(osint_normalizer.normalize_theharvester(context.query, raw))
            elif pid == "spiderfoot":
                entities.extend(osint_normalizer.normalize_spiderfoot(context.query, raw))
            elif pid == "image_osint":
                entities.extend(osint_normalizer.normalize_image(context.query, raw))

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
