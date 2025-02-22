import { useState } from 'react';
import './App.css';
import Header from './components/Header';
import InputPanel from './components/InputPanel';
import ComparePanel from './components/ComparePanel';
import AnalysisPanel from './components/AnalysisPanel';
import Footer from './components/Footer';

function App() {
  const [analysisData] = useState(null);

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

  return (
    <div className="app">
      <Header />
      <div className="main-content">
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
      </div>
      <Footer />
    </div>
  );
}

export default App;