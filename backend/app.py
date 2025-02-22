from flask import Flask
from flask_socketio import SocketIO
from pose import process_frame  # Import function from pose.py

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on("message")
def handle_frame(frame_data):
    """Receives a frame, processes it, and sends it back to the frontend."""
    processed_frame = process_frame(frame_data)
    socketio.emit("processed_frame", processed_frame)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)