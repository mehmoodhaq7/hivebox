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
    with patch("app.get_temperature", return_value=22.5):
        response = client.get("/temperature")
        assert response.status_code == 200
        data = response.get_json()
        assert "average_temperature" in data
        assert data["unit"] == "celsius"
        assert data["status"] == "Good"
        
def test_temperature_status_too_cold(client):
    with patch("app.get_temperature", return_value=5.0):
        response = client.get("/temperature")
        assert response.status_code == 200
        assert response.get_json()["status"] == "Too Cold"

def test_temperature_status_too_hot(client):
    with patch("app.get_temperature", return_value=40.0):
        response = client.get("/temperature")
        assert response.status_code == 200
        assert response.get_json()["status"] == "Too Hot"

def test_temperature_endpoint_no_data(client):
    with patch("app.get_temperature", return_value=None):
        response = client.get("/temperature")
        assert response.status_code == 503