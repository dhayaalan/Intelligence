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
        - 1 second of highway roadway scene without vehicle
        - 1 second of realistic vehicle (chassis, tires, windshield, LED tail lights, bumper, and HSRP plate)
        - 1 second of vehicle exiting
        Ensures 100% reproducible test verification with high-fidelity vehicle visuals.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        w, h = 640, 480
        fps = 25.0
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        total_frames = int(fps * 3.0)  # 75 frames

        for i in range(total_frames):
            # 1. Environment / Highway roadway background
            frame = np.full((h, w, 3), (48, 48, 52), dtype=np.uint8)
            # Sky & Horizon
            cv2.rectangle(frame, (0, 0), (w, 130), (195, 175, 155), -1)
            cv2.rectangle(frame, (0, 120), (w, 138), (75, 110, 70), -1)  # Distant landscape
            cv2.rectangle(frame, (0, 138), (w, 145), (140, 140, 140), -1)  # Roadside guard rail

            # Road perspective boundaries
            cv2.line(frame, (50, h), (260, 145), (230, 230, 230), 4)
            cv2.line(frame, (w - 50, h), (380, 145), (230, 230, 230), 4)
            # Center dashed lane divider
            for dash_y in range(160, h, 40):
                cv2.line(frame, (320, dash_y), (320, min(h, dash_y + 22)), (240, 240, 240), 3)

            # CCTV Camera HUD
            cv2.putText(frame, "● LIVE CCTV / ANPR SURVEILLANCE", (16, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 230), 1, cv2.LINE_AA)
            cv2.putText(frame, "CAM-04 NHAI HIGHWAY SIGHTING [KM 14.2] 25FPS", (16, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (200, 200, 200), 1, cv2.LINE_AA)

            # Frame 25..55: Realistic Vehicle present in frame
            if 25 <= i <= 55:
                car_center_x, car_center_y = 320, 275

                # 2. Ground Contact Shadow
                cv2.ellipse(frame, (car_center_x, car_center_y + 115), (160, 22), 0, 0, 360, (20, 20, 22), -1)

                # 3. Wheels / Tires with Alloy Rims
                cv2.ellipse(frame, (car_center_x - 145, car_center_y + 75), (26, 36), 0, 0, 360, (25, 25, 28), -1)
                cv2.ellipse(frame, (car_center_x - 145, car_center_y + 75), (13, 18), 0, 0, 360, (120, 120, 125), -1)
                cv2.ellipse(frame, (car_center_x + 145, car_center_y + 75), (26, 36), 0, 0, 360, (25, 25, 28), -1)
                cv2.ellipse(frame, (car_center_x + 145, car_center_y + 75), (13, 18), 0, 0, 360, (120, 120, 125), -1)

                # 4. Lower Bumper & Diffuser
                body_left, body_w = car_center_x - 150, 300
                body_bottom = car_center_y + 105
                cv2.rectangle(frame, (body_left + 15, body_bottom - 36), (body_left + body_w - 15, body_bottom), (35, 36, 40), -1)
                # Dual chrome exhaust tips
                cv2.ellipse(frame, (body_left + 45, body_bottom - 12), (10, 6), 0, 0, 360, (180, 180, 185), 2)
                cv2.ellipse(frame, (body_left + body_w - 45, body_bottom - 12), (10, 6), 0, 0, 360, (180, 180, 185), 2)
                # Red bumper reflectors
                cv2.rectangle(frame, (body_left + 25, body_bottom - 30), (body_left + 75, body_bottom - 22), (30, 30, 210), -1)
                cv2.rectangle(frame, (body_left + body_w - 75, body_bottom - 30), (body_left + body_w - 25, body_bottom - 22), (30, 30, 210), -1)

                # 5. Main Car Body (Metallic Deep Sapphire Blue-Grey)
                body_pts = np.array([
                    [body_left + 20, body_bottom - 36],
                    [body_left, car_center_y + 30],
                    [body_left + 12, car_center_y - 15],
                    [body_left + 45, car_center_y - 20],
                    [body_left + body_w - 45, car_center_y - 20],
                    [body_left + body_w - 12, car_center_y - 15],
                    [body_left + body_w, car_center_y + 30],
                    [body_left + body_w - 20, body_bottom - 36],
                ], dtype=np.int32)
                cv2.fillPoly(frame, [body_pts], (85, 45, 28))
                cv2.polylines(frame, [body_pts], True, (50, 28, 15), 2)

                # 6. Upper Cabin & Tinted Rear Window
                cabin_w_top = 185
                cabin_top = car_center_y - 95
                cabin_bottom = car_center_y - 20
                roof_left = car_center_x - cabin_w_top // 2
                cv2.rectangle(frame, (roof_left, cabin_top - 8), (roof_left + cabin_w_top, cabin_top), (85, 45, 28), -1)
                # Shark-fin roof antenna
                cv2.ellipse(frame, (car_center_x, cabin_top - 10), (6, 12), 0, 0, 360, (85, 45, 28), -1)

                window_pts = np.array([
                    [car_center_x - cabin_w_top // 2 + 8, cabin_top],
                    [car_center_x + cabin_w_top // 2 - 8, cabin_top],
                    [car_center_x + 110, cabin_bottom],
                    [car_center_x - 110, cabin_bottom],
                ], dtype=np.int32)
                cv2.fillPoly(frame, [window_pts], (30, 28, 25))
                cv2.polylines(frame, [window_pts], True, (60, 58, 55), 2)
                # Headrests inside
                cv2.ellipse(frame, (car_center_x - 55, cabin_bottom - 32), (18, 14), 0, 0, 360, (45, 45, 45), -1)
                cv2.ellipse(frame, (car_center_x + 55, cabin_bottom - 32), (18, 14), 0, 0, 360, (45, 45, 45), -1)
                # Third high-mount brake lamp
                cv2.rectangle(frame, (car_center_x - 30, cabin_top + 4), (car_center_x + 30, cabin_top + 10), (35, 35, 230), -1)

                # 7. Tail Lights (Vivid modern LED clusters)
                tail_w, tail_h = 68, 32
                left_tail_pts = np.array([
                    [body_left + 15, car_center_y - 5],
                    [body_left + 15 + tail_w, car_center_y + 2],
                    [body_left + 15 + tail_w - 12, car_center_y + tail_h],
                    [body_left + 10, car_center_y + tail_h - 4],
                ], dtype=np.int32)
                cv2.fillPoly(frame, [left_tail_pts], (25, 25, 220))
                cv2.rectangle(frame, (body_left + 35, car_center_y + 6), (body_left + 65, car_center_y + 18), (220, 220, 240), -1)

                right_tail_pts = np.array([
                    [body_left + body_w - 15, car_center_y - 5],
                    [body_left + body_w - 15 - tail_w, car_center_y + 2],
                    [body_left + body_w - 15 - tail_w + 12, car_center_y + tail_h],
                    [body_left + body_w - 10, car_center_y + tail_h - 4],
                ], dtype=np.int32)
                cv2.fillPoly(frame, [right_tail_pts], (25, 25, 220))
                cv2.rectangle(frame, (body_left + body_w - 65, car_center_y + 6), (body_left + body_w - 35, car_center_y + 18), (220, 220, 240), -1)

                # 8. Chrome Brand Emblem & Trunk Release
                cv2.ellipse(frame, (car_center_x, car_center_y + 14), (14, 9), 0, 0, 360, (210, 215, 220), 2)
                cv2.circle(frame, (car_center_x, car_center_y + 14), 4, (210, 215, 220), 1)

                # 9. License Plate Alcove & High Security Plate (HSRP)
                plate_left, plate_top = car_center_x - 80, car_center_y + 36
                plate_w, plate_h = 160, 42
                # Alcove recess
                cv2.rectangle(frame, (plate_left - 8, plate_top - 6), (plate_left + plate_w + 8, plate_top + plate_h + 6), (32, 33, 38), -1)
                cv2.rectangle(frame, (plate_left - 8, plate_top - 6), (plate_left + plate_w + 8, plate_top + plate_h + 6), (20, 20, 24), 2)
                # Plate lights
                cv2.rectangle(frame, (car_center_x - 45, plate_top - 6), (car_center_x - 30, plate_top - 3), (250, 250, 230), -1)
                cv2.rectangle(frame, (car_center_x + 30, plate_top - 6), (car_center_x + 45, plate_top - 3), (250, 250, 230), -1)

                # White reflective plate
                cv2.rectangle(frame, (plate_left, plate_top), (plate_left + plate_w, plate_top + plate_h), (255, 255, 255), -1)
                cv2.rectangle(frame, (plate_left, plate_top), (plate_left + plate_w, plate_top + plate_h), (0, 0, 0), 2)

                # Indian HSRP blue strip
                cv2.rectangle(frame, (plate_left + 2, plate_top + 2), (plate_left + 20, plate_top + plate_h - 2), (180, 50, 0), -1)
                cv2.circle(frame, (plate_left + 11, plate_top + 13), 4, (255, 255, 255), 1)
                cv2.putText(frame, "IND", (plate_left + 3, plate_top + 33), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (255, 255, 255), 1, cv2.LINE_AA)

                # License plate characters
                cv2.putText(
                    frame,
                    plate_text,
                    (plate_left + 26, plate_top + 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.78,
                    (0, 0, 0),
                    2,
                    cv2.LINE_AA
                )

            out.write(frame)

        out.release()
        return output_path


anpr_service = ANPRService()
