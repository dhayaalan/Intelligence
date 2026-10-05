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
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.sdk import ModuleSDK

class ExampleProvider(ProviderAdapter):
    @property
    def provider_id(self) -> str:
        return "example_verifier"

    @property
    def name(self) -> str:
        return "Example Intelligence Verifier"

    async def health_check(self) -> HealthCheckResult:
        return HealthCheckResult(
            status=ModuleHealthStatus.HEALTHY,
            message="Example Verifier is operating normally",
            latency_ms=0.5
        )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        target = request.query.strip()
        duration = round((time.time() - start_time) * 1000, 2)
        return ProviderResponse(
            provider_id=self.provider_id,
            status="success",
            raw_data={"verified_target": target, "confidence_tier": "HIGH"},
            duration_ms=duration
        )

EXAMPLE_MANIFEST = ModuleManifest(
    id="example_intelligence",
    name="Example Intelligence (Plugin)",
    version="1.0.0",
    description="Independent verification module demonstrating dynamic pluggability without Core modification.",
    capabilities=["search", "enrichment"],
    permissions=["search", "view_results"],
    providers=["example_verifier"],
    configuration_schema=[
        ModuleConfigField(
            key="example_api_key",
            label="Example Provider Key",
            type="secret",
            required=False,
            default="example-key-9999",
            description="Dynamic configuration test field"
        )
    ],
    ui_metadata={
        "icon": "Cpu",
        "badge": "Pluggable Module",
        "color": "emerald"
    }
)

class ExampleModule(IntelligenceModule):
    """Example pluggable module demonstrating zero-core-modification extensibility."""

    def __init__(self):
        self._manifest = EXAMPLE_MANIFEST
        self._providers = {
            "example_verifier": ExampleProvider()
        }
        self._config: Dict[str, Any] = {}

    @property
    def manifest(self) -> ModuleManifest:
        return self._manifest

    async def initialize(self, config: Dict[str, Any]) -> None:
        self._config = config or {}

    async def health_check(self) -> HealthCheckResult:
        return HealthCheckResult(
            status=ModuleHealthStatus.HEALTHY,
            message="Example Intelligence module operational",
            latency_ms=0.5,
            provider_statuses={"example_verifier": "healthy"}
        )

    async def capabilities(self) -> List[str]:
        return self._manifest.capabilities

    async def search(self, context: SearchContext) -> NormalizedModuleResult:
        start_time = time.time()
        exec_id = f"exec_ex_{uuid.uuid4().hex[:8]}"

        resp = await self._providers["example_verifier"].execute(
            ProviderRequest(query=context.query, target_type=context.target_type)
        )

        entities = [
            ModuleSDK.create_entity(
                entity_type=EntityType.ORGANIZATION,
                value=f"Verified Organization for {context.query}",
                confidence=0.99,
                sources=["example_intelligence"]
            )
        ]

        ev = ModuleSDK.create_evidence(
            source="ExampleIntelligence - example_verifier",
            provider="example_verifier",
            module=self.module_id,
            raw_data=resp.raw_data,
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
            sources=["example_verifier"],
            duration_ms=duration
        )

    async def shutdown(self) -> None:
        pass

example_module = ExampleModule()
