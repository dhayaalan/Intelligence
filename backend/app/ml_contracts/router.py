"""
ML Team Integration Router

Provides endpoints for inspecting ML service readiness and issuing requests to
external ML services under the documented integration contract.
"""

from fastapi import APIRouter, Depends, status
from typing import Dict, Any

from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.ml_contracts.models import (
    MLExecutionStatus,
    MLAnalysisRequest,
    MLAnalysisResponse,
    MLPersonaCorrelationRequest,
    MLPersonaCorrelationResponse,
)
from app.ml_contracts.client import ml_service_client

router = APIRouter(prefix="/ml", tags=["ML Team Integration Contract"])


@router.get("/status")
async def get_ml_integration_status(
    current_user: UserRecord = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Returns the operational integration status of the external ML microservice.
    """
    configured = ml_service_client.is_configured
    return {
        "status": MLExecutionStatus.AVAILABLE if configured else MLExecutionStatus.NOT_CONFIGURED,
        "is_configured": configured,
        "service_url": ml_service_client.service_url if configured else None,
        "message": (
            "External ML microservice is connected and active."
            if configured
            else "ML Service is not configured. The external service is operated independently by the ML team."
        ),
        "contract_version": "v1.0.0",
        "supported_capabilities": [
            "evidence_grounded_synthesis",
            "multi_platform_persona_correlation"
        ]
    }


@router.post("/analyze", response_model=MLAnalysisResponse)
async def request_ml_analysis(
    req: MLAnalysisRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Dispatches evidence analysis to the external ML microservice.
    Returns status=not_configured if ML_SERVICE_URL is not configured.
    """
    return await ml_service_client.analyze_evidence(req)


@router.post("/persona-correlation", response_model=MLPersonaCorrelationResponse)
async def request_persona_correlation(
    req: MLPersonaCorrelationRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Dispatches persona correlation to the external ML microservice.
    Returns status=not_configured if ML_SERVICE_URL is not configured.
    """
    return await ml_service_client.correlate_persona(req)
