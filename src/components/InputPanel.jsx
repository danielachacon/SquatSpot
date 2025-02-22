import React, { useState, useRef } from 'react';
import WebcamComponent from './webcam';

const InputPanel = ({ onUpload, onRecord, onCompare }) => {
  const [showWebcam, setShowWebcam] = useState(false);
  const [videoFile, setVideoFile] = useState(null);
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  const handleRecordClick = () => {
    if (showWebcam) {
        setShowWebcam(false);
      } else {
        setShowWebcam(true);
        setVideoFile(null);
        onRecord();
      }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    const validTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo'];
    
    if (file && validTypes.includes(file.type)) {
      setVideoFile(URL.createObjectURL(file));
      setShowWebcam(false);
      onUpload(file);
    } else {
      alert('Please upload a valid video file (MP4, MOV, or AVI)');
    }
  };

  const handleUploadClick = () => {
    setShowWebcam(false);
    fileInputRef.current.click();
  };

  const handleVideoEnd = () => {
    if (videoRef.current) {
      videoRef.current.play();
    }
  };

  return (
    <div className="panel input-panel">
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
          Upload
        </button>
        <button 
          className="action-button"
          onClick={handleRecordClick}
        >
          {showWebcam ? 'Stop' : 'Record'}
        </button>
      </div>
      
      {showWebcam ? (
        <div className="webcam-container">
          <WebcamComponent />
        </div>
      ) : videoFile ? (
        <div className="video-container">
          <video 
            ref={videoRef}
            src={videoFile}
            controls
            autoPlay        // Add autoplay
            loop            // Add loop
            muted          // Required for autoplay in most browsers
            playsInline    // Better mobile support
            className="uploaded-video"
            onEnded={handleVideoEnd}  // Handle video end
          >
            Your browser does not support the video tag.
          </video>
        </div>
      ) : null}
    </div>
  );
};

export default InputPanel; 