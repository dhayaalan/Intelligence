"""
Camera Evidence & Automated Number Plate Recognition (ANPR) Module.
Adheres to strict forensic integrity, source provenance, and human-in-the-loop review.
"""
from app.modules.camera_evidence.models import (
    CameraSourceRecord, CameraFeedType, ANPRMatchStatus, ANPRDetectionRecord,
    ANPRReviewRequest
)
from app.modules.camera_evidence.catalog import camera_catalog_service
from app.modules.camera_evidence.anpr_service import anpr_service

__all__ = [
    "CameraSourceRecord",
    "CameraFeedType",
    "ANPRMatchStatus",
    "ANPRDetectionRecord",
    "ANPRReviewRequest",
    "camera_catalog_service",
    "anpr_service"
]
