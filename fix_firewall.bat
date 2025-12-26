@echo off
echo Requesting Admin Privileges...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Opening Port 5000 for TCP...
    netsh advfirewall firewall add rule name="Allow Flask 5000" dir=in action=allow protocol=TCP localport=5000
    echo.
    echo SUCCESS! Port 5000 is now open.
    echo You can now scan from your phone.
) else (
    echo FAILURE: You must Right-Click this file and select "Run as Administrator"
)
pause
