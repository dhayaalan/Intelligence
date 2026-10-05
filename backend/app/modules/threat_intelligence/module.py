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
from app.modules.threat_intelligence.manifest import THREAT_INTEL_MANIFEST
from app.modules.threat_intelligence.normalization.normalizer import threat_normalizer
from app.modules.threat_intelligence.engines.registry import ScannerRegistry
from app.modules.threat_intelligence.scanner_adapter import ThreatIntelEngineAdapter
from app.core.provider_registry.registry import provider_registry
from app.core.provider_registry.schemas import ProviderMetadata
from app.module_sdk.provider_adapter import ProviderRequest

logger = logging.getLogger("sential.threat_intelligence")

class ThreatIntelligenceModule(IntelligenceModule):
    """
    Independent Threat Intelligence Module conforming strictly to the IntelligenceModule contract.
    Orchestrates all 33 specialized security & threat scanner engines without hardcoded Core logic.
    """
    
    def __init__(self):
        self._manifest = THREAT_INTEL_MANIFEST
        self._providers: Dict[str, ThreatIntelEngineAdapter] = {}
        self._config: Dict[str, Any] = {}
        self._bootstrap_engines()

    def _bootstrap_engines(self):
        """Loads and registers all 33 threat intelligence scanning engines."""
        scanner_reg = ScannerRegistry.get_instance()
        for engine_id, engine in scanner_reg._engines.items():
            adapter = ThreatIntelEngineAdapter(engine)
            self._providers[engine_id] = adapter
            
            # Register in central platform ProviderRegistry
            meta = ProviderMetadata(
                provider_id=engine_id,
                name=adapter.name,
                module_id="threat_intelligence",
                category=adapter.category,
                provider_type="SCANNER_ENGINE",
                capabilities=adapter.capabilities,
                supported_targets=adapter.supported_targets,
                version=adapter.version,
                is_enabled=True,
                status="HEALTHY",
                timeout_seconds=float(engine.timeout_seconds()),
                rate_limit="60/min"
            )
            provider_registry.register(adapter, meta)

        logger.info(f"ThreatIntelligenceModule initialized with {len(self._providers)} verified engines.")

    @property
    def manifest(self) -> ModuleManifest:
        return self._manifest

    async def initialize(self, config: Dict[str, Any]) -> None:
        self._config = config or {}

    async def health_check(self) -> HealthCheckResult:
        provider_statuses = {}
        all_healthy = True
        
        for pid, prov in self._providers.items():
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
            message=f"All {len(self._providers)} Threat Intelligence engines operational" if all_healthy else "Some engines degraded",
            provider_statuses=provider_statuses
        )

    async def capabilities(self) -> List[str]:
        return self._manifest.capabilities

    async def search(self, context: SearchContext) -> NormalizedModuleResult:
        # Fault injection flag support for resilience tests
        if context.options.get("force_failure_threat_intelligence"):
            raise RuntimeError("Threat intelligence cluster unreachable: upstream connection reset")

        start_time = time.time()
        exec_id = f"exec_ti_{uuid.uuid4().hex[:8]}"
        
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
        
        # Search across all 33 registered Threat Intelligence engines concurrently
        active_providers = {}
        for pid, p in self._providers.items():
            meta = provider_registry.get_metadata(pid)
            if meta and not meta.is_enabled:
                continue
            active_providers[pid] = p

        semaphore = asyncio.Semaphore(20)

        async def run_single_provider(pid: str, provider: ThreatIntelEngineAdapter):
            async with semaphore:
                try:
                    resp = await asyncio.wait_for(provider.execute(req), timeout=5.0)
                    return pid, resp, None
                except asyncio.TimeoutError:
                    return pid, None, "Execution timed out (5s)"
                except Exception as e:
                    return pid, None, str(e)

        tasks = [run_single_provider(pid, p) for pid, p in active_providers.items()]
        results = await asyncio.gather(*tasks)

        for pid, resp, error in results:
            if error:
                provider_errors[pid] = error
                continue
                
            if not resp or resp.status != "success":
                if resp and resp.error:
                    provider_errors[pid] = resp.error
                continue
                
            sources.append(pid)
            raw = resp.raw_data or {}
            
            # Incorporate normalized entities
            for ent_dict in raw.get("entities", []):
                try:
                    entities.append(EntityPayload(**ent_dict))
                except Exception:
                    pass

            # Incorporate evidence
            for ev_dict in raw.get("evidence", []):
                try:
                    evidence.append(EvidencePayload(**ev_dict))
                except Exception:
                    pass

            # Findings into evidence summary
            findings = raw.get("findings", [])
            if findings:
                ev = ModuleSDK.create_evidence(
                    source=f"ThreatIntel - {pid}",
                    provider=pid,
                    module=self.module_id,
                    raw_data={"findings": findings, "count": len(findings)},
                    reference=f"Target: {context.query}"
                )
                evidence.append(ev)

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
                "threat_assessment": "Assessed",
                "engines_executed": len(active_providers)
            },
            duration_ms=duration
        )

    async def shutdown(self) -> None:
        pass

# Instance export for registration
threat_intelligence_module = ThreatIntelligenceModule()
