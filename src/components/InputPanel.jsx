import React, { useState, useRef } from "react";

const InputPanel = ({ onUpload, onRecord, isComparing, analysis, setAnalysis, repsAnalysis, setRepsAnalysis }) => {
  const [showWebcam, setShowWebcam] = useState(false);
  const [uploadedVideo, setUploadedVideo] = useState(null);
  const fileInputRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);

  const handleRecordClick = () => {
    setShowWebcam(!showWebcam);
    if (!showWebcam) {
      onRecord();
      // Clear any existing uploaded video when starting recording
      setUploadedVideo(null);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        const formData = new FormData();
        formData.append('video', file);

        // First upload and process the video
        const uploadResponse = await fetch('http://localhost:8000/upload_video', {
          method: 'POST',
          body: formData,
          credentials: 'include',
        });

        if (!uploadResponse.ok) {
          throw new Error('Upload failed');
        }

        // Create a blob URL from the video response
        const videoBlob = await uploadResponse.blob();
        const videoUrl = URL.createObjectURL(videoBlob);
        setUploadedVideo(videoUrl);

        // Hide webcam if it was shown
        setShowWebcam(false);

        // Then get the analysis
        const analysisResponse = await fetch('http://localhost:8000/analyze_video', {
          method: 'POST',
          credentials: 'include',
        });

        if (!analysisResponse.ok) {
          throw new Error('Analysis failed');
        }

        const analysisData = await analysisResponse.json();
        setAnalysis(analysisData);

        // Then get the reps analysis
        const repsAnalysisResponse = await fetch('http://localhost:8000/analyze_reps', {
          method: 'POST',
          credentials: 'include',
        });

        if (!repsAnalysisResponse.ok) {
          throw new Error('Reps analysis failed');
        }

        const repsAnalysisData = await repsAnalysisResponse.json();
        setRepsAnalysis(repsAnalysisData);

      } catch (error) {
        console.error('Error uploading video:', error);
        alert(error.message || 'Failed to upload video');
      }
    }
  };

  const handleStopRecording = async () => {
    setIsRecording(false);
    try {
      // Your existing code for stopping recording...

      // Get the metrics from your backend
      const repsAnalysisResponse = await fetch('http://localhost:8000/analyze_reps', {
        method: 'POST',
        credentials: 'include',
      });

      if (!repsAnalysisResponse.ok) {
        throw new Error('Reps analysis failed');
      }

      const repsData = await repsAnalysisResponse.json();
      setRepsAnalysis(repsData);

      // Now analyze the metrics with Llama
      const aiResponse = await analyzeSquat(repsData);
      setAiAnalysis(aiResponse);

    } catch (error) {
      console.error('Error processing recording:', error);
    }
  };

  // Fixed size style for comparison mode
  const containerStyle = isComparing ? {
    height: '480px',
    width: '100%',
    transition: 'height 0.3s ease'
  } : {
    height: '70vh',
    width: '100%'
  };

  return (
    <div className="panel input-panel">
      <div className="button-row large-buttons">
        <button className="compare-button" onClick={handleRecordClick}>
          {showWebcam ? "Stop" : "Record"}
        </button>

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept="video/mp4,video/quicktime,video/x-msvideo"
          style={{ display: "none" }}
        />
        <button className="compare-button" onClick={() => fileInputRef.current.click()}>
          Upload
        </button>
      </div>

      {showWebcam && (
        <div className="webcam-container" style={containerStyle}>
          <img
            src="http://localhost:8000/video_feed"
            alt="Webcam Feed with Pose Tracking"
            className="webcam-feed"
            style={{ 
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              borderRadius: '8px'  // Keeping the rounded corners
            }}
          />
        </div>
      )}

      {uploadedVideo && !showWebcam && (
        <div className="video-container" style={containerStyle}>
          <video
            src={uploadedVideo}
            controls
            autoPlay
            className="uploaded-video"
            style={{ 
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              borderRadius: '8px'
            }}
          />
        </div>
      )}
    </div>
  );
};

export default InputPanel;
