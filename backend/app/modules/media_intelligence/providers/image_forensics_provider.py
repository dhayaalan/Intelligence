import time
import base64
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse, ProviderExecutionStatus
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus
from app.modules.media_intelligence.service import media_intelligence_service

class ImageForensicsProvider(ProviderAdapter):
    """Forensic Image Extraction Provider: SHA-256, EXIF, GPS, dHash/pHash, and C2PA."""
    
    @property
    def provider_id(self) -> str:
        return "image_forensics_provider"

    @property
    def name(self) -> str:
        return "Image Forensics & Provenance Provider"

    async def health_check(self) -> HealthCheckResult:
        return HealthCheckResult(
            module_id="media_intelligence",
            status=ModuleHealthStatus.HEALTHY,
            latency_ms=0.5,
            message="Image forensics provider operational"
        )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        options = request.options or {}
        image_data_b64 = options.get("image_base64")
        filename = options.get("filename", "evidence.jpg")

        if not image_data_b64:
            return ProviderResponse(
                provider_id=self.provider_id,
                status=ProviderExecutionStatus.FAILED.value,
                error="No image payload provided",
                duration_ms=(time.time() - start_time) * 1000
            )

        try:
            image_bytes = base64.b64decode(image_data_b64)
            result = media_intelligence_service.analyze_image(image_bytes, filename=filename)
            return ProviderResponse(
                provider_id=self.provider_id,
                status=ProviderExecutionStatus.SUCCESS.value,
                raw_data=result.dict(),
                duration_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return ProviderResponse(
                provider_id=self.provider_id,
                status=ProviderExecutionStatus.FAILED.value,
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )

image_forensics_provider = ImageForensicsProvider()
