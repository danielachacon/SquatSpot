import React, { useState, useRef } from 'react';

const ComparePanel = ({ onCompareStateChange }) => {
  const [videoFile, setVideoFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        const formData = new FormData();
        formData.append('video', file);

        // Change the URL to post to /compare_video
        const response = await fetch('http://localhost:5000/compare_video', {
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
        setVideoFile(videoUrl); 
        onCompareStateChange(true); // Notify parent component to update state
      } catch (error) {
        console.error('Error uploading video:', error);
        alert('Failed to upload video');
      }
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
          className="compare-button"
          onClick={() => fileInputRef.current.click()}
        >
          Compare
        </button>
      </div>

      {videoFile && (
        <div className="video-container">
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