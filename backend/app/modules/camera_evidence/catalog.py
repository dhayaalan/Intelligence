"""
Public and Open-Data Camera Source Catalog Service.
Maintains curated, documented official public transport camera feeds and open-data portals.
Enforces strict epistemic rules:
- Only enumerates documented official catalogs and approved portals.
- Explicitly forbids IP scanning, guessing RTSP URLs, or unauthorized camera enumeration.
- Differentiates static traffic snapshots from continuous CCTV video streams.
"""

from datetime import datetime
from typing import Dict, List, Optional
from app.modules.camera_evidence.models import (
    CameraSourceRecord, CameraFeedType, CameraAccessMethod, CameraAvailability
)


class PublicCameraCatalogService:
    def __init__(self):
        self._sources: Dict[str, CameraSourceRecord] = {}
        self._load_documented_catalogs()

    def _load_documented_catalogs(self):
        catalogs = [
            CameraSourceRecord(
                source_id="cam_tfl_jamcams",
                operator="Transport for London (TfL)",
                name="TfL JamCams London Open Data",
                source_url="https://api.tfl.gov.uk/Place/Type/JamCam",
                geographic_coverage="Greater London, United Kingdom",
                latitude=51.5074,
                longitude=-0.1278,
                feed_type=CameraFeedType.SNAPSHOT_SERIES,
                access_method=CameraAccessMethod.REST_API,
                licensing_status="UK Open Government Licence (OGL v3.0)",
                availability=CameraAvailability.AVAILABLE,
                auth_requirements="Public Open Data API (App ID/Key optional for rate limit expansion)",
                retention_restrictions="Live traffic snapshots only. Historical recordings not archived on public endpoint.",
                is_public_catalog=True,
                metadata={
                    "total_cameras": 900,
                    "refresh_interval_sec": 180,
                    "jurisdiction": "UK",
                    "format": "JPEG Snapshots"
                }
            ),
            CameraSourceRecord(
                source_id="cam_uk_national_highways",
                operator="National Highways (UK)",
                name="Highways England Traffic CCTV API",
                source_url="https://trafficengland.com/services/cctv",
                geographic_coverage="Strategic Road Network (Motorways & Major A-Roads), England",
                latitude=52.4862,
                longitude=-1.8904,
                feed_type=CameraFeedType.SNAPSHOT_SERIES,
                access_method=CameraAccessMethod.REST_API,
                licensing_status="Open Government Licence v3.0",
                availability=CameraAvailability.AVAILABLE,
                auth_requirements="Traffic England Open Developer Registration",
                retention_restrictions="Real-time situational awareness snapshots; no long-term public footage retention.",
                is_public_catalog=True,
                metadata={
                    "total_cameras": 1500,
                    "refresh_interval_sec": 60,
                    "jurisdiction": "UK"
                }
            ),
            CameraSourceRecord(
                source_id="cam_sg_lta_datamall",
                operator="Singapore Land Transport Authority (LTA)",
                name="LTA DataMall Expressway Traffic Cameras",
                source_url="https://datamall.lta.gov.sg/content/datamall/en/dynamic-data.html",
                geographic_coverage="Singapore Expressways & Arterial Roads",
                latitude=1.3521,
                longitude=103.8198,
                feed_type=CameraFeedType.SNAPSHOT_SERIES,
                access_method=CameraAccessMethod.REST_API,
                licensing_status="Singapore Open Data Licence",
                availability=CameraAvailability.AVAILABLE,
                auth_requirements="LTA DataMall API Key Required",
                retention_restrictions="Snapshots refreshed every 20 seconds; automated bulk archiving restricted by terms.",
                is_public_catalog=True,
                metadata={
                    "total_cameras": 300,
                    "refresh_interval_sec": 20,
                    "jurisdiction": "SG"
                }
            ),
            CameraSourceRecord(
                source_id="cam_us_nycdot",
                operator="New York City Department of Transportation (NYCDOT)",
                name="NYC DOT Traffic Cameras Open Data Feed",
                source_url="https://webcams.nyctmc.org/api/cameras",
                geographic_coverage="New York City (5 Boroughs), New York, USA",
                latitude=40.7128,
                longitude=-74.0060,
                feed_type=CameraFeedType.SNAPSHOT_SERIES,
                access_method=CameraAccessMethod.REST_API,
                licensing_status="NYC Open Data Terms of Use",
                availability=CameraAvailability.AVAILABLE,
                auth_requirements="None (Public Read Access)",
                retention_restrictions="Ephemerally refreshed snapshots; non-commercial public safety awareness.",
                is_public_catalog=True,
                metadata={
                    "total_cameras": 950,
                    "refresh_interval_sec": 30,
                    "jurisdiction": "US"
                }
            ),
            CameraSourceRecord(
                source_id="cam_us_wsdot",
                operator="Washington State Department of Transportation (WSDOT)",
                name="WSDOT Traveler Information Highway Cameras",
                source_url="https://wsdot.wa.gov/traffic/api/highwaycameras",
                geographic_coverage="Washington State, USA",
                latitude=47.6062,
                longitude=-122.3321,
                feed_type=CameraFeedType.SNAPSHOT_SERIES,
                access_method=CameraAccessMethod.REST_API,
                licensing_status="WSDOT Public Domain / State Open Records",
                availability=CameraAvailability.AVAILABLE,
                auth_requirements="WSDOT API Access Code Required",
                retention_restrictions="Real-time road weather and traffic feeds.",
                is_public_catalog=True,
                metadata={
                    "total_cameras": 800,
                    "refresh_interval_sec": 60,
                    "jurisdiction": "US"
                }
            ),
            CameraSourceRecord(
                source_id="cam_in_smart_city_chennai",
                operator="Greater Chennai Corporation & Traffic Police (ICCCC)",
                name="Chennai Integrated Command and Control Centre (ICCCC) Traffic Feeds",
                source_url="https://chennaicitytraffic.gov.in/icccc-live",
                geographic_coverage="Chennai & Tamil Nadu Highways, India",
                latitude=13.0827,
                longitude=80.2707,
                feed_type=CameraFeedType.SNAPSHOT_SERIES,
                access_method=CameraAccessMethod.REST_API,
                licensing_status="Smart Cities Mission Open Portal (Government of Tamil Nadu)",
                availability=CameraAvailability.AVAILABLE,
                auth_requirements="Public Traffic Awareness Endpoint",
                retention_restrictions="Real-time junction snapshots; investigative retention subject to state guidelines.",
                is_public_catalog=True,
                metadata={
                    "total_cameras": 1200,
                    "refresh_interval_sec": 30,
                    "jurisdiction": "IN",
                    "state": "Tamil Nadu"
                }
            ),
            CameraSourceRecord(
                source_id="cam_in_nhai_tms",
                operator="National Highways Authority of India (NHAI)",
                name="NHAI Advanced Traffic Management & Toll Plaza CCTV Network",
                source_url="https://nhai.gov.in/nhai/sites/default/files/ATMS-Guidelines.pdf",
                geographic_coverage="National Highways Network, India",
                latitude=28.6139,
                longitude=77.2090,
                feed_type=CameraFeedType.LIVE_STREAM,
                access_method=CameraAccessMethod.RTSP_CONNECTOR,
                licensing_status="Government of India Ministry of Road Transport and Highways Restricted",
                availability=CameraAvailability.CONFIGURATION_REQUIRED,
                auth_requirements="Official MoRTH / Law Enforcement Credential & Secured Gateway Required",
                retention_restrictions="Restricted internal security network; public scraping strictly forbidden by IT Act.",
                is_public_catalog=True,
                metadata={
                    "jurisdiction": "IN",
                    "access_policy": "LAW_ENFORCEMENT_AUTHORIZED_GATEWAY_ONLY"
                }
            ),
            CameraSourceRecord(
                source_id="cam_in_delhi_traffic",
                operator="Delhi Traffic Police Surveillance Division",
                name="Delhi Urban Traffic Management & ITS Surveillance",
                source_url="https://delhitrafficpolice.nic.in/cctv-traffic",
                geographic_coverage="National Capital Region (NCR), Delhi, India",
                latitude=28.7041,
                longitude=77.1025,
                feed_type=CameraFeedType.SNAPSHOT_SERIES,
                access_method=CameraAccessMethod.REST_API,
                licensing_status="Delhi Police Open Transit Intelligence",
                availability=CameraAvailability.AVAILABLE,
                auth_requirements="Public Open Transit Access",
                retention_restrictions="Real-time corridor management snapshots.",
                is_public_catalog=True,
                metadata={
                    "total_cameras": 2000,
                    "refresh_interval_sec": 45,
                    "jurisdiction": "IN"
                }
            ),
        ]

        for cat in catalogs:
            self._sources[cat.source_id] = cat

    def list_sources(
        self,
        query: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        feed_type: Optional[CameraFeedType] = None
    ) -> List[CameraSourceRecord]:
        results = list(self._sources.values())
        if query:
            q = query.lower().strip()
            results = [
                s for s in results
                if q in s.name.lower() or q in s.operator.lower() or q in s.geographic_coverage.lower()
            ]
        if jurisdiction:
            j = jurisdiction.upper().strip()
            results = [
                s for s in results
                if s.metadata.get("jurisdiction") == j or j in s.geographic_coverage.upper()
            ]
        if feed_type:
            results = [s for s in results if s.feed_type == feed_type]
        return results

    def get_source(self, source_id: str) -> Optional[CameraSourceRecord]:
        return self._sources.get(source_id)

    def register_case_camera(self, camera: CameraSourceRecord) -> CameraSourceRecord:
        """
        Registers an authorized, case-scoped camera source explicitly approved for an investigation.
        """
        self._sources[camera.source_id] = camera
        return camera


camera_catalog_service = PublicCameraCatalogService()
