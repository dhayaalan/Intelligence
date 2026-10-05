import time
import uuid
from typing import Any, Dict, List
from app.module_sdk.contract import IntelligenceModule
from app.module_sdk.manifest import ModuleManifest, ModuleConfigField
from app.module_sdk.models import (
    HealthCheckResult, ModuleHealthStatus, NormalizedModuleResult,
    SearchContext, EntityPayload, RelationshipPayload, EvidencePayload,
    EntityType, RelationshipType
)
from app.module_sdk.sdk import ModuleSDK

TEST_INTEL_MANIFEST = ModuleManifest(
    id="test_intelligence",
    name="Test Intelligence (Plugin)",
    version="1.0.0",
    description="Pluggable verification intelligence module proving modular extensibility without touching Core.",
    capabilities=["search", "enrichment"],
    permissions=["search", "view_results"],
    providers=["mock_verifier"],
    configuration_schema=[
        ModuleConfigField(
            key="test_api_token",
            label="Verification API Token",
            type="secret",
            required=False,
            default="mock-token-12345",
            description="Mock token for testing pluggability"
        )
    ],
    ui_metadata={
        "icon": "Cpu",
        "badge": "Pluggable Extension",
        "color": "emerald"
    }
)

class TestIntelligenceModule(IntelligenceModule):
    """Dynamic pluggable module created to prove zero-core-modification extensibility."""
    
    def __init__(self):
        self._manifest = TEST_INTEL_MANIFEST
        self._config: Dict[str, Any] = {}

    @property
    def manifest(self) -> ModuleManifest:
        return self._manifest

    async def initialize(self, config: Dict[str, Any]) -> None:
        self._config = config or {}

    async def health_check(self) -> HealthCheckResult:
        return HealthCheckResult(
            status=ModuleHealthStatus.HEALTHY,
            message="Test Intelligence plugin operational",
            latency_ms=0.5,
            provider_statuses={"mock_verifier": "healthy"}
        )

    async def capabilities(self) -> List[str]:
        return self._manifest.capabilities

    async def search(self, context: SearchContext) -> NormalizedModuleResult:
        start_time = time.time()
        exec_id = f"exec_test_{uuid.uuid4().hex[:8]}"
        
        entities = [
            ModuleSDK.create_entity(
                entity_type=EntityType.ORGANIZATION,
                value=f"Verified Organization for {context.query}",
                confidence=0.99,
                sources=["test_intelligence"]
            )
        ]
        
        ev = ModuleSDK.create_evidence(
            source="TestIntelligence - mock_verifier",
            provider="mock_verifier",
            module=self.module_id,
            raw_data={"verification_status": "Passed", "target": context.query},
            reference=f"Target: {context.query}"
        )
        
        duration = round((time.time() - start_time) * 1000, 2)
        return NormalizedModuleResult(
            module=self.module_id,
            execution_id=exec_id,
            status="completed",
            entities=entities,
            relationships=[],
            evidence=[ev],
            sources=["mock_verifier"],
            duration_ms=duration
        )

    async def shutdown(self) -> None:
        pass

test_intelligence_module = TestIntelligenceModule()
