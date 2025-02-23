from flask import Flask, Response, request, send_file, jsonify, session
from flask_cors import CORS
from posetracking import analyze_video_upload, analyze_video
from analysis import calculate_z_scores_to_gold_standard, analyze_all_reps, compare_2_squats
import os
from datetime import datetime
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'spotsquat'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# Create necessary directories
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

@app.route("/upload_video", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file found"}), 400

    file = request.files["video"]
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Create uploads directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"uploaded_video_{timestamp}.mp4"
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        
        print(f"Saving video to: {video_path}")  # Debug print
        file.save(video_path)
        
        output_path, metrics = analyze_video_upload(video_path)
        if output_path:
            # Store metrics directly if it's already a dict
            session['uploaded_metric'] = metrics
            
            # Calculate and store analysis
            z_scores = calculate_z_scores_to_gold_standard(metrics)
            session['analysis_data'] = z_scores
            
            # Calculate and store reps analysis
            reps_analysis = analyze_all_reps(metrics)
            
            # Convert all metrics to list format for frontend
            reps_list = []
            for rep_num, rep_data in metrics.items():
                rep_dict = {k: float(v) if isinstance(v, (np.float32, np.float64)) else v 
                          for k, v in rep_data.items()}
                reps_list.append(rep_dict)
            
            session['analysis_reps_data'] = reps_list
            
            print("Session after upload:", dict(session))
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
        
        output_path, metrics = analyze_video_upload(video_path)
        
        if output_path:
            if 'uploaded_metric' not in session:
                return "No reference video uploaded. Please upload a video first.", 400
                
            # Convert Pandas Series to dictionary or list before storing in session
            metrics_json = metrics.to_dict() if hasattr(metrics, 'to_dict') else metrics
            session['compare_metric'] = metrics_json
            
            # Compare the two sets of metrics
            comparison_score = compare_2_squats(metrics, session['uploaded_metric'])
            # Make sure comparison_score is JSON serializable
            if isinstance(comparison_score, (pd.Series, pd.DataFrame)):
                comparison_score = comparison_score.to_dict()
            
            session['comparison_score'] = comparison_score
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

@app.route("/analyze_video", methods=["POST"])
def analyze_video_to_gold_standard():
    print("Session during analysis:", dict(session))
    if 'analysis_data' not in session:
        print("No analysis_data in session")
        return jsonify({"error": "No analysis data found. Please upload a video first."}), 400
        
    return jsonify(session['analysis_data'])

@app.route("/analyze_reps", methods=["POST"])
def analyze_reps():
    print("Session during Rep analysis:", dict(session))  # Debug log
    if 'analysis_reps_data' not in session:
        print("No analysis_reps_data in session")  # Debug log
        return jsonify({"error": "No analysis reps data found. Please upload a video first."}), 400

    return jsonify(session['analysis_reps_data'])

@app.route("/compare_set", methods=["POST"])
def compare_sets():
    if 'uploaded_metric' not in session:
        return jsonify({"error": "No reference video uploaded yet."}), 400
    if 'compare_metric' not in session:
        return jsonify({"error": "No comparison video uploaded yet."}), 400
    if "comparison_score" not in session:
        return jsonify({"error": "No comparison analysis found."}), 400
    
    return jsonify(session['comparison_score'])

@app.route("/stop_recording", methods=["POST"])
def stop_recording():
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recorded_video_{timestamp}.mp4"
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Process the recorded video
        output_path, metrics = analyze_video_upload(video_path)
        if output_path:
            # Store metrics directly if it's already a dict
            session['uploaded_metric'] = metrics
            
            # Calculate and store analysis
            z_scores = calculate_z_scores_to_gold_standard(metrics)
            session['analysis_data'] = z_scores
            
            # Convert all metrics to list format for frontend
            reps_list = []
            for rep_num, rep_data in metrics.items():
                rep_dict = {k: float(v) if isinstance(v, (np.float32, np.float64)) else v 
                          for k, v in rep_data.items()}
                reps_list.append(rep_dict)
            
            session['analysis_reps_data'] = reps_list
            
            return send_file(output_path, mimetype='video/mp4')
            
        return jsonify({"error": "Failed to process video"}), 500
            
    except Exception as e:
        print(f"Error processing recording: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
    
