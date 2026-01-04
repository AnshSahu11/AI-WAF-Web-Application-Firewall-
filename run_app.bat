@echo off
TITLE Hybrid ML-WAF Launcher

echo ===================================================
echo      SWAVLAMBAN 2025 - ML-WAF MODULE LAUNCHER
echo ===================================================

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)

:: 2. Install Dependencies
echo [INFO] Checking dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b
)

:: 3. Start Backend (in a new window)
echo [INFO] Starting FastAPI Backend on Port 8000...
start "ML-WAF Backend" cmd /k "uvicorn api.app:app --port 8000 --reload"

:: Wait for API to boot
echo [INFO] Waiting 5 seconds for API to initialize...
timeout /t 5 /nobreak >nul

:: 4. Start Frontend
echo [INFO] Launching Streamlit Dashboard...
streamlit run UI/waf_gui.py

pause
