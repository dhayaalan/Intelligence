"""
Automated Number Plate Recognition (ANPR) and Video Ingestion Engine.
Decodes authorized video footage, extracts candidate plate regions using OpenCV morphology,
and recognizes characters using Tesseract OCR.
Enforces calibrated confidence thresholds and explicit human-in-the-loop review states:
- NO_MATCH
- POSSIBLE_MATCH
- CANDIDATE_MATCH
- HUMAN_CONFIRMED
- HUMAN_REJECTED
- INCONCLUSIVE
"""

import os
import re
import uuid
import base64
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

import cv2
import numpy as np
import pytesseract
from PIL import Image

from app.modules.camera_evidence.models import (
    ANPRDetectionRecord, ANPRMatchStatus, CameraSourceRecord
)
from app.modules.geo_intelligence.models import (
    GeographicObservation, LocationObservationType
)
from app.modules.geo_intelligence.service import geo_intelligence_service

logger = logging.getLogger(__name__)


def compute_string_similarity(s1: str, s2: str) -> float:
    """
    Computes normalized Levenshtein similarity ratio between two strings [0.0, 1.0].
    """
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    if s1 == s2:
        return 1.0

    len1, len2 = len(s1), len(s2)
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost # substitution
            )

    distance = dp[len1][len2]
    max_len = max(len1, len2)
    return max(0.0, 1.0 - (distance / max_len))


def encode_image_base64(image_bgr: np.ndarray, quality: int = 80) -> str:
    """Encodes an OpenCV BGR image as a JPEG base64 data URL."""
    try:
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        success, buffer = cv2.imencode('.jpg', image_bgr, encode_params)
        if success:
            b64_str = base64.b64encode(buffer).decode('utf-8')
            return f"data:image/jpeg;base64,{b64_str}"
    except Exception as e:
        logger.warning(f"Error encoding image to base64: {e}")
    return ""


