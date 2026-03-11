@echo off
SETLOCAL EnableDelayedExpansion

TITLE RepoPilot Launcher

echo ==========================================
echo           🚀 Launching RepoPilot
echo ==========================================

:: Check for conda
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Conda was not found in your PATH.
    echo Please ensure Anaconda or Miniconda is installed.
    pause
    exit /b
)

echo [1/3] Activating conda environment 'repopilot'...
:: We use 'call' to ensure the batch script continues after conda activation
call conda activate repopilot

echo [2/3] Starting FastAPI Backend in a new window...
start "RepoPilot Backend" cmd /k "call conda activate repopilot && python -m backend.app"

echo [WAIT] Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo [3/3] Starting Streamlit Frontend in a new window...
start "RepoPilot Frontend" cmd /k "call conda activate repopilot && streamlit run frontend/streamlit_app.py"

echo ==========================================
echo           ✅ RepoPilot is running!
echo ==========================================
echo Backend is at: http://localhost:8000
echo Frontend is at: http://localhost:8501 (usually)
echo.
echo You can close this window. Backend and Frontend will keep running in their own windows.
pause
