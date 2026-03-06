"""HiveBox Flask REST API application."""

from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from config import APP_VERSION
from sensebox import get_temperature, get_temperature_status

app = Flask(__name__)
PrometheusMetrics(app)

@app.route("/version")
def version():
    """Return current app version."""
    return jsonify({"version": APP_VERSION})

@app.route("/temperature")
def temperature():
    """Return average temperature from senseBox sensors."""
    avg_temp = get_temperature()
    if avg_temp is None:
        return jsonify({"error": "No temperature data available"}), 503
    return jsonify({"average_temperature": avg_temp, "unit": "celsius","status": get_temperature_status(avg_temp)})

if __name__ == "__main__":
    print(app.url_map)
    app.run(host="0.0.0.0", port=8080)