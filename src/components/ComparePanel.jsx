import React, { useState, useRef } from 'react';

const ComparePanel = ({ onCompareStateChange, analysis, setAnalysis, setComparisonScore }) => {
  const [videoFile, setVideoFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        const formData = new FormData();
        formData.append('video', file);

        // First API call for video comparison
        const compareResponse = await fetch('http://localhost:8000/compare_video', {
          method: 'POST',
          body: formData,
          credentials: 'include',
        });

        if (!compareResponse.ok) {
          // Try to parse error message from JSON response
          const errorText = await compareResponse.text();
          throw new Error(errorText || 'Failed to compare videos');
        }

        // Clone the response before reading it as blob
        const responseClone = compareResponse.clone();
        
        // Check content type of response
        const contentType = compareResponse.headers.get('content-type');
        if (!contentType || !contentType.includes('video/mp4')) {
          const errorText = await responseClone.text();
          throw new Error(errorText || 'Invalid response format from server');
        }

        const videoBlob = await compareResponse.blob();
        const videoUrl = URL.createObjectURL(videoBlob);
        setVideoFile(videoUrl);

        // Call the compare_set API
        const compareSetResponse = await fetch('http://localhost:8000/compare_set', {
          method: 'POST',
          credentials: 'include',
        });

        if (!compareSetResponse.ok) {
          const errorData = await compareSetResponse.json();
          throw new Error(errorData.error || 'Failed to get comparison results');
        }

        const comparisonScore = await compareSetResponse.json();
        setComparisonScore(comparisonScore);
      } catch (error) {
        console.error('Error processing video:', error);
        alert(error.message || 'Failed to process video');
        // Clean up if there was an error
        if (videoFile) {
          URL.revokeObjectURL(videoFile);
          setVideoFile(null);
        }
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