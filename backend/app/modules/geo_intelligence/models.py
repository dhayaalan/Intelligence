from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class LocationObservationType(str, Enum):
    DIRECTLY_OBSERVED = "DIRECTLY_OBSERVED"
    SOURCE_REPORTED = "SOURCE_REPORTED"
    APPROXIMATE_INFRASTRUCTURE = "APPROXIMATE_INFRASTRUCTURE"
    GEOCODED_PLACE_MENTION = "GEOCODED_PLACE_MENTION"
    POSSIBLE_ASSOCIATION = "POSSIBLE_ASSOCIATION"
    ANALYST_ASSERTED = "ANALYST_ASSERTED"
    UNKNOWN_OR_CONFLICTING = "UNKNOWN_OR_CONFLICTING"

class TimeFilterRange(str, Enum):
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_3_MONTHS = "3m"
    LAST_6_MONTHS = "6m"
    LAST_12_MONTHS = "12m"
    LAST_3_YEARS = "3y"
    LAST_5_YEARS = "5y"
    CUSTOM = "custom"

class GeographicObservation(BaseModel):
    """
    Evidence-backed location observation adhering to strict forensic integrity.
    Never fabricates intermediate points, continuous movement, or precise coordinates.
    Separates event, publication, observation, and collection timestamps.
    """
    id: str
    tenant_id: str = "platform_admin"
    case_id: Optional[str] = None
    place_name: str
    location_type: str = "place"  # "city", "country", "venue", "ip_point_of_presence", "cell_tower", "waypoint"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy_radius_meters: Optional[float] = None
    coordinate_source: str = "unknown"  # "exif_gps", "gpx_track", "source_metadata", "geocoded_mention", "ip_approximate"
    
    # Strictly separated timestamps
    event_time: Optional[datetime] = None          # When the event physically took place
    publication_time: Optional[datetime] = None    # When the document/article/post was published
    observation_time: Optional[datetime] = None    # When the sensor/witness observed the entity
    collection_time: datetime = Field(default_factory=datetime.utcnow)  # When our system collected the record
    
    timezone: Optional[str] = "UTC"
    temporal_uncertainty_seconds: Optional[int] = None
    
    observation_type: LocationObservationType = LocationObservationType.SOURCE_REPORTED
    extraction_method: str = "source_extract"  # "exif", "file_import", "named_entity_geocoding", "ip_lookup"
    
    # Evidence & Provenance
    evidence_id: Optional[str] = None
    source_provider: str = "unknown"
    source_url: Optional[str] = None
    raw_reference: Optional[str] = None
    
    # Entity Relationship
    associated_entity_id: Optional[str] = None
    associated_entity_value: Optional[str] = None
    relationship_to_entity: str = "OBSERVED_AT"
    identity_resolution_confidence: float = 1.0  # 0.0 to 1.0
    
    access_classification: str = "PUBLIC"  # "PUBLIC", "RESTRICTED", "AUTHORIZED_INVESTIGATOR_SUPPLIED"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GeoFilterParams(BaseModel):
    time_range: TimeFilterRange = TimeFilterRange.LAST_30_DAYS
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    associated_entity: Optional[str] = None
    location_types: Optional[List[str]] = None
    observation_types: Optional[List[LocationObservationType]] = None
    min_confidence: float = 0.0
    page: int = 1
    page_size: int = 50

class GeoImportRequest(BaseModel):
    format: str  # "json", "csv", "gpx", "kml"
    content: str  # raw text / file content
    case_id: Optional[str] = None
    source_label: str = "Authorized Investigator Import"
    authorization_reference: Optional[str] = None

class GeoImportResult(BaseModel):
    success: bool
    imported_count: int = 0
    skipped_count: int = 0
    errors: List[str] = Field(default_factory=list)
    observations: List[GeographicObservation] = Field(default_factory=list)
