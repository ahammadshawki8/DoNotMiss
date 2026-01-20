@echo off
REM DoNotMiss Backend - Local Development Script (Windows)

echo Starting DoNotMiss Backend (Local Development)
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo Please edit .env with your database URL
)

REM Run the application
echo.
echo Starting Flask server on http://localhost:5000
echo ==================================================
echo.
python app.py
