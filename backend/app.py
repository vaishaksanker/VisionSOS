import os

from flask import (
    Flask,
    jsonify,
    send_file,
    send_from_directory
)

from database.database import init_db, get_events
from backend.system_state import read_state


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)

LIVE_FRAME_PATH = os.path.join(
    BASE_DIR,
    "events",
    "live_frame.jpg"
)


app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)


# Initialize database
init_db()


@app.route("/")
def home():
    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


@app.route("/api/status")
def status():
    return jsonify(read_state())


@app.route("/api/events")
def events():
    return jsonify(get_events())


@app.route("/api/frame")
def frame():

    if not os.path.exists(LIVE_FRAME_PATH):
        return jsonify({
            "error": "Camera frame not available"
        }), 404

    return send_file(
        LIVE_FRAME_PATH,
        mimetype="image/jpeg",
        max_age=0
    )


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "system": "VisionSOS"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )