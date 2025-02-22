import React, { useState, useRef } from 'react';

const ComparePanel = ({ onCompare }) => {
  const [videoFile, setVideoFile] = useState(null);
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    const validTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo'];

    if (file && validTypes.includes(file.type)) {
      setVideoFile(URL.createObjectURL(file));
      onCompare(file); // Pass the file to parent component if needed
    } else {
      alert('Please upload a valid video file (MP4, MOV, or AVI)');
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleVideoEnd = () => {
    if (videoRef.current) {
      videoRef.current.play(); // Replay when video ends
    }
  };

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
          className="action-button"
          onClick={handleUploadClick}
        >
          Compare
        </button>
      </div>

      {videoFile && (
        <div className="video-container">
          <video 
            ref={videoRef}
            src={videoFile}
            controls
            autoPlay
            loop
            muted
            playsInline
            className="uploaded-video"
            onEnded={handleVideoEnd}
          >
            Your browser does not support the video tag.
          </video>
        </div>
      )}
    </div>
  );
};

export default ComparePanel;