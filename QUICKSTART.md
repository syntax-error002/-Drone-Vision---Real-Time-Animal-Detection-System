# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Node.js 16+ and npm (for mobile app)
- Camera-enabled device (for testing)

## Step 1: Backend Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start the Server

```bash
cd backend
python server.py
```

You should see:
```
Loading Model (Large)...
✓ Model loaded and warmed up successfully
Starting server on 0.0.0.0:5000...
```

**Note**: The YOLOv8 model will be automatically downloaded on first run (~140MB).

## Step 2: Configure Mobile App

### Update API URL

Edit `mobile/app/camera.js` and update the API_URL:

```javascript
const API_URL = 'http://YOUR_SERVER_IP:5000';
```

To find your server IP:
- **Windows**: Run `ipconfig` and look for IPv4 address
- **Linux/Mac**: Run `ifconfig` or `ip addr`

### Install Mobile Dependencies

```bash
cd mobile
npm install
```

### Start Mobile App

```bash
npm start
```

Scan the QR code with Expo Go app on your phone, or press `a` for Android emulator, `i` for iOS simulator.

## Step 3: Test the System

### Option 1: Test Script (Backend)

```bash
cd backend
python test_server.py
```

### Option 2: Manual Testing

1. Open the mobile app
2. Grant camera permissions
3. Point camera at animals (or images of animals)
4. Tap scan button for manual mode
5. Toggle AUTO switch for real-time detection

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/
```

### Single Image Prediction
```bash
curl -X POST -F "file=@test_image.jpg" http://localhost:5000/predict
```

### Performance Metrics
```bash
curl http://localhost:5000/metrics
```

## Troubleshooting

### Server won't start
- Check if port 5000 is available: `netstat -an | grep 5000`
- Ensure all dependencies are installed: `pip list`

### Mobile app can't connect
- Verify server IP address is correct
- Ensure phone and server are on same network
- Check firewall isn't blocking port 5000
- Try disabling Windows Firewall temporarily for testing

### Slow performance
- Reduce image quality in camera.js (quality parameter)
- Increase frame_skip_rate in server.py REAL_TIME_CONFIG
- Use smaller YOLO model (yolov8n.pt instead of yolov8l.pt)

### Model download issues
- Download manually from: https://github.com/ultralytics/assets/releases
- Place in `backend/` directory

## Performance Optimization

For best real-time performance:

1. **Reduce Image Size**: Set `scale: 0.6` in camera.js
2. **Increase Frame Skip**: Set `frame_skip_rate: 3` in server.py
3. **Lower Quality**: Set `quality: 0.5` in camera.js
4. **Use Smaller Model**: Change to `yolov8n.pt` for 3x faster inference

## Configuration

### Backend Configuration

Edit `REAL_TIME_CONFIG` in `backend/server.py`:

```python
REAL_TIME_CONFIG = {
    'frame_skip_rate': 2,        # Lower = more frames processed
    'target_fps': 15,             # Target performance
    'conf_threshold': 0.25,       # Detection confidence
    'max_frame_size': (1280, 720), # Max resolution
}
```

### Mobile Configuration

Edit capture settings in `mobile/app/camera.js`:

```javascript
const photo = await cameraRef.current.takePictureAsync({
    quality: 0.6,      // 0.0 - 1.0 (lower = faster)
    scale: 0.8,        // 0.0 - 1.0 (lower = faster)
});
```

## Next Steps

- Read `README.md` for full documentation
- Check `RESEARCH_METHODOLOGY.md` for research details
- Review `backend/test_server.py` for testing examples
- Monitor performance via `/metrics` endpoint

## Support

For issues or questions:
1. Check logs in `drone_vision.log`
2. Review error messages in console
3. Test endpoints with `test_server.py`
4. Check network connectivity

---

**Happy Detecting! 🦓🐘🦒**

