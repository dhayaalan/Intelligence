# Geospatial Intelligence & Location History Engine

## 1. Overview & Forensic Imperatives

The Sential Geospatial Intelligence module (`geo_intelligence`) provides an evidence-backed geospatial observation tracking service. Unlike consumer mapping applications that draw continuous interpolated routes between distant points, Sential adheres to strict forensic standards:

1. **Point Observation Integrity**: Discovered locations represent discrete, source-backed observations at specific timestamps.
2. **No Fabricated Travel Routes**: The platform never generates artificial lines, travel paths, or continuous movement between disjointed location sightings.
3. **Strict Timestamp Separation**: Forensically separates when an event took place (`event_time`), when the document was published (`publication_time`), when the sensor or witness recorded it (`observation_time`), and when our system ingested it (`collection_time`).
4. **Authorized Ingestion Only**: Prohibits covert device tracking or unlawful subscriber location collection.

---

## 2. Forensic Observation Data Model

Each observation conforms to the `GeographicObservation` model:

```python
class GeographicObservation(BaseModel):
    id: str                                        # Stable unique observation identifier
    tenant_id: str                                # Multi-tenant isolation scope
    case_id: Optional[str]                        # Case folder binding
    place_name: str                               # Normalized human-readable location name
    location_type: str                            # e.g., venue, city, waypoint, ip_point_of_presence
    latitude: Optional[float]                     # Verified WGS84 coordinate (-90 to +90)
    longitude: Optional[float]                    # Verified WGS84 coordinate (-180 to +180)
    accuracy_radius_meters: Optional[float]       # Spatial precision radius
    coordinate_source: str                        # exif_gps, gpx_track, source_metadata, geocoded_mention
    
    # Strictly separated timestamps
    event_time: Optional[datetime]                # Time the event physically occurred
    publication_time: Optional[datetime]          # Time the media/article was published
    observation_time: Optional[datetime]          # Time of sensor recording
    collection_time: datetime                     # Time of platform collection
    
    timezone: Optional[str]                       # UTC or local observation timezone
    temporal_uncertainty_seconds: Optional[int]   # Temporal error margin
    
    observation_type: LocationObservationType     # Forensic classification enum
    extraction_method: str                        # Method used to discover the coordinate
    
    evidence_id: Optional[str]                    # Pointer to Evidence Vault record
    source_provider: str                          # Originating provider
    source_url: Optional[str]                     # Canonical source link
    
    associated_entity_id: Optional[str]           # Linked subject entity
    associated_entity_value: Optional[str]        # Subject name / identifier
    relationship_to_entity: str                   # Relationship type (default: LOCATED_AT)
    identity_resolution_confidence: float         # 0.0 to 1.0 confidence
    access_classification: str                    # PUBLIC, RESTRICTED, AUTHORIZED_INVESTIGATOR_SUPPLIED
```

---

## 3. Observation Classification Taxonomy

Observations are classified into distinct evidential grades:

- `DIRECTLY_OBSERVED`: Ground-truth telemetry (e.g., authorized GPS tracks, authentic photo EXIF).
- `SOURCE_REPORTED`: Location explicitly stated by an official agency or news publisher.
- `GEOCODED_PLACE_MENTION`: A text place mention geocoded to nominal administrative coordinates.
- `APPROXIMATE_INFRASTRUCTURE`: Coarse IP-to-datacenter or city-level ISP point-of-presence. Never used to claim device owner personal location.
- `POSSIBLE_ASSOCIATION`: Unconfirmed co-occurrence requiring corroboration.
- `ANALYST_ASSERTED`: Manually entered by investigator with case justification.
- `UNKNOWN_OR_CONFLICTING`: Conflicting location reports across sources.

---

## 4. Supported Authorized File Formats

Investigators can upload authorized location history exports via `POST /api/v1/geo/import`:

1. **GeoJSON / JSON**:
   - Accepts GeoJSON `FeatureCollection` containing `Point` coordinates and ISO 8601 timestamps.
   - Accepts Google Takeout location history format (`latitudeE7`, `longitudeE7`, `timestampMs`).
2. **CSV**:
   - Header-tolerant parser detecting `latitude`, `longitude`, `timestamp`, `name`, and `accuracy`.
3. **GPX (GPS Exchange Format)**:
   - XML parsing of both `<wpt>` (waypoints) and `<trkpt>` (trackpoints) with `<ele>`, `<time>`, and `<name>`.
4. **KML (Keyhole Markup Language)**:
   - XML parsing of `<Placemark>` coordinates and `<TimeStamp><when>` elements.

---

## 5. Server-Side Temporal Filtering

The engine enforces precise server-side date range filtering across all observation lookups:

- `7d`: Observations within the last 7 calendar days.
- `30d`: Observations within the last 30 calendar days.
- `3m`: Observations within the last 90 calendar days.
- `6m`: Observations within the last 180 calendar days.
- `12m`: Observations within the last 365 calendar days.
- `3y`: Observations within the last 3 years.
- `5y`: Observations within the last 5 years.
- `custom`: Investigator-defined `start_date` and `end_date` bounds.

Filtering evaluates `event_time` first, falling back to `observation_time` or `publication_time`. Records are sorted in reverse chronological order and paginated to guarantee rapid rendering on geospatial map canvases.
