@echo off
echo ==========================================
echo      Drone Vision Network Fixer 🛠️
echo ==========================================
echo.
echo This script attempts to open Port 5000 for the Backend.
echo Please run this file as Administrator if it fails.
echo.

echo [1/3] Adding Firewall Rule for Python Flask (Port 5000)...
netsh advfirewall firewall add rule name="DroneVision_Flask_5000" dir=in action=allow protocol=TCP localport=5000 profile=any
if %errorlevel% neq 0 (
    echo    X Failed. (Run as Admin!)
) else (
    echo    V Success! Port 5000 is Open.
)

echo.
echo [2/3] Checking Local IP Address...
ipconfig | findstr "IPv4"
echo.

echo [3/3] Checking Connectivity...
curl -I http://localhost:5000
echo.

echo ==========================================
echo Done. If the App still fails, continue using the Tunnel.
echo ==========================================
pause
