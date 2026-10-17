from app.module_sdk.manifest import ModuleManifest, ModuleConfigField

GEO_INTELLIGENCE_MANIFEST = ModuleManifest(
    id="geo_intelligence",
    name="Geospatial Intelligence & Location History",
    version="1.0.0",
    description="Evidence-driven geospatial intelligence platform with strict observation schemas, authorized location imports (JSON/CSV/GPX/KML), temporal filtering, and forensic coordinate provenance.",
    capabilities=[
        "search",
        "geo_observation_tracking",
        "location_history_analysis",
        "authorized_file_import",
        "temporal_filtering",
        "coordinate_provenance_verification"
    ],
    permissions=["geo_search", "geo_investigate", "geo_import"],
    providers=["authorized_file_ingest", "exif_metadata_extractor", "incident_geocoder", "ip_approximate_resolver"],
    configuration_schema=[
        ModuleConfigField(
            key="enforce_authorized_import_only",
            label="Enforce Authorized Ingestion Only",
            type="boolean",
            required=False,
            default=True,
            description="Prohibits covert or non-consensual personal device location tracking"
        ),
        ModuleConfigField(
            key="default_accuracy_threshold_meters",
            label="Default Accuracy Threshold (Meters)",
            type="number",
            required=False,
            default=500.0,
            description="Exclude approximate locations with accuracy radius greater than threshold"
        )
    ],
    ui_metadata={
        "icon": "MapPin",
        "badge": "Geospatial Observation Engine",
        "color": "cyan"
    }
)
