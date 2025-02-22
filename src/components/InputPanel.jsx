import React, { useState, useRef } from "react";

const InputPanel = ({ onRecord }) => {
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);
  const fileInputRef = useRef(null);

  // Toggle Camera
  const handleCameraToggle = () => {
    setIsCameraActive((prev) => !prev);
    setVideoUrl(null); // Clear uploaded video when switching to camera

    if (!isCameraActive) {
      onRecord(); // Start webcam processing
    }
  };

  // Trigger File Upload
  const handleUploadClick = () => {
    setIsCameraActive(false); // Ensure webcam is off when uploading
    fileInputRef.current.click();
  };

  // Handle File Upload
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("video", file);

    try {
      const response = await fetch("http://localhost:5000/upload_video", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        setVideoUrl("http://localhost:5000/processed_video"); // New route for uploaded videos
      } else {
        alert("Error uploading video");
      }
    } catch (error) {
      console.error("Upload error:", error);
      alert("Upload failed!");
    }
  };

  return (
    <div className="panel input-panel">
      {/* Action Buttons */}
      <div className="button-row large-buttons">
        <button className="compare-button" onClick={handleCameraToggle}>
          {isCameraActive ? "Stop Camera" : "Start Camera"}
        </button>

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept="video/mp4,video/quicktime,video/x-msvideo"
          style={{ display: "none" }}
        />
        <button className="compare-button" onClick={handleUploadClick}>
          Upload Video
        </button>
      </div>

      {/* Display Webcam Stream */}
      {isCameraActive && (
        <div className="webcam-container">
          <img
            src="http://localhost:5000/video_feed"
            alt="Webcam Feed with Pose Tracking"
            className="webcam-feed"
          />
        </div>
      )}

      {/* Display Processed Uploaded Video */}
      {!isCameraActive && videoUrl && (
        <div className="video-container">
          <img src={videoUrl} alt="Processed Video" className="webcam-feed" />
        </div>
      )}
    </div>
  );
};

export default InputPanel;
