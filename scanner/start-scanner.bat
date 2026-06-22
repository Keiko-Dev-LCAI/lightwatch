@echo off
:: ── LightView Scanner Service Launcher ──────────────────────────────────────
:: Double-click this file to start the scanner service on port 8189.
:: The service must be running before you click "Scan Ticket" in LightView.
::
:: Requirements (run once to install):
::   pip install pillow flask flask-cors
::
:: To stop the service: close this window.
:: ─────────────────────────────────────────────────────────────────────────────

title LightView Scanner Service (port 8189)

echo.
echo  ============================================================
echo   LightView Scanner Service
echo   HP ENVY 5660 series -- port 8189
echo  ============================================================
echo.
echo  Keep this window open while using "Scan Ticket" in LightView.
echo  Close this window to stop the scanner service.
echo.

:: Check Pillow is installed; install if missing
python -c "import PIL" 2>nul
if errorlevel 1 (
    echo  [Setup] Installing required packages...
    pip install pillow flask flask-cors
    echo.
)

:: Start the service
python "%USERPROFILE%\Desktop\scanner_service.py"

echo.
echo  Scanner service stopped.
pause
