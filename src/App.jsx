import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import InputPanel from './components/InputPanel';
import ComparePanel from './components/ComparePanel';
import AnalysisPanel from './components/AnalysisPanel';
import Footer from './components/Footer';

function App() {
  const [analysisData] = useState(null);
  const [isComparing, setIsComparing] = useState(false);

  const handleUpload = () => {
    // Implement file upload logic
    console.log('Upload clicked');
  };

  const handleRecord = () => {
    // Implement recording logic
    console.log('Record clicked');
  };

  const handleCompare = () => {
    // Implement recording logic
    console.log('Compare clicked');
  };

  const handleTitleClick = () => {
    window.location.reload();
  };

  const handleCompareStateChange = (comparing) => {
    setIsComparing(comparing);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="logo-container">
          <img src="/barbell-icon.png" alt="SquatSpot Logo" className="barbell-logo" />
          <h1 className="title" onClick={handleTitleClick} style={{ cursor: 'pointer' }}>
            SQUATSPOT
          </h1>
        </div>
      </header>
      
      <main className="main-content">
        <div className="content-wrapper">
          <InputPanel 
            onUpload={handleUpload}
            onRecord={handleRecord}
            isComparing={isComparing}
          />
          <ComparePanel
            onCompare={handleCompare}
            onCompareStateChange={handleCompareStateChange}
          />
        </div>
        <div className="bottom-row">
          <AnalysisPanel 
            analysisData={analysisData}
          />
        </div>
      </main>
    </div>
  );
}

export default App;