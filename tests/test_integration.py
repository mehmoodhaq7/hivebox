"""Integration tests for HiveBox Flask application."""

import pytest
import sys
sys.path.insert(0, "src")

from app import app

@pytest.fixture
def client():
    """Create test client with real app."""
    app.testing = True
    return app.test_client()

def test_version_endpoint_returns_version(client):
    """Test /version returns correct version format."""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.get_json()
    assert "version" in data
    assert data["version"] == "0.0.1"

def test_metrics_endpoint_accessible(client):
    """Test /metrics endpoint is accessible and returns prometheus format."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"flask_http_request_total" in response.data

def test_temperature_endpoint_returns_valid_structure(client):
    """Test /temperature returns valid response structure."""
    response = client.get("/temperature")
    assert response.status_code in [200, 503]
    data = response.get_json()
    assert data is not None

    if response.status_code == 200:
        assert "average_temperature" in data
        assert "unit" in data
        assert "status" in data
        assert data["unit"] == "celsius"
        assert data["status"] in ["Too Cold", "Good", "Too Hot"]

def test_temperature_status_valid_values(client):
    """Test /temperature status field has valid value."""
    response = client.get("/temperature")
    if response.status_code == 200:
        data = response.get_json()
        assert data["status"] in ["Too Cold", "Good", "Too Hot"]