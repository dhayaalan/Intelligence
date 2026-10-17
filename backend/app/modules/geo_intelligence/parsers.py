import csv
import io
import json
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, List, Optional, Tuple
from app.modules.geo_intelligence.models import (
    GeographicObservation, LocationObservationType
)

from datetime import datetime, timezone

def _parse_iso_or_epoch(val: Any) -> Optional[datetime]:
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    if isinstance(val, (int, float)):
        # Support milliseconds or seconds epoch
        if val > 1e11:
            return datetime.fromtimestamp(val / 1000.0, timezone.utc)
        return datetime.fromtimestamp(val, timezone.utc)
    if isinstance(val, str):
        val = val.strip()
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00"))
        except Exception:
            pass
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(val, fmt)
            except ValueError:
                continue
    return None

def parse_geo_json(content: str, tenant_id: str, case_id: Optional[str] = None, source_label: str = "Authorized JSON Import") -> Tuple[List[GeographicObservation], List[str]]:
    observations: List[GeographicObservation] = []
    errors: List[str] = []
    try:
        data = json.loads(content)
    except Exception as e:
        return [], [f"Invalid JSON payload: {e}"]

    # GeoJSON FeatureCollection support
    if isinstance(data, dict) and data.get("type") == "FeatureCollection":
        features = data.get("features", [])
        for idx, feat in enumerate(features):
            geom = feat.get("geometry") or {}
            props = feat.get("properties") or {}
            coords = geom.get("coordinates")
            if geom.get("type") == "Point" and coords and len(coords) >= 2:
                lon, lat = float(coords[0]), float(coords[1])
                if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
                    errors.append(f"Feature {idx}: Coordinates out of range ({lat}, {lon})")
                    continue
                t_str = props.get("time") or props.get("timestamp") or props.get("observation_time")
                obs_t = _parse_iso_or_epoch(t_str)
                obs = GeographicObservation(
                    id=f"geo_obs_{uuid.uuid4().hex[:12]}",
                    tenant_id=tenant_id,
                    case_id=case_id,
                    place_name=props.get("name") or props.get("place_name") or f"Point ({lat:.4f}, {lon:.4f})",
                    location_type=props.get("location_type") or "waypoint",
                    latitude=lat,
                    longitude=lon,
                    accuracy_radius_meters=float(props.get("accuracy", 10.0)),
                    coordinate_source="authorized_import",
                    observation_time=obs_t,
                    observation_type=LocationObservationType.DIRECTLY_OBSERVED,
                    extraction_method="geojson_import",
                    source_provider=source_label,
                    access_classification="AUTHORIZED_INVESTIGATOR_SUPPLIED",
                    metadata=props
                )
                observations.append(obs)
        return observations, errors

    # Custom or Takeout Records list
    items = data if isinstance(data, list) else data.get("locations", data.get("records", [data]))
    for idx, item in enumerate(items):
        try:
            lat = item.get("latitude") or item.get("lat") or item.get("latitudeE7")
            lon = item.get("longitude") or item.get("lon") or item.get("longitudeE7")
            if lat is not None and lon is not None:
                if isinstance(lat, int) and abs(lat) > 90:
                    lat = lat / 1e7
                if isinstance(lon, int) and abs(lon) > 180:
                    lon = lon / 1e7
                lat, lon = float(lat), float(lon)
                
                t_str = item.get("timestamp") or item.get("time") or item.get("timestampMs")
                obs_t = _parse_iso_or_epoch(t_str)
                obs = GeographicObservation(
                    id=f"geo_obs_{uuid.uuid4().hex[:12]}",
                    tenant_id=tenant_id,
                    case_id=case_id,
                    place_name=item.get("name") or item.get("place_name") or f"Location ({lat:.4f}, {lon:.4f})",
                    location_type=item.get("type", "observation"),
                    latitude=lat,
                    longitude=lon,
                    accuracy_radius_meters=float(item.get("accuracy", 15.0)),
                    coordinate_source="authorized_json_import",
                    observation_time=obs_t,
                    observation_type=LocationObservationType.DIRECTLY_OBSERVED,
                    extraction_method="json_import",
                    source_provider=source_label,
                    access_classification="AUTHORIZED_INVESTIGATOR_SUPPLIED",
                    metadata=item
                )
                observations.append(obs)
        except Exception as ex:
            errors.append(f"Row {idx}: {ex}")

    return observations, errors

