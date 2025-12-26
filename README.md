# 🦅 Drone Vision - Real-Time Animal Detection System

A high-performance mobile application and backend system designed for real-time object detection and tracking using drone camera feeds. This project integrates state-of-the-art computer vision with a cinematic, sci-fi inspired mobile interface.

![Drone Vision HUD](mobile/assets/icon.png)

## ✨ Features

- **Real-Time Detection**: Powered by **YOLOv8 (Large)** for high-accuracy animal detection and classification.
- **Cinematic HUD**: A "Jarvis-like" sci-fi user interface with dynamic data streams, holographic overlays, and tactical controls.
- **Dynamic Tracking**: Real-time Animated Bounding Boxes that intelligently scale and track targets across the screen.
- **Adaptive Performance**: Automatic frame skipping and resolution adjustment to maintain different target FPS rates.
- **Dual Modes**:
  - **Manual Scan**: High-precision single-shot analysis with detailed biological data.
  - **Auto-Pilot**: Continuous real-time scanning and tracking.
- **Smart Feedback**: Haptic feedback and Text-to-Speech audio alerts ("Target Confirmed").

## 🛠 Tech Stack

### Mobile App (Frontend)
- **Framework**: React Native (Expo)
- **Camera**: `expo-camera` with custom aspect-fill scaling logic.
- **UI/FX**: `react-native-reanimated`, customized `StyleSheet`, and vector icons.
- **Communication**: Multipart form data streaming over HTTP.

### Backend (AI Server)
- **Language**: Python 3.12+
- **Core AI**: Ultralytics YOLOv8
- **Image Processing**: OpenCV (cv2) & PIL
- **Server**: Flask with concurrent threading support.

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js & npm
- Android Device (with USB Debugging enabled)

### 1. Backend Setup
```bash
cd backend
pip install flask flask-cors opencv-python ultralytics pillow numpy
python server.py
```
> The server runs on port `5000`. Ensure you have the YOLO weights (`yolov8l.pt`) in the backend directory.

### 2. Mobile App Setup
```bash
cd mobile
npm install
npx expo start --android
```

### 3. Connection (USB Debugging)
For the most stable real-time performance, we use **ADB Reverse Tethering**:
```bash
# Map the phone's localhost:5000 to your computer's port 5000
adb reverse tcp:5000 tcp:5000
```
*Note: The app is configured to connect to `http://127.0.0.1:5000` by default when running in this mode.*

## 📐 Architecture

1.  **Capture**: Mobile app captures frames (downscaled for speed).
2.  **Transport**: Frames are sent via HTTP POST to the Flask server.
3.  **Inference**:
    - Server preprocesses image (CLAHE enhancement, Thermal simulation).
    - YOLOv8 performs inference.
4.  **Response**: Server returns JSON (Label, Confidence, BBox [x,y,w,h], Biological Facts).
5.  **Visualization**:
    - Mobile app calculates "Scale & Offset" to map the image bbox to the screen coordinates.
    - An animated overlay renders on top of the camera feed.

## ⚠️ Troubleshooting

- **"Aborted" / Connection Failed**:
  - Ensure `adb reverse` command was run.
  - Check if `python server.py` is active.
- **Box Not Aligned**:
  - The app uses "Aspect Fill". Ensure your device isn't forcing a strange aspect ratio. Shake device -> "Reload" to recalibrate.
