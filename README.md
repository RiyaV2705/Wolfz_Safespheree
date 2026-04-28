 SafeSphere

This is an AI-powered crowd monitoring system built using computer vision. It detects, tracks, and analyzes people in real time to identify overcrowding situations and provide live visual insights.It works offline also .

 
 Getting Started

First, install the required dependencies:

pip install ultralytics opencv-python streamlit numpy

Run the Application:

streamlit run streamlit_app.py

 Usage:

* Choose input source:

  * Webcam (real-time monitoring)
  * Upload Video (MP4/AVI)

* Click Start Monitoring

The system will:

* Detect people in the frame
* Count number of individuals
* Track unique people
* Display heatmap of movement
* Show alerts when crowd exceeds threshold


