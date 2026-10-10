"""
ML Service Client

Minimal, decoupled integration client for communicating with the external ML microservice
developed independently by the ML team.

Returns explicit NOT_CONFIGURED status when ML_SERVICE_URL is unset. Never fabricates predictions.
"""

import time
import logging
from typing import Optional
import httpx

from app.core.config import settings
from app.ml_contracts.models import (
    MLExecutionStatus,
    MLAnalysisRequest,
    MLAnalysisResponse,
    MLPersonaCorrelationRequest,
    MLPersonaCorrelationResponse,
)

logger = logging.getLogger(__name__)


class MLServiceClient:
    """
    Client boundary that connects the core Intelligence platform to the external ML service.
    """

    def __init__(self):
        self.service_url = getattr(settings, "ML_SERVICE_URL", None)
        self.api_key = getattr(settings, "ML_SERVICE_API_KEY", None)
        self.timeout_seconds = getattr(settings, "ML_SERVICE_TIMEOUT_SECONDS", 30)

    @property
    def is_configured(self) -> bool:
        return bool(self.service_url and self.service_url.strip())

    async def analyze_evidence(self, request: MLAnalysisRequest) -> MLAnalysisResponse:
        """
        Submits evidence artifacts and query to external ML service for grounded analysis.
        """
        if not self.is_configured:
            return MLAnalysisResponse(
                status=MLExecutionStatus.NOT_CONFIGURED,
                error_message="ML Service is not configured. External ML microservice deployment pending by the ML team.",
                execution_time_ms=0.0
            )

        start_time = time.time()
        headers = {
            "Content-Type": "application/json",
            "X-Tenant-ID": request.context.tenant_id,
            "X-User-ID": request.context.user_id,
            "X-Trace-ID": request.context.trace_id,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        target_url = f"{self.service_url.rstrip('/')}/v1/analyze"

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                res = await client.post(target_url, json=request.dict(), headers=headers)
                elapsed = (time.time() - start_time) * 1000

                if res.status_code == 200:
                    data = res.json()
                    data["execution_time_ms"] = elapsed
                    return MLAnalysisResponse(**data)
                else:
                    return MLAnalysisResponse(
                        status=MLExecutionStatus.FAILED,
                        error_message=f"External ML service returned status HTTP {res.status_code}: {res.text[:200]}",
                        execution_time_ms=elapsed
                    )
        except httpx.TimeoutException:
            elapsed = (time.time() - start_time) * 1000
            return MLAnalysisResponse(
                status=MLExecutionStatus.TIMEOUT,
                error_message=f"Request to external ML service timed out after {self.timeout_seconds}s",
                execution_time_ms=elapsed
            )
        except Exception as exc:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"Failed to communicate with external ML service: {exc}")
            return MLAnalysisResponse(
                status=MLExecutionStatus.UNAVAILABLE,
                error_message=f"Failed to communicate with external ML service: {str(exc)}",
                execution_time_ms=elapsed
            )

    async def correlate_persona(self, request: MLPersonaCorrelationRequest) -> MLPersonaCorrelationResponse:
        """
        Submits handle and context to external ML service for persona correlation.
        """
        if not self.is_configured:
            return MLPersonaCorrelationResponse(
                status=MLExecutionStatus.NOT_CONFIGURED,
                error_message="ML Service is not configured. External ML microservice deployment pending by the ML team.",
                execution_time_ms=0.0
            )

        start_time = time.time()
        headers = {
            "Content-Type": "application/json",
            "X-Tenant-ID": request.context.tenant_id,
            "X-User-ID": request.context.user_id,
            "X-Trace-ID": request.context.trace_id,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        target_url = f"{self.service_url.rstrip('/')}/v1/persona-correlation"

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                res = await client.post(target_url, json=request.dict(), headers=headers)
                elapsed = (time.time() - start_time) * 1000

                if res.status_code == 200:
                    data = res.json()
                    data["execution_time_ms"] = elapsed
                    return MLPersonaCorrelationResponse(**data)
                else:
                    return MLPersonaCorrelationResponse(
                        status=MLExecutionStatus.FAILED,
                        error_message=f"External ML service returned status HTTP {res.status_code}: {res.text[:200]}",
                        execution_time_ms=elapsed
                    )
        except httpx.TimeoutException:
            elapsed = (time.time() - start_time) * 1000
            return MLPersonaCorrelationResponse(
                status=MLExecutionStatus.TIMEOUT,
                error_message=f"Request to external ML service timed out after {self.timeout_seconds}s",
                execution_time_ms=elapsed
            )
        except Exception as exc:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"Failed to communicate with external ML service: {exc}")
            return MLPersonaCorrelationResponse(
                status=MLExecutionStatus.UNAVAILABLE,
                error_message=f"Failed to communicate with external ML service: {str(exc)}",
                execution_time_ms=elapsed
            )


ml_service_client = MLServiceClient()
