from flask import Flask, jsonify

APP_VERSION = "0.0.1"

app = Flask(__name__)

def get_version():
    """Returns the current version of the HiveBox app."""
    return APP_VERSION

@app.route("/version")
def version():
    return jsonify({"version": get_version()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
