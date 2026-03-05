"""SenseBox API integration for fetching temperature data."""

import requests

SENSEBOX_IDS = [
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c",
]

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
                    value = sensor.get("lastMeasurement", {}).get("value")
                    if value:
                        temperatures.append(float(value))
                    break
        except (requests.RequestException, ValueError, KeyError):
            continue

    if not temperatures:
        return None

    return round(sum(temperatures) / len(temperatures), 2)
