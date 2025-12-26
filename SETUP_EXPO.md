# Expo Go Setup Guide - USB Debugging

## Quick Setup for USB Debugging

### Your Configuration:
- **Server IP**: `192.168.31.205`
- **Port**: `5000`
- **API URL**: `http://192.168.31.205:5000`

## Step 1: Start Backend Server

The server should already be running. To verify:
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

## Step 2: Configure Mobile App

The mobile app is already configured with your IP address (`192.168.31.205:5000`).

If you need to change it later, edit `mobile/app/camera.js`:
```javascript
const API_URL = 'http://YOUR_IP:5000';
```

## Step 3: Start Expo

```bash
cd mobile
npm start
```

## Step 4: Connect with Expo Go

### Option A: USB Debugging (Recommended)

1. **Enable USB Debugging** on your Android phone:
   - Settings → About Phone → Tap "Build Number" 7 times
   - Settings → Developer Options → Enable "USB Debugging"

2. **Connect phone via USB** to your computer

3. **Run adb command** (if needed):
   ```bash
   adb reverse tcp:5000 tcp:5000
   ```
   This forwards your phone's port 5000 to your computer's port 5000.

4. **Update API URL** to use localhost:
   ```javascript
   const API_URL = 'http://localhost:5000';
   ```

5. **Start Expo**:
   ```bash
   cd mobile
   npm start
   ```

6. **Press 'a'** in the Expo terminal to open on Android device

### Option B: Same WiFi Network

1. Ensure phone and computer are on **same WiFi network**

2. Use your computer's IP: `http://192.168.31.205:5000`

3. **Start Expo**:
   ```bash
   cd mobile
   npm start
   ```

4. **Scan QR code** with Expo Go app

## Troubleshooting

### Can't connect to server?

1. **Check server is running**:
   ```bash
   curl http://localhost:5000/
   ```

2. **Check firewall**:
   - Windows Firewall might block port 5000
   - Allow Python through firewall or disable temporarily

3. **Verify IP address**:
   ```bash
   ipconfig
   ```
   Look for IPv4 address and update `API_URL` if different

4. **Test connection from phone browser**:
   - Open `http://192.168.31.205:5000/` on your phone
   - Should show server status JSON

### USB Debugging Issues?

1. **Install ADB** (Android Debug Bridge):
   - Download Android Platform Tools
   - Or install via Android Studio

2. **Verify connection**:
   ```bash
   adb devices
   ```
   Should show your device

3. **Port forwarding**:
   ```bash
   adb reverse tcp:5000 tcp:5000
   ```

### Expo Go Issues?

1. **Clear Expo cache**:
   ```bash
   cd mobile
   npx expo start -c
   ```

2. **Check Expo Go app version**:
   - Update to latest version from Play Store

3. **Restart Metro bundler**:
   - Stop Expo (Ctrl+C)
   - Run `npm start` again

## Testing

### Test Backend:
```bash
cd backend
python test_server.py
```

### Test Mobile Connection:
1. Open Expo Go app
2. Navigate to camera screen
3. Check if "SYSTEM ONLINE" appears in top bar
4. Try scanning an image

## Current Configuration

- ✅ Backend: Running on `192.168.31.205:5000`
- ✅ Mobile App: Configured for `192.168.31.205:5000`
- ✅ Endpoints: `/predict` and `/stream` ready

---

**Ready to go!** Start the mobile app and begin scanning! 🚀

