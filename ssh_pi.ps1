#!/usr/bin/env pwsh
# ========================================
# Quick SSH to Raspberry Pi
# ========================================

param(
    [string]$Command = ""
)

$PI_HOST = "raspberrypi.local"
$PI_USER = "pi"

Write-Host "🔌 Connecting to Raspberry Pi..." -ForegroundColor Cyan
Write-Host ""

if ($Command -eq "") {
    # Interactive SSH
    Write-Host "Opening SSH session..." -ForegroundColor Yellow
    Write-Host "💡 Default password is usually: raspberry" -ForegroundColor Yellow
    Write-Host ""
    
    ssh "$PI_USER@$PI_HOST"
} else {
    # Execute command
    Write-Host "Executing: $Command" -ForegroundColor Yellow
    Write-Host ""
    
    ssh "$PI_USER@$PI_HOST" "$Command"
}
