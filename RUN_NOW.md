# 🚀 Quick Start Guide - Expo Go with USB Debugging

## Your Setup is Ready!

### ✅ Configuration Complete:
- **Your IP Address**: `192.168.31.205`
- **Mobile App**: Configured with correct IP
- **Server Port**: `5000`

## Step 1: Start Backend Server

### Option A: Use the Batch File (Easiest)
Double-click: **`START_SERVER.bat`**

### Option B: Manual Start
Open PowerShell/Terminal and run:
```bash
cd backend
python server.py
```

**Wait for this message:**
```
✓ Model loaded and warmed up successfully
Starting server on 0.0.0.0:5000...
```

⏳ **First time?** The YOLO model will download (~140MB) - this takes 1-2 minutes.

## Step 2: Test Server (Optional)

Open a new terminal and test:
```bash
curl http://localhost:5000/
```

Or open in browser: `http://localhost:5000/`

You should see JSON with server status.

## Step 3: Setup USB Debugging (For Expo Go)

### On Your Android Phone:

1. **Enable Developer Options:**
   - Settings → About Phone
   - Tap "Build Number" **7 times**
   - You'll see "You are now a developer!"

2. **Enable USB Debugging:**
   - Settings → Developer Options
   - Toggle **"USB Debugging"** ON

3. **Connect Phone via USB** to your computer

4. **Allow USB Debugging** when prompted on phone (tap "Allow")

### On Your Computer:

Run this command in PowerShell:
```bash
adb reverse tcp:5000 tcp:5000
```

This forwards your phone's port 5000 to your computer's port 5000.

**Note:** If `adb` is not found, you need Android Platform Tools:
- Download from: https://developer.android.com/studio/releases/platform-tools
- Or install Android Studio (includes ADB)

## Step 4: Update Mobile App for USB Debugging

Since you're using USB debugging, update the API URL to use `localhost`:

Edit `mobile/app/camera.js` line 10:
```javascript
const API_URL = 'http://localhost:5000'; // For USB debugging
```

Or keep it as `http://192.168.31.205:5000` if using WiFi.

## Step 5: Start Mobile App

### Option A: Use the Batch File
Double-click: **`START_MOBILE.bat`**

### Option B: Manual Start
```bash
cd mobile
npm start
```

### Option C: If npm start doesn't work
```bash
cd mobile
npx expo start
```

## Step 6: Connect with Expo Go

### Method 1: USB Connection (Recommended)
1. Open **Expo Go** app on your phone
2. In the terminal where Expo is running, press **`a`** (lowercase)
3. App will open on your connected Android device

### Method 2: QR Code (WiFi)
1. Open **Expo Go** app
2. Scan the QR code shown in terminal
3. Make sure phone and computer are on same WiFi

## Step 7: Test the App

1. **Grant camera permission** when prompted
2. **Check top status bar** - should show "SYSTEM ONLINE"
3. **Point camera** at an animal (or animal image)
4. **Tap scan button** for manual detection
5. **Toggle AUTO switch** for real-time detection

## Troubleshooting

### ❌ "Can't connect to server"

**Check 1: Is server running?**
```bash
curl http://localhost:5000/
```

**Check 2: Firewall blocking?**
- Windows Firewall might block port 5000
- Temporarily disable or allow Python through firewall

**Check 3: For USB debugging:**
```bash
adb reverse tcp:5000 tcp:5000
```

**Check 4: For WiFi:**
- Ensure phone and computer on same network
- Test: Open `http://192.168.31.205:5000/` in phone browser

### ❌ "ADB not found"

Install Android Platform Tools:
1. Download: https://developer.android.com/studio/releases/platform-tools
2. Extract to a folder (e.g., `C:\platform-tools`)
3. Add to PATH or use full path:
   ```bash
   C:\platform-tools\adb.exe reverse tcp:5000 tcp:5000
   ```

### ❌ Expo Go won't connect

1. **Clear cache:**
   ```bash
   cd mobile
   npx expo start -c
   ```

2. **Check Expo Go app version** (update if needed)

3. **Try QR code instead** of USB connection

### ❌ Model loading slow

- First run downloads YOLOv8 model (~140MB)
- Be patient, it only downloads once
- Check internet connection

## Quick Commands Reference

```bash
# Start server
cd backend && python server.py

# Test server
curl http://localhost:5000/

# Setup USB port forwarding
adb reverse tcp:5000 tcp:5000

# Start mobile app
cd mobile && npm start

# In Expo terminal:
# Press 'a' for Android device
# Press 'i' for iOS simulator
```

## Current Status

✅ Backend configured  
✅ Mobile app IP updated: `192.168.31.205:5000`  
✅ Ready for USB debugging  

## Next Steps

1. ⚡ Start backend server (wait for model to load)
2. 📱 Setup USB debugging on phone
3. 🔄 Run `adb reverse tcp:5000 tcp:5000`
4. 🚀 Start Expo: `cd mobile && npm start`
5. 📸 Open app in Expo Go and start scanning!

---

**Need help?** Check `SETUP_EXPO.md` for detailed troubleshooting.

