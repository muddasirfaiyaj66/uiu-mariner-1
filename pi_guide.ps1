## ========================================
## RASPBERRY PI CONNECTION GUIDE
## ========================================

Write-Host ""
Write-Host "========================================"
Write-Host " Connect to Raspberry Pi - Step by Step"
Write-Host "========================================"
Write-Host ""

Write-Host "Your Pi Info:"
Write-Host "  Hostname: raspberrypi.local"
Write-Host "  Username: pi"
Write-Host "  Password: 1234"
Write-Host ""

## Get PC IP
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notmatch "Loopback" -and $_.IPAddress -notmatch "^169"} | Select-Object -First 1).IPAddress

if ($ipAddress) {
    Write-Host "Your PC IP: $ipAddress" -ForegroundColor Green
} else {
    Write-Host "Run 'ipconfig' to find your PC IP" -ForegroundColor Yellow
    $ipAddress = "YOUR_PC_IP"
}

Write-Host ""
Write-Host "========================================"
Write-Host " STEP 1: SSH to Pi"
Write-Host "========================================"
Write-Host ""
Write-Host "ssh pi@raspberrypi.local"
Write-Host ""

Write-Host "========================================"
Write-Host " STEP 2: On Pi, create directory"
Write-Host "========================================"
Write-Host ""
Write-Host "mkdir -p ~/mariner/pi_scripts"
Write-Host "exit"
Write-Host ""

Write-Host "========================================"
Write-Host " STEP 3: Copy scripts to Pi"
Write-Host "========================================"
Write-Host ""
Write-Host "cd `"E:\UIU MARINER\mariner-software-1.0`""
Write-Host "scp -r pi_scripts\* pi@raspberrypi.local:~/mariner/pi_scripts/"
Write-Host ""

Write-Host "========================================"
Write-Host " STEP 4: SSH back to Pi"
Write-Host "========================================"
Write-Host ""
Write-Host "ssh pi@raspberrypi.local"
Write-Host "cd ~/mariner/pi_scripts"
Write-Host "chmod +x *.sh *.py"
Write-Host ""

Write-Host "========================================"
Write-Host " STEP 5: Start services on Pi"
Write-Host "========================================"
Write-Host ""
Write-Host "./start_all_services.sh $ipAddress"
Write-Host ""

Write-Host "========================================"
Write-Host " STEP 6: Launch app on Windows"
Write-Host "========================================"
Write-Host ""
Write-Host "cd `"E:\UIU MARINER\mariner-software-1.0`""
Write-Host ".\venv\Scripts\Activate.ps1"
Write-Host "python launch_mariner.py"
Write-Host ""

Write-Host "========================================"
Write-Host " All Done!"
Write-Host "========================================"
Write-Host ""
Write-Host "See QUICK_START_PI.md for more help"
Write-Host ""
