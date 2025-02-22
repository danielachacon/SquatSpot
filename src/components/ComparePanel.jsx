import React, { useState, useRef } from 'react';

const ComparePanel = ({ onCompare, onCompareStateChange }) => {
  const [videoFile, setVideoFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    const validTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo'];

    if (file && validTypes.includes(file.type)) {
      setVideoFile(URL.createObjectURL(file));
      onCompare?.(file);
      onCompareStateChange(true); // Notify parent that comparison started
    } else {
      alert('Please upload a valid video file (MP4, MOV, or AVI)');
    }
  };

  const handleButtonClick = () => {
    if (videoFile) {
      // Stop/clear the video
      setVideoFile(null);
      onCompareStateChange(false); // Notify parent that comparison stopped
    } else {
      // Upload new video
      fileInputRef.current.click();
    }
  };

  const containerStyle = videoFile ? {
    height: '480px',
    width: '100%',
    transition: 'height 0.3s ease'
  } : {};

  return (
    <div className="panel compare-panel">
      <div className="button-row">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept="video/mp4,video/quicktime,video/x-msvideo"
          style={{ display: 'none' }}
        />
        <button 
          className="compare-button"
          onClick={handleButtonClick}
        >
          {videoFile ? "Stop" : "Compare"}
        </button>
      </div>

      {videoFile && (
        <div className="video-container" style={containerStyle}>
          <video 
            src={videoFile}
            controls
            autoPlay
            loop
            muted
            playsInline
            className="uploaded-video"
            style={{ height: '100%', objectFit: 'contain' }}
          />
        </div>
      )}
    </div>
  );
};

export default ComparePanel;