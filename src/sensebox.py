"""SenseBox API integration for fetching temperature data."""

import requests
from datetime import datetime, timezone, timedelta
import os

SENSEBOX_IDS = os.getenv(
    "SENSEBOX_IDS",
    "5eba5fbad46fb8001b799786,5c21ff8f919bf8001adf2488,5ade1acf223bd80019a1011c"
).split(",")

def get_temperature_status(temperature):
    """Return status based on temperature value."""
    if temperature is None:
        return None
    if temperature < 10:
        return "Too Cold"
    if temperature > 37:
        return "Too Hot"
    return "Good"

def is_recent(timestamp_str):
    """Check if measurement is not older than 1 hour."""
    if not timestamp_str:
        return False
    measured_at = datetime.fromisoformat(
        timestamp_str.replace("Z", "+00:00")
    )
    now = datetime.now(timezone.utc)
    return now - measured_at <= timedelta(hours=1)

def get_temperature():
    """Fetch average temperature from senseBox sensors."""
    temperatures = []

    for box_id in SENSEBOX_IDS:
        try:
            url = f"https://api.opensensemap.org/boxes/{box_id}"
            response = requests.get(url, timeout=5)
            data = response.json()

            for sensor in data.get("sensors", []):
                if "temperatur" in sensor.get("title", "").lower():
                    measurement = sensor.get("lastMeasurement", {})
                    timestamp = measurement.get("createdAt")
                    value = measurement.get("value")
                    if value and is_recent(timestamp):
                        temperatures.append(float(value))
                    break
        except (requests.RequestException, ValueError, KeyError):
            continue

    if not temperatures:
        return None

    return round(sum(temperatures) / len(temperatures), 2)
