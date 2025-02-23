# SquatSpot 🏋️‍♂️ - Your AI-Powered Squat Analysis Assistant

SquatSpot revolutionizes squat form analysis by providing real-time feedback and detailed metrics through advanced computer vision and AI technology.

## 🏆 Hacklytics 2025 Winner - Best AI Application Built with Cloudflare

## 🛠️ What It Does
SquatSpot offers comprehensive squat analysis through:

✅ **Real-time Form Analysis** 
- Upload or record squats for instant feedback
- Get immediate form corrections
- Track multiple reps in a single set

✅ **Detailed Metrics Tracking**
- Squat depth measurement
- Spine angle tracking
- Knee balance assessment
- Lateral movement detection
- Hip position analysis
- Bottom position hold time

✅ **Comparative Analysis**
- Compare your form against reference squats
- Get a similarity score
- Identify specific areas for improvement

✅ **AI-Powered Feedback**
- Personalized recommendations
- Rep-by-rep breakdown
- Overall set analysis

## ⚙️ How We Built It
SquatSpot combines multiple AI-powered components:
- **Computer Vision Engine** – MediaPipe and OpenCV process real-time video feeds for precise pose estimation
- **Metrics Analysis System** – Custom algorithms calculate key performance indicators
- **AI Feedback Generator** – Processes metrics through specialized LLMs for personalized recommendations
- **Real-time Processing** – Optimized for minimal latency in live analysis

## 💻 Tech Stack
- **Frontend**: React.js
- **Backend**: Python (Flask)
- **Computer Vision**: MediaPipe, OpenCV
- **AI Analysis**: CloudFlare Workers AI, LLaMa 3
- **Data Processing**: NumPy, Pandas

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

bash
cd backend
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt

### Frontend Setup

bash
cd frontend
npm install
npm run dev

### Usage
1. **Upload Video**
   - Click "Upload" to analyze a pre-recorded squat video
   - Supported formats: MP4, MOV, AVI

2. **Record Live**
   - Click "Record" to use your webcam for real-time analysis
   - Position yourself so your full body is visible

3. **Compare Form**
   - Upload a reference video using the "Compare" button
   - View side-by-side analysis and comparison scores

## 🤝 Contributing
Help make SquatSpot better! Here's how:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📜 License
This project is licensed under the MIT License – see the LICENSE file for details.

---
**Note**: SquatSpot is designed for educational purposes and should not replace professional coaching or medical advice.
