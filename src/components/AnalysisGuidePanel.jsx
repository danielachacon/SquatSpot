import React from 'react';
import './AnalysisGuidePanel.css';

const AnalysisGuidePanel = () => {
  console.log('AnalysisGuidePanel is rendering');
  
  return (
    <div className="panel analysis-guide-panel">
      <h2>ANALYSIS GUIDE</h2>
      
      <div className="guide-grid">
        <div className="guide-box">
          <h3>Depth Guide</h3>
          <div className="guide-content">
            <p>
              <span className="guide-metric">Below 90 Degrees:</span>
              <span className="guide-value">Ideal squat depth</span>
            </p>
            <p>
              <span className="guide-metric">90-120 Degrees:</span>
              <span className="guide-value">Acceptable range</span>
            </p>
            <p>
              <span className="guide-metric">Above 120 Degrees:</span>
              <span className="guide-value">Need to squat deeper</span>
            </p>
          </div>
        </div>

        <div className="guide-box">
          <h3>Balance Guide</h3>
          <div className="guide-content">
            <p>
              <span className="guide-metric">Knee Imbalance {'>'} 15:</span>
              <span className="guide-value">Weight shifted left</span>
            </p>
            <p>
              <span className="guide-metric">Knee Imbalance {'<'} -15:</span>
              <span className="guide-value">Weight shifted right</span>
            </p>
            <p>
              <span className="guide-metric">Lateral Shift {'>'} |2|:</span>
              <span className="guide-value">Excessive side lean</span>
            </p>
          </div>
        </div>

        <div className="guide-box">
          <h3>Form Guide</h3>
          <div className="guide-content">
            <p>
              <span className="guide-metric">Hips Below Knees = 1:</span>
              <span className="guide-value">Good depth achieved</span>
            </p>
            <p>
              <span className="guide-metric">Bottom Position:</span>
              <span className="guide-value">Hold 1-2 seconds</span>
            </p>
            <p>
              <span className="guide-metric">Min Spine Angle {'>'} |0.7|:</span>
              <span className="guide-value">Excessive forward lean</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisGuidePanel; 