# ========================================
# Quick Start Pi Services
# ========================================

$PI_HOST = "raspberrypi.local"
$PC_IP = "192.168.0.104"  # Your Windows PC IP from diagnostics

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "STARTING PI SERVICES" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pi Address: $PI_HOST (192.168.0.102)" -ForegroundColor Green
Write-Host "PC Address: $PC_IP" -ForegroundColor Green
Write-Host ""
Write-Host "This will SSH to Pi and start all ROV services" -ForegroundColor Yellow
Write-Host "You may need to enter Pi password (usually: raspberry)" -ForegroundColor Yellow
Write-Host ""

# SSH command to run on Pi
$command = "cd ~/mariner/pi_scripts && ./start_all_services.sh $PC_IP"

Write-Host "Running: $command" -ForegroundColor Cyan
Write-Host ""

# Execute via SSH
ssh pi@$PI_HOST $command

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services should now be starting on Pi..." -ForegroundColor Yellow
Write-Host "Wait 5-10 seconds, then run diagnostics again:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  .\diagnose_pi_connection.ps1" -ForegroundColor White
Write-Host ""
Write-Host "If all ports show [OK], you can start the app:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  python launch_mariner.py" -ForegroundColor White
Write-Host ""
