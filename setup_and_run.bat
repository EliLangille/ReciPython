@echo off
echo Setting up ReciPython...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.9 or higher and try again.
    pause
    exit /b
)

:: Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment and install dependencies
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

:: Run the app
echo Starting ReciPython...
python app/main.py
pause