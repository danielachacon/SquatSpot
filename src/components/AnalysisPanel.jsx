import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './AnalysisPanel.css';

// Function to analyze squat metrics
async function analyzeSquat(metrics) {
  try {
    const response = await fetch('https://analyzer.e-danielachacon.workers.dev', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(metrics)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const analysis = await response.json();
    return analysis;
  } catch (error) {
    console.error('Error analyzing squat:', error);
    return null;
  }
}

const AnalysisPanel = ({ analysis, repsAnalysis, comparisonScore }) => {
  console.log("Raw analysis data:", analysis); // Debug log
  console.log("Raw reps analysis:", repsAnalysis); // Debug log
  console.log("Comparison score:", comparisonScore); // Debug log
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const analysisData = Array.isArray(analysis) ? analysis[0] : analysis;

  useEffect(() => {
    const getAIAnalysis = async () => {
      if (analysis) {
        const answer = await analyzeSquat({
          type: "overall",
          data: analysis
        }); 
        // Extract the response text from the AI response object
        setAiAnalysis(answer?.response || "No analysis available");
      }
    };

    getAIAnalysis();
  }, [analysis]);

  return (
    <div className="panel analysis-panel">
      <h2>ANALYSIS</h2>
      
      <div className="summary-grid">
        {/* AI Analysis Box - First */}
        {aiAnalysis && (
          <div className="summary-box">
            <h3>AI Form Analysis</h3>
            <div className="ai-content">
              <ReactMarkdown>{aiAnalysis}</ReactMarkdown>
            </div>
          </div>
        )}

        {/* Overall Summary Box - Second */}
        {analysisData && (
          <div className="summary-box">
            <h3>Overall Summary</h3>
            {Object.entries(analysisData || {}).map(([metric, score]) => {
              const numericScore = parseFloat(score);
              return (
                <p key={metric}>
                  <span className="metric-name">{metric}</span>
                  <span className="metric-value">
                    {!isNaN(numericScore) ? numericScore.toFixed(2) : 'N/A'}
                  </span>
                </p>
              );
            })}
          </div>
        )}

        {/* Comparison Score Box */}
        {comparisonScore !== null && comparisonScore !== undefined && (
          <div className="summary-box">
            <h3>Comparison Score</h3>
            <p>{typeof comparisonScore === 'number' ? comparisonScore.toFixed(2) : comparisonScore}</p>
          </div>
        )}
      </div>

      <h3>Rep Details</h3>
      <div className="reps-grid">
        {Array.isArray(repsAnalysis) && repsAnalysis.map((rep, index) => (
          rep && (
            <div key={index} className="rep-data">
              <h4>Rep {index + 1}</h4>
              {Object.entries(rep).map(([metric, value]) => (
                <p key={metric}>
                  <span className="metric-name">{metric}</span>
                  <span className="metric-value">
                    {value !== null ? Number(value).toFixed(2) : 'N/A'}
                  </span>
                </p>
              ))}
            </div>
          )
        ))}
      </div>
    </div>
  );
};

export default AnalysisPanel; 