# UIU MARINER ROV Control Launcher
# Windows PowerShell script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  UIU MARINER - ROV Control System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    & .\venv\Scripts\Activate.ps1
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "Launching ROV Control Application..." -ForegroundColor Green
Write-Host ""

# Launch application
python src\ui\rovControlApp.py

Write-Host ""
Write-Host "Application closed." -ForegroundColor Yellow
