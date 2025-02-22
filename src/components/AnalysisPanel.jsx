import React from 'react';

const AnalysisPanel = ({ analysisData }) => {
  return (
    <div className="panel analysis-panel">
      <h2>ANALYSIS</h2>
      {analysisData ? (
        <div className="analysis-content">
          {/* Add your analysis content here */}
        </div>
      ) : (
        <div className="empty-state">
            <p></p>
        </div>
      )}
    </div>
  );
};

export default AnalysisPanel; 