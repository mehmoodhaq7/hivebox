"""HiveBox Flask REST API application."""

from flask import Flask, jsonify, json
from prometheus_flask_exporter import PrometheusMetrics
from config import APP_VERSION
from sensebox import get_temperature
from cache import get_cached_temperature, set_cached_temperature

app = Flask(__name__)
PrometheusMetrics(app)

@app.route("/version")
def version():
    """Return current app version."""
    return jsonify({"version": APP_VERSION})

@app.route("/temperature")
def temperature():
    cached = get_cached_temperature()
    if cached:
        return jsonify(json.loads(cached))

    temp = get_temperature()
    if temp is None:
        return jsonify({"error": "Could not fetch temperature"}), 503

    status = "Too Cold"
    if 10 <= temp <= 36:
        status = "Good"
    elif temp > 36:
        status = "Too Hot"

    result = {"temperature": temp, "status": status}
    set_cached_temperature(json.dumps(result))
    return jsonify(result)

if __name__ == "__main__":
    print(app.url_map)
    app.run(host="0.0.0.0", port=8080)