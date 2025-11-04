@echo off
echo Starting TDR Agent Web Application...
echo.
echo Installing Python dependencies...
pip install -r requirements.txt
echo.
echo Starting Flask server...
echo Open your browser and navigate to: http://127.0.0.1:5000
echo.
echo Note: If you encounter socket errors, the app will run on localhost only.
echo.
python app.py
if %errorlevel% neq 0 (
    echo.
    echo Error occurred. Please check the error message above.
    echo Common solutions:
    echo 1. Make sure port 5000 is not in use by another application
    echo 2. Try running: netstat -ano ^| findstr :5000
    echo 3. If port is in use, kill the process or change the port in app.py
)
pause
