# ========================================
# CONNECT TO RASPBERRY PI - STEP BY STEP
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🍓 Connect to Raspberry Pi" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Follow these commands step by step."
Write-Host "Copy and paste each command into PowerShell."
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "STEP 1: Connect to Raspberry Pi" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""
Write-Host "Run this command:" -ForegroundColor White
Write-Host "  ssh pi@raspberrypi.local" -ForegroundColor Green
Write-Host ""
Write-Host "When asked for password, type:" -ForegroundColor White
Write-Host "  1234" -ForegroundColor Green
Write-Host ""
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "STEP 2: On Raspberry Pi Terminal" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""
Write-Host "After SSH connects, run these commands:" -ForegroundColor White
Write-Host ""
Write-Host "# Create directory" -ForegroundColor Gray
Write-Host "mkdir -p ~/mariner/pi_scripts" -ForegroundColor Green
Write-Host ""
Write-Host "# Keep this terminal open!" -ForegroundColor Gray
Write-Host ""
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "STEP 3: In NEW PowerShell Window" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""
Write-Host "Open a NEW PowerShell window and run:" -ForegroundColor White
Write-Host ""
Write-Host "cd `"E:\UIU MARINER\mariner-software-1.0`"" -ForegroundColor Green
Write-Host "scp -r pi_scripts\* pi@raspberrypi.local:~/mariner/pi_scripts/" -ForegroundColor Green
Write-Host ""
Write-Host "Password when asked:" -ForegroundColor White
Write-Host "  1234" -ForegroundColor Green
Write-Host ""
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "STEP 4: Back on Raspberry Pi Terminal" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""
Write-Host "After files are copied, run on Pi:" -ForegroundColor White
Write-Host ""
Write-Host "cd ~/mariner/pi_scripts" -ForegroundColor Green
Write-Host "chmod +x *.sh *.py" -ForegroundColor Green
Write-Host ""
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "STEP 5: Get Your PC IP Address" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""
Write-Host "In PowerShell, run:" -ForegroundColor White
Write-Host ""
Write-Host "ipconfig" -ForegroundColor Green
Write-Host ""
Write-Host "Look for 'IPv4 Address' and note it down." -ForegroundColor White
Write-Host "Example: 192.168.1.100" -ForegroundColor Gray
Write-Host ""

Write-Host ""
Write-Host "Finding your PC IP address now..." -ForegroundColor Cyan
Write-Host ""

# Get PC IP automatically
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notmatch "Loopback" -and $_.IPAddress -notmatch "^169"} | Select-Object -First 1).IPAddress

if ($ipAddress) {
    Write-Host "✅ Your PC IP Address: $ipAddress" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "⚠️  Could not auto-detect. Run ipconfig manually." -ForegroundColor Yellow
    Write-Host ""
    $ipAddress = "YOUR_PC_IP"
}

Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "STEP 6: Start Services on Raspberry Pi" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""
Write-Host "On Raspberry Pi terminal, run:" -ForegroundColor White
Write-Host ""
Write-Host "./start_all_services.sh $ipAddress" -ForegroundColor Green
Write-Host ""
Write-Host "Wait for all services to start (✅ messages)" -ForegroundColor Gray
Write-Host ""
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "STEP 7: Launch Application on Windows" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""
Write-Host "In PowerShell, run:" -ForegroundColor White
Write-Host ""
Write-Host "cd `"E:\UIU MARINER\mariner-software-1.0`"" -ForegroundColor Green
Write-Host ".\venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "python launch_mariner.py" -ForegroundColor Green
Write-Host ""
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ Setup Guide Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 Need more help? See:" -ForegroundColor White
Write-Host "   • QUICK_START_PI.md" -ForegroundColor Gray
Write-Host "   • pi_scripts/SETUP_RASPBERRY_PI.md" -ForegroundColor Gray
Write-Host "   • PI_CONNECTION_READY.md" -ForegroundColor Gray
Write-Host ""
