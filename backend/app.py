from flask import Flask, Response, request
from posetracking import analyze_video  # Import function from posetracking
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # Ensure folder exists

video_path = None  # Store path of the latest uploaded video

@app.route("/upload_video", methods=["POST"])
def upload_video():
    """Handles video uploads and saves them to the server."""
    global video_path

    if "video" not in request.files:
        return "No video file found", 400

    file = request.files["video"]
    video_path = os.path.join(UPLOAD_FOLDER, "uploaded_video.mp4")
    file.save(video_path)

    return "Video uploaded successfully", 200

@app.route("/video_feed")
def video_feed():
    """Streams webcam feed with pose tracking."""
    return Response(analyze_video(0), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/processed_video")
def processed_video():
    """Streams the uploaded video with pose tracking."""
    global video_path
    if video_path and os.path.exists(video_path):
        return Response(analyze_video(video_path), mimetype="multipart/x-mixed-replace; boundary=frame")
    else:
        return "No video uploaded yet", 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
