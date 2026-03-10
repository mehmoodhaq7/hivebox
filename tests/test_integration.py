"""Integration tests for HiveBox Flask application."""

import pytest
import sys
import json
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
        assert "temperature" in data
        assert "status" in data

def test_temperature_status_valid_values(client):
    """Test /temperature status field has valid value."""
    response = client.get("/temperature")
    if response.status_code == 200:
        data = response.get_json()
        assert data["status"] in ["Too Cold", "Good", "Too Hot"]

def test_readyz_endpoint_returns_valid_structure(client):
    """Test /readyz returns valid response structure."""
    response = client.get("/readyz")
    assert response.status_code in [200, 503]
    data = response.get_json()
    assert data is not None
    assert "status" in data
    assert data["status"] in ["ready", "not ready"]

def test_cache_integration():
    """Test real Valkey cache set and get."""
    from cache import get_valkey_client, set_cached_temperature, get_cached_temperature, is_cache_fresh
    
    client = get_valkey_client()
    assert client.ping() is True

    test_data = json.dumps({"temperature": 22.5, "status": "Good"})
    set_cached_temperature(test_data)

    cached = get_cached_temperature()
    assert cached is not None
    data = json.loads(cached)
    assert data["temperature"] == 22.5
    assert data["status"] == "Good"

    assert is_cache_fresh() is True

def test_storage_integration():
    """Test real MinIO storage."""
    from storage import get_s3_client, store_temperature

    s3 = get_s3_client()
    buckets = s3.list_buckets()
    bucket_names = [b["Name"] for b in buckets["Buckets"]]
    assert "hivebox-data" in bucket_names

    key = store_temperature({"temperature": 22.5, "status": "Good"})
    assert key is not None
    assert key.startswith("temperature/")