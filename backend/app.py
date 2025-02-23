from flask import Flask, Response, request, send_file, jsonify, session
from flask_cors import CORS
from posetracking import analyze_video_upload, analyze_video
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.secret_key = 'spotsquat' 

currentUploadedMetric= None
currentCompareMetric = None

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# Create necessary directories
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

@app.route("/upload_video", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return "No video file found", 400

    file = request.files["video"]
    if file.filename == '':
        return "No selected file", 400

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"uploaded_video_{timestamp}.mp4"
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(video_path)
        
        output_path, session['uploaded_metric'] = analyze_video_upload(video_path)
        if output_path:
            # Log the metrics to the console
            print("Metrics:", session['uploaded_metric'])  # Log metrics here
            
            # Return the processed video file directly
            return send_file(output_path, mimetype='video/mp4')
        return "Failed to process video", 500
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error processing video: {str(e)}", 500

@app.route("/compare_video", methods=["POST"])
def compare_upload_video():
    if "video" not in request.files:
        return "No video file found", 400

    file = request.files["video"]
    if file.filename == '':
        return "No selected file", 400

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"uploaded_video_{timestamp}.mp4"
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(video_path)
        
        output_path, session['compare_metric'] = analyze_video_upload(video_path)
        if output_path:
            # Log the metrics to the console
            print("Metrics:", session['compare_metric'])  # Log metrics here
            
            # Return the processed video file directly
            return send_file(output_path, mimetype='video/mp4')
        return "Failed to process video", 500
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error processing video: {str(e)}", 500


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
