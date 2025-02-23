import React, { useState, useRef, useEffect } from 'react';

const ComparePanel = ({ onCompareStateChange, analysis, setAnalysis, setComparisonScore }) => {
  const [videoFile, setVideoFile] = useState(null);
  const fileInputRef = useRef(null);

  // Cleanup function for video URL
  useEffect(() => {
    return () => {
      if (videoFile) {
        URL.revokeObjectURL(videoFile);
      }
    };
  }, [videoFile]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        // Cleanup previous video URL if it exists
        if (videoFile) {
          URL.revokeObjectURL(videoFile);
        }

        const formData = new FormData();
        formData.append('video', file);

        const compareResponse = await fetch('http://localhost:8000/compare_video', {
          method: 'POST',
          body: formData,
          credentials: 'include',
        });

        if (!compareResponse.ok) {
          const errorText = await compareResponse.text();
          throw new Error(`Compare failed: ${errorText || compareResponse.statusText}`);
        }

        // Clone the response before reading it as blob
        const responseClone = compareResponse.clone();
        const videoBlob = await responseClone.blob();
        const videoUrl = URL.createObjectURL(videoBlob);
        setVideoFile(videoUrl);

        const compareSetResponse = await fetch('http://localhost:8000/compare_set', {
          method: 'POST',
          credentials: 'include',
        });

        if (!compareSetResponse.ok) {
          throw new Error(`Compare set failed: ${compareSetResponse.statusText}`);
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