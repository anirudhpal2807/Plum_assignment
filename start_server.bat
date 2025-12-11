@echo off
REM Start Medical Report Simplifier - Windows Batch Script
REM This script starts the FastAPI server and opens the frontend

echo.
echo ======================================
echo   Medical Report Simplifier - Startup
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if pip packages are installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install requirements
        pause
        exit /b 1
    )
)

echo Starting FastAPI server on http://localhost:8000...
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python -m uvicorn app.main:app --reload --port 8000

pause