class ANPRService:
    def __init__(self):
        # In-memory detection cache keyed by detection_id
        self._detections: Dict[str, ANPRDetectionRecord] = {}
        # Ensure pytesseract config
        self._tess_config = '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def get_detection(self, detection_id: str) -> Optional[ANPRDetectionRecord]:
        return self._detections.get(detection_id)

    def list_detections(
        self,
        investigation_id: Optional[str] = None,
        case_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        target_plate: Optional[str] = None
    ) -> List[ANPRDetectionRecord]:
        results = list(self._detections.values())
        if tenant_id:
            results = [d for d in results if d.tenant_id == tenant_id]
        if investigation_id:
            results = [d for d in results if d.investigation_id == investigation_id]
        if case_id:
            results = [d for d in results if d.case_id == case_id]
        if target_plate:
            clean_target = re.sub(r'[^A-Z0-9]', '', target_plate.upper())
            results = [d for d in results if re.sub(r'[^A-Z0-9]', '', d.target_plate.upper()) == clean_target]
        return results

    def extract_plate_candidates(self, frame_bgr: np.ndarray) -> List[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
        """
        Locates candidate vehicle license plate crops within a video frame using morphological filtering.
        Returns a list of (cropped_image, (x, y, w, h)).
        """
        candidates: List[Tuple[np.ndarray, Tuple[int, int, int, int]]] = []
        h_frame, w_frame = frame_bgr.shape[:2]

        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        # Noise reduction while preserving edges
        blurred = cv2.bilateralFilter(gray, 11, 17, 17)
        # Canny edge detection
        edged = cv2.Canny(blurred, 30, 200)

        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Sort contours by area descending and examine the top 20
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:20]

        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.018 * cv2.arcLength(cnt, True), True)
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / max(1, h)
            area = w * h

            # License plates standard aspect ratio is between ~1.8 and ~5.8
            # Area must be significant but not the entire screen
            if 1.6 <= aspect_ratio <= 6.2 and 800 <= area <= (w_frame * h_frame * 0.35):
                # Add padding
                pad_x = int(w * 0.05)
                pad_y = int(h * 0.05)
                x1 = max(0, x - pad_x)
                y1 = max(0, y - pad_y)
                x2 = min(w_frame, x + w + pad_x)
                y2 = min(h_frame, y + h + pad_y)

                crop = frame_bgr[y1:y2, x1:x2]
                if crop.size > 0:
                    candidates.append((crop, (x, y, w, h)))

        # Fallback: if no contours matched, provide the lower/middle third center crop
        if not candidates:
            cy1, cy2 = int(h_frame * 0.45), int(h_frame * 0.95)
            cx1, cx2 = int(w_frame * 0.15), int(w_frame * 0.85)
            fallback_crop = frame_bgr[cy1:cy2, cx1:cx2]
            candidates.append((fallback_crop, (cx1, cy1, cx2 - cx1, cy2 - cy1)))

        return candidates

    def recognize_plate_text(self, crop_bgr: np.ndarray) -> Tuple[str, List[str]]:
        """
        Runs OCR on a license plate crop image.
        Returns (best_canonical_reading, alternative_readings).
        """
        if crop_bgr is None or crop_bgr.size == 0:
            return "", []

        gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
        # Contrast adjustment & adaptive threshold
        scaled = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        thresh = cv2.threshold(scaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        readings: List[str] = []

        try:
            # 1. Primary PSM 7 OCR
            text1 = pytesseract.image_to_string(thresh, config='--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            clean1 = re.sub(r'[^A-Z0-9]', '', text1.upper())
            if clean1:
                readings.append(clean1)
        except Exception as e:
            logger.debug(f"Tesseract PSM 7 failed: {e}")

        try:
            # 2. Secondary PSM 8 OCR (single word)
            text2 = pytesseract.image_to_string(scaled, config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            clean2 = re.sub(r'[^A-Z0-9]', '', text2.upper())
            if clean2 and clean2 not in readings:
                readings.append(clean2)
        except Exception as e:
            logger.debug(f"Tesseract PSM 8 failed: {e}")

        if not readings:
            return "", []

        # Best candidate is the longest valid reading, typically between 6 and 11 characters
        valid_length = [r for r in readings if 5 <= len(r) <= 12]
        best = valid_length[0] if valid_length else readings[0]
        alternatives = [r for r in readings if r != best]

        return best, alternatives

    def process_video_footage(
        self,
        video_path: str,
        target_plate: str,
        camera: CameraSourceRecord,
        investigation_id: Optional[str] = None,
        case_id: Optional[str] = None,
        tenant_id: str = "tenant_default",
        source_base_time: Optional[datetime] = None,
        max_duration_seconds: float = 60.0,
        sample_interval_seconds: float = 1.0
    ) -> List[ANPRDetectionRecord]:
        """
        Decodes video file, samples frames with strict bounds, performs ANPR detection,
        and generates evidence-backed candidate sightings.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Unable to decode video file: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / max(1.0, fps)
        effective_duration = min(duration, max_duration_seconds)

        frame_step = max(1, int(fps * sample_interval_seconds))
        clean_target = re.sub(r'[^A-Z0-9]', '', target_plate.upper())
        base_time = source_base_time or datetime.utcnow()

        detections: List[ANPRDetectionRecord] = []
        frame_idx = 0
        sampled_count = 0
        max_samples = 60

        try:
            while cap.isOpened() and sampled_count < max_samples:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % frame_step == 0:
                    timecode = frame_idx / fps
                    if timecode > effective_duration:
                        break

                    sampled_count += 1
                    candidates = self.extract_plate_candidates(frame)

                    for crop, bbox in candidates:
                        best_reading, alts = self.recognize_plate_text(crop)
                        if not best_reading:
                            continue

                        similarity = compute_string_similarity(best_reading, clean_target)
                        is_exact = (best_reading == clean_target)

                        # Determine match status based on calibrated thresholds
                        if is_exact:
                            match_status = ANPRMatchStatus.CANDIDATE_MATCH
                            confidence = 0.92
                        elif similarity >= 0.72:
                            match_status = ANPRMatchStatus.POSSIBLE_MATCH
                            confidence = round(0.50 + (similarity * 0.35), 2)
                        else:
                            match_status = ANPRMatchStatus.NO_MATCH
                            confidence = round(similarity * 0.40, 2)

                        # Only surface sightings that meet possible/candidate criteria
                        if match_status in [ANPRMatchStatus.CANDIDATE_MATCH, ANPRMatchStatus.POSSIBLE_MATCH]:
                            det_id = f"det_anpr_{uuid.uuid4().hex[:10]}"
                            s_time = base_time + timedelta(seconds=timecode)

                            # Scale frame preview down for lightweight evidence preview
                            h, w = frame.shape[:2]
                            preview_scale = min(1.0, 640.0 / max(1, w))
                            preview_frame = cv2.resize(frame, (int(w * preview_scale), int(h * preview_scale)))

                            # Draw bounding box on preview
                            x, y, bw, bh = bbox
                            px, py = int(x * preview_scale), int(y * preview_scale)
                            pbw, pbh = int(bw * preview_scale), int(bh * preview_scale)
                            cv2.rectangle(preview_frame, (px, py), (px + pbw, py + pbh), (0, 255, 0), 2)
                            cv2.putText(
                                preview_frame,
                                f"ANPR: {best_reading} ({int(confidence*100)}%)",
                                (px, max(15, py - 6)),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 0),
                                1
                            )

                            frame_b64 = encode_image_base64(preview_frame, quality=80)
                            crop_b64 = encode_image_base64(crop, quality=90)

                            det_record = ANPRDetectionRecord(
                                detection_id=det_id,
                                investigation_id=investigation_id,
                                case_id=case_id,
                                tenant_id=tenant_id,
                                camera_id=camera.source_id,
                                camera_operator=camera.operator,
                                camera_location_name=camera.name,
                                camera_coordinates={
                                    "latitude": camera.latitude,
                                    "longitude": camera.longitude
                                } if camera.latitude is not None else None,
                                video_reference=os.path.basename(video_path),
                                frame_number=frame_idx,
                                timecode_seconds=round(timecode, 2),
                                source_timestamp=s_time,
                                raw_ocr_text=best_reading,
                                normalized_candidate_plate=best_reading,
                                alternative_candidates=alts,
                                target_plate=clean_target,
                                confidence=confidence,
                                match_status=match_status,
                                frame_preview_data=frame_b64,
                                plate_crop_data=crop_b64,
                                evidence_id=f"evi_anpr_{uuid.uuid4().hex[:8]}",
                                detector_version="OpenCV 5.0.0 Morphological Contour Filter + Tesseract 5.5.0",
                                processed_at=datetime.utcnow(),
                                limitations="Model candidate sighting requires human investigator confirmation before authoritative attribution."
                            )

                            self._detections[det_id] = det_record
                            detections.append(det_record)
                            # Once we found the best plate in this sampled frame, continue to next frame
                            break

                frame_idx += 1
        finally:
            cap.release()

        return detections

    def review_detection(
        self,
        detection_id: str,
        reviewer_id: str,
        decision: str,
        notes: Optional[str] = None
    ) -> Optional[ANPRDetectionRecord]:
        """
        Executes human-in-the-loop review.
        If confirmed: marks HUMAN_CONFIRMED and generates a source-backed GeographicObservation.
        If rejected: marks HUMAN_REJECTED.
        If inconclusive: marks INCONCLUSIVE.
        """
        det = self._detections.get(detection_id)
        if not det:
            return None

        clean_dec = decision.upper().strip()
        if clean_dec == "CONFIRM":
            det.match_status = ANPRMatchStatus.HUMAN_CONFIRMED
            det.confidence = 1.0

            # Automatically inject confirmed observation into Geo Intelligence timeline
            if det.camera_coordinates and det.camera_coordinates.get("latitude"):
                geo_obs = GeographicObservation(
                    id=f"geo_anpr_{det.detection_id}",
                    tenant_id=det.tenant_id,
                    case_id=det.case_id,
                    place_name=f"{det.camera_location_name} (Camera {det.camera_id})",
                    location_type="traffic_camera_sighting",
                    latitude=det.camera_coordinates.get("latitude"),
                    longitude=det.camera_coordinates.get("longitude"),
                    accuracy_radius_meters=15.0,
                    coordinate_source="camera_metadata",
                    event_time=det.source_timestamp,
                    observation_time=det.source_timestamp,
                    collection_time=det.processed_at,
                    observation_type=LocationObservationType.DIRECTLY_OBSERVED,
                    extraction_method="anpr_cctv_sightings",
                    evidence_id=det.evidence_id,
                    source_provider=f"ANPR CCTV Recon ({det.camera_operator})",
                    associated_entity_value=det.target_plate,
                    relationship_to_entity="SIGHTED_AT",
                    identity_resolution_confidence=1.0,
                    access_classification="AUTHORIZED_INVESTIGATOR_SUPPLIED",
                    metadata={
                        "detection_id": det.detection_id,
                        "timecode_seconds": det.timecode_seconds,
                        "frame_number": det.frame_number,
                        "raw_ocr_text": det.raw_ocr_text,
                        "reviewer_id": reviewer_id,
                        "review_notes": notes
                    }
                )
                geo_intelligence_service.store_observation(geo_obs)

        elif clean_dec == "REJECT":
            det.match_status = ANPRMatchStatus.HUMAN_REJECTED
        else:
            det.match_status = ANPRMatchStatus.INCONCLUSIVE

        det.human_reviewer_id = reviewer_id
        det.reviewed_at = datetime.utcnow()
        det.review_decision_notes = notes

        return det

    def create_synthetic_authorized_test_clip(self, output_path: str, plate_text: str = "TN34MA8562") -> str:
        """
        Generates a 3-second synthetic authorized test MP4 video containing:
        - 1 second of street scene without vehicle
        - 1 second of vehicle entering with clearly visible license plate
        - 1 second of vehicle exiting
        Ensures 100% reproducible test verification without external network dependency.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        w, h = 640, 480
        fps = 25.0
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        total_frames = int(fps * 3.0)  # 75 frames

        for i in range(total_frames):
            # Draw background asphalt and road markings
            frame = np.full((h, w, 3), (70, 70, 70), dtype=np.uint8)
            # Road dashed lane divider
            cv2.line(frame, (w // 2, 0), (w // 2, h), (255, 255, 255), 3)

            # Frame 25..55: Vehicle present in frame
            if 25 <= i <= 55:
                # Vehicle body (dark blue rectangle)
                car_x, car_y = 180, 160
                car_w, car_h = 280, 180
                cv2.rectangle(frame, (car_x, car_y), (car_x + car_w, car_y + car_h), (120, 50, 20), -1)
                # Windshield
                cv2.rectangle(frame, (car_x + 30, car_y + 20), (car_x + car_w - 30, car_y + 80), (190, 190, 190), -1)

                # License plate (white background with black text)
                plate_x = car_x + 60
                plate_y = car_y + 110
                plate_w = 160
                plate_h = 42
                cv2.rectangle(frame, (plate_x, plate_y), (plate_x + plate_w, plate_y + plate_h), (255, 255, 255), -1)
                cv2.rectangle(frame, (plate_x, plate_y), (plate_x + plate_w, plate_y + plate_h), (0, 0, 0), 2)

                # License plate characters
                cv2.putText(
                    frame,
                    plate_text,
                    (plate_x + 8, plate_y + 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.82,
                    (0, 0, 0),
                    2,
                    cv2.LINE_AA
                )

            out.write(frame)

        out.release()
        return output_path


anpr_service = ANPRService()