def parse_geo_csv(content: str, tenant_id: str, case_id: Optional[str] = None, source_label: str = "Authorized CSV Import") -> Tuple[List[GeographicObservation], List[str]]:
    observations: List[GeographicObservation] = []
    errors: List[str] = []
    reader = csv.DictReader(io.StringIO(content))
    
    for idx, row in enumerate(reader):
        try:
            # Flexible field discovery
            lat_key = next((k for k in row.keys() if k and k.lower() in ["latitude", "lat", "y"]), None)
            lon_key = next((k for k in row.keys() if k and k.lower() in ["longitude", "lon", "lng", "x"]), None)
            time_key = next((k for k in row.keys() if k and k.lower() in ["timestamp", "time", "date", "datetime"]), None)
            name_key = next((k for k in row.keys() if k and k.lower() in ["place_name", "name", "location", "label", "city"]), None)
            acc_key = next((k for k in row.keys() if k and k.lower() in ["accuracy", "radius", "precision"]), None)
            
            if not lat_key or not lon_key or not row[lat_key] or not row[lon_key]:
                continue
                
            lat = float(row[lat_key])
            lon = float(row[lon_key])
            if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
                errors.append(f"CSV Row {idx+1}: Coordinates out of range ({lat}, {lon})")
                continue
            obs_time = _parse_iso_or_epoch(row[time_key]) if time_key else None
            accuracy = float(row[acc_key]) if acc_key and row[acc_key] else None
            place_name = row[name_key] if name_key and row[name_key] else f"Coordinate ({lat:.4f}, {lon:.4f})"
            
            obs = GeographicObservation(
                id=f"geo_obs_{uuid.uuid4().hex[:12]}",
                tenant_id=tenant_id,
                case_id=case_id,
                place_name=place_name,
                location_type=row.get("location_type", "waypoint"),
                latitude=lat,
                longitude=lon,
                accuracy_radius_meters=accuracy,
                coordinate_source="authorized_csv_import",
                observation_time=obs_time,
                observation_type=LocationObservationType.DIRECTLY_OBSERVED,
                extraction_method="csv_import",
                source_provider=source_label,
                access_classification="AUTHORIZED_INVESTIGATOR_SUPPLIED",
                metadata=dict(row)
            )
            observations.append(obs)
        except Exception as e:
            errors.append(f"CSV Row {idx+1}: {e}")
            
    return observations, errors

def parse_geo_gpx(content: str, tenant_id: str, case_id: Optional[str] = None, source_label: str = "Authorized GPX Import") -> Tuple[List[GeographicObservation], List[str]]:
    observations: List[GeographicObservation] = []
    errors: List[str] = []
    try:
        root = ET.fromstring(content)
    except Exception as e:
        return [], [f"Failed to parse GPX XML: {e}"]

    # Strip XML namespace if present
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"

    # Parse both waypoints <wpt> and trackpoints <trkpt>
    points = root.findall(f".//{ns}wpt") + root.findall(f".//{ns}trkpt")
    for idx, pt in enumerate(points):
        try:
            if "lat" not in pt.attrib or "lon" not in pt.attrib:
                errors.append(f"GPX point {idx}: Missing required lat/lon coordinate attribute")
                continue
            lat = float(pt.attrib["lat"])
            lon = float(pt.attrib["lon"])
            if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
                errors.append(f"GPX point {idx}: Coordinates out of range ({lat}, {lon})")
                continue
            
            time_el = pt.find(f"{ns}time")
            name_el = pt.find(f"{ns}name")
            
            obs_time = _parse_iso_or_epoch(time_el.text) if time_el is not None and time_el.text else None
            name = name_el.text if name_el is not None and name_el.text else f"GPX Point ({lat:.4f}, {lon:.4f})"
            
            obs = GeographicObservation(
                id=f"geo_obs_{uuid.uuid4().hex[:12]}",
                tenant_id=tenant_id,
                case_id=case_id,
                place_name=name,
                location_type="waypoint",
                latitude=lat,
                longitude=lon,
                accuracy_radius_meters=10.0,
                coordinate_source="gpx_track",
                observation_time=obs_time,
                observation_type=LocationObservationType.DIRECTLY_OBSERVED,
                extraction_method="gpx_import",
                source_provider=source_label,
                access_classification="AUTHORIZED_INVESTIGATOR_SUPPLIED",
                metadata={"point_index": idx}
            )
            observations.append(obs)
        except Exception as ex:
            errors.append(f"GPX point {idx}: {ex}")

    return observations, errors

def parse_geo_kml(content: str, tenant_id: str, case_id: Optional[str] = None, source_label: str = "Authorized KML Import") -> Tuple[List[GeographicObservation], List[str]]:
    observations: List[GeographicObservation] = []
    errors: List[str] = []
    try:
        root = ET.fromstring(content)
    except Exception as e:
        return [], [f"Failed to parse KML XML: {e}"]

    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"

    placemarks = root.findall(f".//{ns}Placemark")
    for idx, pm in enumerate(placemarks):
        try:
            coords_el = pm.find(f".//{ns}coordinates")
            if coords_el is None or not coords_el.text:
                continue
            coords_text = coords_el.text.strip().split()[0]
            parts = coords_text.split(",")
            if len(parts) < 2:
                continue
            lon = float(parts[0])
            lat = float(parts[1])
            if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
                errors.append(f"KML Placemark {idx}: Coordinates out of range ({lat}, {lon})")
                continue
            
            name_el = pm.find(f"{ns}name")
            time_el = pm.find(f".//{ns}when") or pm.find(f".//{ns}TimeStamp/{ns}when")
            
            name = name_el.text if name_el is not None and name_el.text else f"KML Placemark ({lat:.4f}, {lon:.4f})"
            obs_time = _parse_iso_or_epoch(time_el.text) if time_el is not None and time_el.text else None
            
            obs = GeographicObservation(
                id=f"geo_obs_{uuid.uuid4().hex[:12]}",
                tenant_id=tenant_id,
                case_id=case_id,
                place_name=name,
                location_type="placemark",
                latitude=lat,
                longitude=lon,
                accuracy_radius_meters=15.0,
                coordinate_source="kml_placemark",
                observation_time=obs_time,
                observation_type=LocationObservationType.DIRECTLY_OBSERVED,
                extraction_method="kml_import",
                source_provider=source_label,
                access_classification="AUTHORIZED_INVESTIGATOR_SUPPLIED",
                metadata={"placemark_index": idx}
            )
            observations.append(obs)
        except Exception as ex:
            errors.append(f"KML Placemark {idx}: {ex}")

    return observations, errors
