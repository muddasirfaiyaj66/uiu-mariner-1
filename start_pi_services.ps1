## ========================================
## START RASPBERRY PI SERVICES
## ========================================

Write-Host ""
Write-Host "============================================"
Write-Host " RASPBERRY PI - Start Services"
Write-Host "============================================"
Write-Host ""

# Get PC IP
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notmatch "Loopback" -and $_.IPAddress -notmatch "^169"} | Select-Object -First 1).IPAddress

Write-Host "Your PC IP Address: " -NoNewline
Write-Host "$ipAddress" -ForegroundColor Green
Write-Host ""

Write-Host "============================================"
Write-Host " Step 1: Connect to Pi via SSH"
Write-Host "============================================"
Write-Host ""
Write-Host "Run this command in your terminal:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ssh pi@raspberrypi.local" -ForegroundColor Yellow
Write-Host ""
Write-Host "Password: " -NoNewline
Write-Host "1234" -ForegroundColor Green
Write-Host ""
Write-Host ""

Write-Host "============================================"
Write-Host " Step 2: Start All Services"
Write-Host "============================================"
Write-Host ""
Write-Host "After SSH connects, run these commands:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  cd ~/mariner/pi_scripts" -ForegroundColor Yellow
Write-Host "  ./start_all_services.sh $ipAddress" -ForegroundColor Yellow
Write-Host ""
Write-Host ""

Write-Host "============================================"
Write-Host " Step 3: Verify Services Started"
Write-Host "============================================"
Write-Host ""
Write-Host "You should see:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  [OK] Sensor server started" -ForegroundColor Green
Write-Host "  [OK] MAVProxy started" -ForegroundColor Green
Write-Host "  [OK] Camera 0 started" -ForegroundColor Green
Write-Host "  [OK] Camera 1 started" -ForegroundColor Green
Write-Host ""
Write-Host ""

Write-Host "============================================"
Write-Host " Step 4: Launch Application"
Write-Host "============================================"
Write-Host ""
Write-Host "Back on Windows, run:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  python launch_mariner.py" -ForegroundColor Yellow
Write-Host ""
Write-Host ""

Write-Host "============================================"
Write-Host " Troubleshooting Commands"
Write-Host "============================================"
Write-Host ""
Write-Host "View running services on Pi:" -ForegroundColor Cyan
Write-Host "  screen -ls" -ForegroundColor Yellow
Write-Host ""
Write-Host "View sensor logs:" -ForegroundColor Cyan
Write-Host "  screen -r sensors" -ForegroundColor Yellow
Write-Host "  (Press Ctrl+A then D to detach)" -ForegroundColor Gray
Write-Host ""
Write-Host "Stop all services:" -ForegroundColor Cyan
Write-Host "  ./stop_all_services.sh" -ForegroundColor Yellow
Write-Host ""
Write-Host ""

Write-Host "============================================"
Write-Host " Need to copy scripts first?"
Write-Host "============================================"
Write-Host ""
Write-Host "If you haven't copied scripts to Pi yet:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. SSH to Pi and create directory:" -ForegroundColor White
Write-Host "   mkdir -p ~/mariner/pi_scripts" -ForegroundColor Yellow
Write-Host "   exit" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Copy from Windows:" -ForegroundColor White
Write-Host "   cd `"E:\UIU MARINER\mariner-software-1.0`"" -ForegroundColor Yellow
Write-Host "   scp -r pi_scripts\* pi@raspberrypi.local:~/mariner/pi_scripts/" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Make executable:" -ForegroundColor White
Write-Host "   ssh pi@raspberrypi.local" -ForegroundColor Yellow
Write-Host "   chmod +x ~/mariner/pi_scripts/*.sh ~/mariner/pi_scripts/*.py" -ForegroundColor Yellow
Write-Host ""
Write-Host ""

Write-Host "============================================"
Write-Host " Ready to Start!"
Write-Host "============================================"
Write-Host ""
Write-Host "See CONTROLLER_AND_PI_STATUS.md for details"
Write-Host ""
