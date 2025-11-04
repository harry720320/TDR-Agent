@echo off
echo Updating OpenAI library to latest version...
pip install --upgrade openai>=1.12.0
echo.
echo OpenAI library updated successfully!
echo.
echo Please restart the Flask server to use the new OpenAI API.
echo.
pause
