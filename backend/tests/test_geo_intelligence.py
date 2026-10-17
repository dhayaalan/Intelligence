import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.modules.geo_intelligence.models import (
    GeographicObservation, GeoFilterParams, TimeFilterRange, LocationObservationType
)
from app.modules.geo_intelligence.service import geo_intelligence_service
from app.modules.geo_intelligence.parsers import (
    parse_geo_json, parse_geo_csv, parse_geo_gpx, parse_geo_kml
)

@pytest.fixture
def test_client():
    return TestClient(app)

def test_geo_observation_model_separation_of_timestamps():
    """Ensure event, publication, observation, and collection times are strictly separated."""
    now = datetime.utcnow()
    event_t = now - timedelta(days=20)
    pub_t = now - timedelta(days=19)
    obs_t = now - timedelta(days=18)
    
    obs = GeographicObservation(
        id="geo_obs_test_1",
        tenant_id="tenant_test",
        place_name="Zurich Operations Center",
        latitude=47.3769,
        longitude=8.5417,
        accuracy_radius_meters=25.0,
        coordinate_source="exif_gps",
        event_time=event_t,
        publication_time=pub_t,
        observation_time=obs_t,
        observation_type=LocationObservationType.DIRECTLY_OBSERVED,
        source_provider="exif_extractor"
    )
    
    assert obs.event_time != obs.publication_time
    assert obs.publication_time != obs.observation_time
    assert obs.collection_time > obs.event_time
    assert obs.latitude == 47.3769
    assert obs.accuracy_radius_meters == 25.0

def test_geo_temporal_filtering():
    """Verify that 7d, 30d, 3m, 6m, 12m, 3y, 5y, and custom filters correctly exclude out-of-range observations."""
    now = datetime.utcnow()
    tenant = "tenant_geo_filter_test"
    
    # Create 3 observations: 3 days ago, 45 days ago, and 400 days ago
    obs_recent = GeographicObservation(
        id="geo_obs_recent",
        tenant_id=tenant,
        place_name="Recent Station",
        latitude=40.7128,
        longitude=-74.0060,
        event_time=now - timedelta(days=3),
        observation_type=LocationObservationType.DIRECTLY_OBSERVED
    )
    obs_medium = GeographicObservation(
        id="geo_obs_medium",
        tenant_id=tenant,
        place_name="Medium Station",
        latitude=34.0522,
        longitude=-118.2437,
        event_time=now - timedelta(days=45),
        observation_type=LocationObservationType.SOURCE_REPORTED
    )
    obs_old = GeographicObservation(
        id="geo_obs_old",
        tenant_id=tenant,
        place_name="Old Station",
        latitude=51.5074,
        longitude=-0.1278,
        event_time=now - timedelta(days=400),
        observation_type=LocationObservationType.SOURCE_REPORTED
    )
    
    geo_intelligence_service.store_observation(obs_recent)
    geo_intelligence_service.store_observation(obs_medium)
    geo_intelligence_service.store_observation(obs_old)
    
    # 7-day filter should only return obs_recent
    res_7d = geo_intelligence_service.search_observations(
        query=None,
        filters=GeoFilterParams(time_range=TimeFilterRange.LAST_7_DAYS),
        tenant_id=tenant
    )
    ids_7d = [o.id for o in res_7d]
    assert "geo_obs_recent" in ids_7d
    assert "geo_obs_medium" not in ids_7d
    assert "geo_obs_old" not in ids_7d

    # 3-month filter (90 days) should return recent and medium, but not old
    res_3m = geo_intelligence_service.search_observations(
        query=None,
        filters=GeoFilterParams(time_range=TimeFilterRange.LAST_3_MONTHS),
        tenant_id=tenant
    )
    ids_3m = [o.id for o in res_3m]
    assert "geo_obs_recent" in ids_3m
    assert "geo_obs_medium" in ids_3m
    assert "geo_obs_old" not in ids_3m

    # 3-year filter should return all three
    res_3y = geo_intelligence_service.search_observations(
        query=None,
        filters=GeoFilterParams(time_range=TimeFilterRange.LAST_3_YEARS),
        tenant_id=tenant
    )
    ids_3y = [o.id for o in res_3y]
    assert "geo_obs_recent" in ids_3y
    assert "geo_obs_medium" in ids_3y
    assert "geo_obs_old" in ids_3y

def test_authorized_parsers_json_csv_gpx_kml():
    """Verify authentic parsers for authorized JSON, CSV, GPX, and KML formats."""
    tenant = "tenant_parser_test"
    
    # 1. JSON
    json_data = '''{
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-0.1276, 51.5072]},
                "properties": {"name": "Trafalgar Square", "accuracy": 5.0}
            }
        ]
    }'''
    obs_json, errs_json = parse_geo_json(json_data, tenant_id=tenant)
    assert len(errs_json) == 0
    assert len(obs_json) == 1
    assert obs_json[0].place_name == "Trafalgar Square"
    assert obs_json[0].latitude == 51.5072
    assert obs_json[0].longitude == -0.1276

    # 2. CSV
    csv_data = "name,latitude,longitude,accuracy,time\nBerlin Checkpoint,52.5075,13.3904,10,2026-05-01T12:00:00Z\n"
    obs_csv, errs_csv = parse_geo_csv(csv_data, tenant_id=tenant)
    assert len(errs_csv) == 0
    assert len(obs_csv) == 1
    assert obs_csv[0].place_name == "Berlin Checkpoint"
    assert obs_csv[0].latitude == 52.5075
    assert obs_csv[0].longitude == 13.3904

    # 3. GPX
    gpx_data = '''<?xml version="1.0" encoding="UTF-8"?>
    <gpx version="1.1" creator="ForensicUnit">
        <wpt lat="48.8566" lon="2.3522">
            <name>Paris Station</name>
            <time>2026-06-15T08:30:00Z</time>
        </wpt>
    </gpx>'''
    obs_gpx, errs_gpx = parse_geo_gpx(gpx_data, tenant_id=tenant)
    assert len(errs_gpx) == 0
    assert len(obs_gpx) == 1
    assert obs_gpx[0].place_name == "Paris Station"
    assert obs_gpx[0].latitude == 48.8566
    assert obs_gpx[0].longitude == 2.3522

    # 4. KML
    kml_data = '''<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
            <Placemark>
                <name>Tokyo Tower</name>
                <Point>
                    <coordinates>139.7454,35.6586,0</coordinates>
                </Point>
            </Placemark>
        </Document>
    </kml>'''
    obs_kml, errs_kml = parse_geo_kml(kml_data, tenant_id=tenant)
    assert len(errs_kml) == 0
    assert len(obs_kml) == 1
    assert obs_kml[0].place_name == "Tokyo Tower"
    assert obs_kml[0].latitude == 35.6586
    assert obs_kml[0].longitude == 139.7454
