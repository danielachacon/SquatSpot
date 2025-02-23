import React, { useState, useRef } from "react";

const InputPanel = ({ onUpload, onRecord, isComparing }) => {
  const [showWebcam, setShowWebcam] = useState(false);
  const [uploadedVideo, setUploadedVideo] = useState(null);
  const fileInputRef = useRef(null);

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

        const response = await fetch('http://localhost:5000/upload_video', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Upload failed');
        }

        // Create a blob URL from the response
        const videoBlob = await response.blob();
        const videoUrl = URL.createObjectURL(videoBlob);
        
        // Set the uploaded video path from the blob URL
        setUploadedVideo(videoUrl); 

        // Optionally hide the webcam if it was shown
        setShowWebcam(false);
      } catch (error) {
        console.error('Error uploading video:', error);
        alert('Failed to upload video');
      }
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
            src="http://localhost:5000/video_feed"
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
