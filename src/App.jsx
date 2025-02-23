import { useState } from 'react';
import './App.css';
import Header from './components/Header';
import InputPanel from './components/InputPanel';
import ComparePanel from './components/ComparePanel';
import AnalysisPanel from './components/AnalysisPanel';
import Footer from './components/Footer';

function App() {
  const [analysisData] = useState(null);

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('video', file);

    try {
      const response = await fetch('http://localhost:5000/upload_video', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Upload failed');
      }
      
      console.log('Upload successful');
    } catch (error) {
      console.error('Error uploading video:', error);
    }
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
          />
          <ComparePanel
            onCompare={handleCompare}
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