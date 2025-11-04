@echo off
REM UIU MARINER - Setup Script for Windows (Command Prompt)
REM Creates virtual environment and installs all dependencies

echo ============================================================
echo UIU MARINER - Virtual Environment Setup
echo ============================================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Found: %PYTHON_VERSION%
echo.

REM Check if venv exists
if exist venv (
    echo [WARNING] Virtual environment already exists!
    set /p RECREATE="Delete and recreate? (y/n): "
    if /i "%RECREATE%"=="y" (
        echo Removing old virtual environment...
        rmdir /s /q venv
        echo [OK] Removed
    ) else (
        echo Using existing virtual environment
        echo.
        echo To activate it manually, run:
        echo   venv\Scripts\activate.bat
        pause
        exit /b 0
    )
)

echo.
echo Creating virtual environment...
python -m venv venv

if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    echo Try: python -m pip install --upgrade pip
    pause
    exit /b 1
)

echo [OK] Virtual environment created: venv\
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded
echo.

REM Install dependencies
echo Installing dependencies from requirements.txt...
echo This may take a few minutes...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Some dependencies failed to install
    echo Check the error messages above
    pause
) else (
    echo.
    echo [OK] All dependencies installed successfully!
)

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Virtual environment is now active
echo.
echo Next steps:
echo   1. Configure your ROV settings in config.json
echo   2. Connect your Xbox/Switch controller
echo   3. Run the application:
echo.
echo      python src\ui\marinerApp.py
echo.
echo      OR use the launcher:
echo.
echo      python launch_mariner.py
echo.
echo To activate virtual environment later:
echo   venv\Scripts\activate.bat
echo.
echo To deactivate:
echo   deactivate
echo.
echo ============================================================
echo.
pause
