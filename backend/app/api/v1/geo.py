from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.audit.logger import audit_logger
from app.modules.geo_intelligence.models import (
    GeographicObservation, GeoFilterParams, GeoImportRequest, GeoImportResult,
    TimeFilterRange, LocationObservationType
)
from app.modules.geo_intelligence.service import geo_intelligence_service

router = APIRouter(prefix="/geo", tags=["Geospatial Intelligence"])

@router.post("/import", response_model=GeoImportResult)
async def import_location_history(
    payload: GeoImportRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Ingests authorized location-history exports (JSON, CSV, GPX, KML).
    Strictly preserves coordinate provenance, timestamps, and precision.
    Audits the import action.
    """
    result = geo_intelligence_service.import_observations(
        request=payload,
        tenant_id=current_user.tenant_id,
        case_id=payload.case_id
    )

    audit_logger.log_event(
        event_type="GEO_DATA_IMPORTED",
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        resource_id=payload.case_id or "global",
        action="import_geo_observations",
        details={
            "format": payload.format,
            "imported_count": result.imported_count,
            "skipped_count": result.skipped_count,
            "source_label": payload.source_label
        }
    )

    return result

@router.get("/observations", response_model=List[GeographicObservation])
async def list_observations(
    query: Optional[str] = Query(None, description="Search term for place or entity"),
    time_range: TimeFilterRange = Query(TimeFilterRange.LAST_30_DAYS, description="Server-side temporal filter"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    associated_entity: Optional[str] = Query(None),
    case_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Retrieves evidence-backed geographic observations with temporal bounds.
    """
    filters = GeoFilterParams(
        time_range=time_range,
        start_date=start_date,
        end_date=end_date,
        associated_entity=associated_entity,
        page=page,
        page_size=page_size
    )

    return geo_intelligence_service.search_observations(
        query=query,
        filters=filters,
        tenant_id=current_user.tenant_id,
        case_id=case_id
    )

@router.post("/filter", response_model=List[GeographicObservation])
async def filter_observations(
    filters: GeoFilterParams,
    query: Optional[str] = Query(None),
    case_id: Optional[str] = Query(None),
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Advanced observation filtering with custom temporal ranges and observation types.
    """
    return geo_intelligence_service.search_observations(
        query=query,
        filters=filters,
        tenant_id=current_user.tenant_id,
        case_id=case_id
    )
