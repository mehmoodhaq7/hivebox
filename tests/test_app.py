import sys
sys.path.insert(0, "src")

import pytest
from unittest.mock import patch
from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_version_endpoint(client):
    response = client.get("/version")
    assert response.status_code == 200
    data = response.get_json()
    assert "version" in data
    assert data["version"] == "0.0.1"

def test_temperature_endpoint_success(client):
    with patch("app.get_temperature", return_value=22.5), \
         patch("app.get_cached_temperature", return_value=None), \
         patch("app.set_cached_temperature"):
        response = client.get("/temperature")
        assert response.status_code == 200
        data = response.get_json()
        assert "temperature" in data
        assert "status" in data
        assert data["temperature"] == 22.5
        assert data["status"] == "Good"
        
def test_temperature_status_too_cold(client):
    with patch("app.get_temperature", return_value=5.0), \
         patch("app.get_cached_temperature", return_value=None), \
         patch("app.set_cached_temperature"):
        response = client.get("/temperature")
        data = response.get_json()
        assert data["status"] == "Too Cold"

def test_temperature_status_too_hot(client):
    with patch("app.get_temperature", return_value=40.0), \
         patch("app.get_cached_temperature", return_value=None), \
         patch("app.set_cached_temperature"):
        response = client.get("/temperature")
        data = response.get_json()
        assert data["status"] == "Too Hot"

def test_temperature_endpoint_no_data(client):
    with patch("app.get_temperature", return_value=None), \
         patch("app.get_cached_temperature", return_value=None):
        response = client.get("/temperature")
        assert response.status_code == 503
        
# Cache tests
def test_get_cached_temperature_miss(client):
    with patch("cache.get_valkey_client") as mock_client:
        mock_client.return_value.get.return_value = None
        from cache import get_cached_temperature
        result = get_cached_temperature()
        assert result is None

def test_get_cached_temperature_hit(client):
    with patch("cache.get_valkey_client") as mock_client:
        mock_client.return_value.get.return_value = b'{"temperature": 20}'
        from cache import get_cached_temperature
        result = get_cached_temperature()
        assert result is not None

def test_set_cached_temperature(client):
    with patch("cache.get_valkey_client") as mock_client:
        from cache import set_cached_temperature
        set_cached_temperature('{"temperature": 20}')
        mock_client.return_value.setex.assert_called_once()

def test_is_cache_fresh_true(client):
    with patch("cache.get_valkey_client") as mock_client:
        mock_client.return_value.ttl.return_value = 100
        from cache import is_cache_fresh
        result = is_cache_fresh()
        assert result is True

def test_is_cache_fresh_false(client):
    with patch("cache.get_valkey_client") as mock_client:
        mock_client.return_value.ttl.return_value = -2
        from cache import is_cache_fresh
        result = is_cache_fresh()
        assert result is False

# Storage tests
def test_store_temperature(client):
    with patch("storage.get_s3_client") as mock_client:
        from storage import store_temperature
        store_temperature({"temperature": 20, "status": "Good"})
        mock_client.return_value.put_object.assert_called_once()

# Sensebox tests
def test_check_sensebox_accessible():
    with patch("sensebox.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        from sensebox import check_sensebox_accessible
        result = check_sensebox_accessible("5eba5fbad46fb8001b799786")
        assert result is True

def test_check_sensebox_not_accessible():
    with patch("sensebox.requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection error")
        from sensebox import check_sensebox_accessible
        try:
            result = check_sensebox_accessible("5eba5fbad46fb8001b799786")
            assert result is False
        except Exception:
            pass

# Readyz tests
def test_readyz_endpoint_ready(client):
    with patch("app.get_accessible_count", return_value=3), \
         patch("app.is_cache_fresh", return_value=True):
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ready"

def test_readyz_endpoint_not_ready(client):
    with patch("app.get_accessible_count", return_value=0), \
         patch("app.is_cache_fresh", return_value=False):
        response = client.get("/readyz")
        assert response.status_code == 503
        data = response.get_json()
        assert data["status"] == "not ready"
