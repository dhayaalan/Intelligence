import logging
import uuid
from typing import Any, Dict, List
from datetime import datetime
from app.module_sdk.contract import IntelligenceModule
from app.module_sdk.manifest import ModuleManifest
from app.module_sdk.models import (
    HealthCheckResult, ModuleHealthStatus, NormalizedModuleResult,
    SearchContext, EntityPayload, RelationshipPayload, EvidencePayload,
    EntityType, RelationshipType
)
from app.modules.geo_intelligence.manifest import GEO_INTELLIGENCE_MANIFEST
from app.modules.geo_intelligence.service import geo_intelligence_service
from app.modules.geo_intelligence.models import (
    GeoFilterParams, TimeFilterRange, GeographicObservation
)

logger = logging.getLogger("sential.geo_intelligence")

class GeoIntelligenceModule(IntelligenceModule):
    """
    Forensic Geospatial Intelligence Module.
    Extracts, indexes, validates, and provides evidence-backed geographic observations.
    Never fabricates travel routes or continuous movement.
    """
    def __init__(self):
        self._manifest = GEO_INTELLIGENCE_MANIFEST
        self._config: Dict[str, Any] = {}

    @property
    def manifest(self) -> ModuleManifest:
        return self._manifest

    async def initialize(self, config: Dict[str, Any]) -> None:
        self._config = config or {}
        logger.info("Geo Intelligence Module initialized.")

    async def health_check(self) -> HealthCheckResult:
        return HealthCheckResult(
            module_id=self.manifest.id,
            status=ModuleHealthStatus.HEALTHY,
            latency_ms=1.0,
            message="Geospatial Intelligence Engine is operational.",
            details={"providers_active": len(self.manifest.providers)}
        )

    async def capabilities(self) -> List[str]:
        return list(self.manifest.capabilities)

    async def shutdown(self) -> None:
        """Gracefully releases resources."""
        logger.info("Geo Intelligence Module shutdown.")

    async def search(self, context: SearchContext) -> NormalizedModuleResult:
        """
        Executes query-bound geospatial search with server-side temporal filtering.
        """
        opts = context.options or {}
        
        # Parse time range filter
        raw_tr = opts.get("time_range", "30d")
        try:
            time_range = TimeFilterRange(raw_tr)
        except ValueError:
            time_range = TimeFilterRange.LAST_30_DAYS

        filters = GeoFilterParams(
            time_range=time_range,
            start_date=opts.get("start_date"),
            end_date=opts.get("end_date"),
            associated_entity=opts.get("associated_entity"),
            location_types=opts.get("location_types"),
            page=opts.get("page", 1),
            page_size=opts.get("page_size", 50)
        )

        observations = geo_intelligence_service.search_observations(
            query=context.query,
            filters=filters,
            tenant_id=context.tenant_id,
            case_id=opts.get("case_id")
        )

        entities: List[EntityPayload] = []
        relationships: List[RelationshipPayload] = []
        evidence_list: List[EvidencePayload] = []
        sources: List[str] = []

        for obs in observations:
            src = obs.source_provider or "Authorized Geo Ingest"
            if src not in sources:
                sources.append(src)

            coord_str = f"({obs.latitude:.5f}, {obs.longitude:.5f})" if (obs.latitude is not None and obs.longitude is not None) else "Unresolved Coordinates"
            
            # 1. Location Entity
            loc_entity = EntityPayload(
                id=obs.id,
                type=EntityType.LOCATION,
                value=f"{obs.place_name} {coord_str}".strip(),
                confidence=obs.identity_resolution_confidence,
                sources=[src],
                metadata={
                    "place_name": obs.place_name,
                    "location_type": obs.location_type,
                    "latitude": obs.latitude,
                    "longitude": obs.longitude,
                    "accuracy_radius_meters": obs.accuracy_radius_meters,
                    "coordinate_source": obs.coordinate_source,
                    "observation_type": obs.observation_type.value,
                    "event_time": obs.event_time.isoformat() if obs.event_time else None,
                    "observation_time": obs.observation_time.isoformat() if obs.observation_time else None,
                    "publication_time": obs.publication_time.isoformat() if obs.publication_time else None,
                    "collection_time": obs.collection_time.isoformat() if obs.collection_time else None,
                    "access_classification": obs.access_classification
                }
            )
            entities.append(loc_entity)

            # 2. Evidence Record
            ev_id = f"ev_geo_{obs.id}"
            ev = EvidencePayload(
                id=ev_id,
                source=src,
                timestamp=obs.observation_time or obs.collection_time,
                provider="geo_intelligence",
                module="geo_intelligence",
                collection_method=obs.extraction_method,
                reference=obs.source_url or obs.raw_reference or f"Observation {obs.place_name}",
                confidence=obs.identity_resolution_confidence,
                raw_data=obs.dict()
            )
            evidence_list.append(ev)

            # 3. Relationship: Only create LOCATED_AT when observation has an explicit verified association
            target_val = obs.associated_entity_value
            if target_val:
                rel = RelationshipPayload(
                    id=f"rel_{obs.id}",
                    source_entity_value=target_val,
                    target_entity_value=loc_entity.value,
                    relationship_type=RelationshipType.LOCATED_AT,
                    confidence=obs.identity_resolution_confidence,
                    basis=obs.observation_type.value,
                    methodology=obs.extraction_method,
                    uncertainty_notes=f"Temporal uncertainty: {obs.temporal_uncertainty_seconds}s; Radius: {obs.accuracy_radius_meters}m" if obs.accuracy_radius_meters else "Standard accuracy",
                    sources=[src],
                    metadata={"evidence_id": ev_id, "observation_id": obs.id}
                )
                relationships.append(rel)
            elif context.query and context.query.lower() not in obs.place_name.lower():
                # General intelligence mention of a location during search
                rel = RelationshipPayload(
                    id=f"rel_{obs.id}",
                    source_entity_value=context.query,
                    target_entity_value=loc_entity.value,
                    relationship_type=RelationshipType.POSSIBLE_ASSOCIATION,
                    confidence=min(0.60, obs.identity_resolution_confidence),
                    basis="DOCUMENTARY_LOCATION_MENTION",
                    methodology=obs.extraction_method,
                    uncertainty_notes="Location mentioned in collected intelligence source; does not confirm physical presence or personal travel.",
                    sources=[src],
                    metadata={"evidence_id": ev_id, "observation_id": obs.id}
                )
                relationships.append(rel)

        if not entities and context.query:
            clean_q = context.query.split(":", 1)[1].strip() if context.query.lower().startswith(("geo:", "location:", "coords:")) else context.query.strip()
            from app.search.classifier import TargetClassifier
            if TargetClassifier.COORDINATES_REGEX.match(clean_q):
                parts = [p.strip() for p in clean_q.split(",")]
                if len(parts) == 2:
                    try:
                        lat, lon = float(parts[0]), float(parts[1])
                        coord_val = f"Coordinates ({lat:.5f}, {lon:.5f})"
                        loc_ent = EntityPayload(
                            id=f"ent_geo_{uuid.uuid4().hex[:8]}",
                            type=EntityType.LOCATION,
                            value=coord_val,
                            confidence=1.0,
                            sources=["Geographic Coordinates Parser"],
                            metadata={
                                "place_name": coord_val,
                                "latitude": lat,
                                "longitude": lon,
                                "coordinate_source": "DIRECT_OBSERVATION",
                                "observation_type": "KNOWN_FIX"
                            }
                        )
                        entities.append(loc_ent)
                        if "Geographic Coordinates Parser" not in sources:
                            sources.append("Geographic Coordinates Parser")
                        evidence_list.append(EvidencePayload(
                            id=f"ev_coord_{uuid.uuid4().hex[:8]}",
                            source="Geographic Coordinates Parser",
                            timestamp=datetime.utcnow(),
                            provider="geo_intelligence",
                            module="geo_intelligence",
                            collection_method="deterministic_coordinate_parse",
                            reference=clean_q,
                            confidence=1.0,
                            raw_data={"latitude": lat, "longitude": lon, "query": clean_q}
                        ))
                    except ValueError:
                        pass

        return NormalizedModuleResult(
            module="geo_intelligence",
            execution_id=f"exec_geo_{uuid.uuid4().hex[:8]}",
            status="completed",
            entities=entities,
            relationships=relationships,
            evidence=evidence_list,
            sources=sources,
            metadata={
                "total_observations_found": len(observations),
                "time_range_applied": filters.time_range.value,
                "has_coordinates_count": len([o for o in observations if o.latitude is not None])
            }
        )

geo_intelligence_module = GeoIntelligenceModule()
