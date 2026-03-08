"""HiveBox Flask REST API application."""

from flask import Flask, jsonify, json
from prometheus_flask_exporter import PrometheusMetrics
from config import APP_VERSION
from sensebox import get_temperature
from cache import get_cached_temperature, set_cached_temperature
from storage import store_temperature
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

def scheduled_store():
    """Background job: store temperature every 5 minutes."""
    temp = get_temperature()
    if temp is None:
        return
    status = "Too Cold"
    if 10 <= temp <= 36:
        status = "Good"
    elif temp > 36:
        status = "Too Hot"
    data = {"temperature": temp, "status": status}
    store_temperature(data)


scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_store, "interval", minutes=5)
scheduler.start()

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

@app.route("/store")
def store():
    """Manually trigger temperature data storage."""
    temp = get_temperature()
    if temp is None:
        return jsonify({"error": "Could not fetch temperature"}), 503

    status = "Too Cold"
    if 10 <= temp <= 36:
        status = "Good"
    elif temp > 36:
        status = "Too Hot"

    data = {"temperature": temp, "status": status}
    key = store_temperature(data)
    if key is None:
        return jsonify({"error": "Storage failed"}), 503

    return jsonify({"stored": True, "key": key})

if __name__ == "__main__":
    print(app.url_map)
    app.run(host="0.0.0.0", port=8080)