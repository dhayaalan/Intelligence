import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_shodan_discover_unconfigured(analyst_headers):
    """Verify Shodan discover returns clean CONFIG_REQUIRED state when API key is missing."""
    with patch.dict("os.environ", {"SHODAN_API_KEY": ""}):
        resp = client.get(
            "/api/v1/camera-evidence/shodan/discover?jurisdiction=IN",
            headers=analyst_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["configured"] is False
        assert data["api_key_status"] == "CONFIG_REQUIRED"
        assert "SHODAN_API_KEY is not configured" in data["message"]
        assert len(data["cameras"]) == 0


def test_shodan_discover_configured_mock(analyst_headers):
    """Verify Shodan discover parses camera responses properly when configured."""
    fake_shodan_resp = {
        "total": 1,
        "matches": [
            {
                "ip_str": "122.161.45.10",
                "port": 554,
                "product": "Hikvision IP Camera",
                "org": "Bharti Airtel Ltd",
                "location": {
                    "city": "Chennai",
                    "country_name": "India",
                    "latitude": 13.0827,
                    "longitude": 80.2707
                },
                "opts": {
                    "screenshot": "dGVzdA=="
                },
                "timestamp": "2026-10-22T06:00:00"
            }
        ]
    }

    with patch.dict("os.environ", {"SHODAN_API_KEY": "shodan_test_key"}):
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = fake_shodan_resp
            mock_get.return_value = mock_resp

            resp = client.get(
                "/api/v1/camera-evidence/shodan/discover?jurisdiction=IN&city=Chennai",
                headers=analyst_headers
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["configured"] is True
            assert data["api_key_status"] == "ACTIVE"
            assert data["total_found"] == 1
            assert len(data["cameras"]) == 1
            cam = data["cameras"][0]
            assert cam["ip"] == "122.161.45.10"
            assert cam["port"] == 554
            assert cam["city"] == "Chennai"
            assert cam["country"] == "India"
            assert cam["stream_url"] == "rtsp://122.161.45.10:554/"
            assert cam["screenshot_url"] == "data:image/jpeg;base64,dGVzdA=="
