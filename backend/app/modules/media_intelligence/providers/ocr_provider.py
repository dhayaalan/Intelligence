import time
import base64
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse, ProviderExecutionStatus
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus
from app.modules.media_intelligence.service import media_intelligence_service, PYTESSERACT_AVAILABLE

class OcrProvider(ProviderAdapter):
    """Optical Character Recognition Provider for images and video frames."""

    @property
    def provider_id(self) -> str:
        return "ocr_provider"

    @property
    def name(self) -> str:
        return "Optical Character Recognition (OCR) Engine"

    async def health_check(self) -> HealthCheckResult:
        if PYTESSERACT_AVAILABLE:
            return HealthCheckResult(
                module_id="media_intelligence",
                status=ModuleHealthStatus.HEALTHY,
                latency_ms=0.5,
                message="Tesseract OCR engine is operational"
            )
        else:
            return HealthCheckResult(
                module_id="media_intelligence",
                status=ModuleHealthStatus.DEGRADED,
                latency_ms=0.0,
                message="Pytesseract binary or library not configured"
            )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        options = request.options or {}
        image_data_b64 = options.get("image_base64")

        if not image_data_b64:
            return ProviderResponse(
                provider_id=self.provider_id,
                status=ProviderExecutionStatus.FAILED.value,
                error="No image payload provided for OCR",
                duration_ms=(time.time() - start_time) * 1000
            )

        try:
            image_bytes = base64.b64decode(image_data_b64)
            result = media_intelligence_service.extract_ocr(image_bytes)
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

ocr_provider = OcrProvider()
