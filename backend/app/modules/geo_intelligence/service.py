import logging
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from app.core.database import db
from app.modules.geo_intelligence.models import (
    GeographicObservation, GeoFilterParams, GeoImportRequest, GeoImportResult,
    TimeFilterRange, LocationObservationType
)
from app.modules.geo_intelligence.parsers import (
    parse_geo_json, parse_geo_csv, parse_geo_gpx, parse_geo_kml
)
from app.infrastructure.mongodb.client import get_database, get_sync_database

logger = logging.getLogger("sential.geo_intelligence")

class GeoIntelligenceService:
    """
    Dedicated Geospatial Intelligence Engine.
    Enforces honest timeline observation tracking, strict coordinate provenance,
    server-side temporal filtering, and authorized location file imports.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._memory_observations: Dict[str, GeographicObservation] = {}

    def _get_time_boundary(self, time_range: TimeFilterRange, start_date: Optional[datetime], end_date: Optional[datetime]) -> Tuple[Optional[datetime], Optional[datetime]]:
        now = datetime.utcnow()
        if time_range == TimeFilterRange.LAST_7_DAYS:
            return now - timedelta(days=7), now
        elif time_range == TimeFilterRange.LAST_30_DAYS:
            return now - timedelta(days=30), now
        elif time_range == TimeFilterRange.LAST_3_MONTHS:
            return now - timedelta(days=90), now
        elif time_range == TimeFilterRange.LAST_6_MONTHS:
            return now - timedelta(days=180), now
        elif time_range == TimeFilterRange.LAST_12_MONTHS:
            return now - timedelta(days=365), now
        elif time_range == TimeFilterRange.LAST_3_YEARS:
            return now - timedelta(days=3*365), now
        elif time_range == TimeFilterRange.LAST_5_YEARS:
            return now - timedelta(days=5*365), now
        elif time_range == TimeFilterRange.CUSTOM:
            return start_date, end_date or now
        return None, None

    def store_observation(self, obs: GeographicObservation) -> GeographicObservation:
        with self._lock:
            self._memory_observations[obs.id] = obs
        
        # Persist to MongoDB
        try:
            sync_db = get_sync_database()
            if sync_db is not None:
                sync_db.geo_observations.update_one(
                    {"id": obs.id, "tenant_id": obs.tenant_id},
                    {"$set": obs.dict()},
                    upsert=True
                )
        except Exception as e:
            logger.warning(f"Could not persist geo observation {obs.id} to MongoDB: {e}")
            
        return obs

    def import_observations(
        self, request: GeoImportRequest, tenant_id: str, case_id: Optional[str] = None
    ) -> GeoImportResult:
        fmt = request.format.lower().strip()
        obs_list: List[GeographicObservation] = []
        errors: List[str] = []

        if fmt in ["json", "geojson"]:
            obs_list, errors = parse_geo_json(request.content, tenant_id, case_id, request.source_label)
        elif fmt == "csv":
            obs_list, errors = parse_geo_csv(request.content, tenant_id, case_id, request.source_label)
        elif fmt == "gpx":
            obs_list, errors = parse_geo_gpx(request.content, tenant_id, case_id, request.source_label)
        elif fmt == "kml":
            obs_list, errors = parse_geo_kml(request.content, tenant_id, case_id, request.source_label)
        else:
            return GeoImportResult(
                success=False,
                imported_count=0,
                skipped_count=0,
                errors=[f"Unsupported format '{fmt}'. Supported: json, csv, gpx, kml"]
            )

        imported = 0
        for obs in obs_list:
            self.store_observation(obs)
            imported += 1

        return GeoImportResult(
            success=len(errors) == 0 or imported > 0,
            imported_count=imported,
            skipped_count=len(errors),
            errors=errors,
            observations=obs_list
        )

    def search_observations(
        self,
        query: Optional[str],
        filters: GeoFilterParams,
        tenant_id: str,
        case_id: Optional[str] = None
    ) -> List[GeographicObservation]:
        start_bound, end_bound = self._get_time_boundary(
            filters.time_range, filters.start_date, filters.end_date
        )

        with self._lock:
            all_obs = list(self._memory_observations.values())

        # If MongoDB has observations, retrieve them
        try:
            sync_db = get_sync_database()
            if sync_db is not None:
                q: Dict[str, Any] = {"tenant_id": tenant_id}
                if case_id:
                    q["case_id"] = case_id
                cursor = sync_db.geo_observations.find(q)
                mongo_obs = [GeographicObservation(**doc) for doc in cursor]
                # Merge into in-memory store
                for mo in mongo_obs:
                    if mo.id not in self._memory_observations:
                        with self._lock:
                            self._memory_observations[mo.id] = mo
                all_obs = list(self._memory_observations.values())
        except Exception as e:
            logger.debug(f"MongoDB read fallback to memory: {e}")

        results: List[GeographicObservation] = []
        q_lower = query.lower().strip() if query else ""

        for obs in all_obs:
            # Tenant isolation
            if obs.tenant_id != tenant_id and obs.tenant_id != "platform_admin":
                continue

            # Strict case isolation if case_id specified
            if case_id and obs.case_id != case_id:
                continue

            # Query match on place_name or metadata
            if q_lower:
                match = (
                    q_lower in obs.place_name.lower() or
                    (obs.associated_entity_value and q_lower in obs.associated_entity_value.lower()) or
                    (obs.source_provider and q_lower in obs.source_provider.lower())
                )
                if not match:
                    continue

            # Entity filter
            if filters.associated_entity:
                ae = filters.associated_entity.lower()
                if not obs.associated_entity_value or ae not in obs.associated_entity_value.lower():
                    continue

            # Confidence threshold
            if obs.identity_resolution_confidence < filters.min_confidence:
                continue

            # Temporal filtering (checks event_time first, then observation_time, then publication_time)
            effective_time = obs.event_time or obs.observation_time or obs.publication_time
            if effective_time:
                if start_bound and effective_time < start_bound:
                    continue
                if end_bound and effective_time > end_bound:
                    continue
            elif start_bound:
                # If record has no valid historical timestamp, check collection_time but note uncertainty
                if obs.collection_time < start_bound:
                    continue

            # Location type filter
            if filters.location_types and obs.location_type not in filters.location_types:
                continue

            # Observation type filter
            if filters.observation_types and obs.observation_type not in filters.observation_types:
                continue

            results.append(obs)

        # Sort chronologically by effective timestamp
        results.sort(
            key=lambda o: o.event_time or o.observation_time or o.publication_time or o.collection_time,
            reverse=True
        )

        # Pagination
        skip = (filters.page - 1) * filters.page_size
        return results[skip : skip + filters.page_size]

geo_intelligence_service = GeoIntelligenceService()
