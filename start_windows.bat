@echo off
title TDR Agent - Natural Language API Query Interface
color 0A

echo.
echo ========================================
echo    TDR Agent Web Application
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.

REM Check if port 5000 is available
netstat -ano | findstr :5000 >nul 2>&1
if %errorlevel% equ 0 (
    echo WARNING: Port 5000 is already in use!
    echo.
    echo Processes using port 5000:
    netstat -ano | findstr :5000
    echo.
    echo You can:
    echo 1. Kill the process using the PID above
    echo 2. Change the port in app.py
    echo 3. Continue anyway (might fail)
    echo.
    set /p choice="Continue anyway? (y/n): "
    if /i "%choice%" neq "y" (
        echo Exiting...
        pause
        exit /b 1
    )
)

echo.
echo Starting Flask server...
echo ========================================
echo   Server will be available at:
echo   http://127.0.0.1:5000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

echo.
echo Server stopped.
pause
