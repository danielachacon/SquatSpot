from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import os

app = Flask(__name__, static_folder="static")
socketio = SocketIO(app, cors_allowed_origins="*")

# Serve React App
@app.route("/")
def serve_react():
    return send_from_directory("static", "index.html")

@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
