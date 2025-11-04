# ========================================
# Pi Connection Diagnostic Tool
# ========================================

$PI_HOST = "raspberrypi.local"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "PI CONNECTION DIAGNOSTIC" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Ping Raspberry Pi
Write-Host "1. Testing network connectivity..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName $PI_HOST -Count 2 -Quiet -ErrorAction SilentlyContinue
if ($ping) {
    Write-Host "   [OK] Pi is reachable on network" -ForegroundColor Green
    $ipAddress = (Test-Connection -ComputerName $PI_HOST -Count 1).IPV4Address.IPAddressToString
    Write-Host "   IP Address: $ipAddress" -ForegroundColor Green
}
else {
    Write-Host "   [FAIL] Cannot reach Pi at $PI_HOST" -ForegroundColor Red
    Write-Host "   Check:" -ForegroundColor Yellow
    Write-Host "      - Pi is powered on" -ForegroundColor Yellow
    Write-Host "      - Pi is connected to same network" -ForegroundColor Yellow
    Write-Host "      - mDNS is enabled (Bonjour service)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Check if we can SSH
Write-Host "2. Testing SSH access..." -ForegroundColor Yellow
$sshTest = Test-NetConnection -ComputerName $PI_HOST -Port 22 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($sshTest) {
    Write-Host "   [OK] SSH port is open (22)" -ForegroundColor Green
}
else {
    Write-Host "   [WARN] SSH port not responding" -ForegroundColor Yellow
}

Write-Host ""

# Test 3: Check ROV service ports
Write-Host "3. Testing ROV service ports..." -ForegroundColor Yellow

$allRunning = $true
foreach ($port in @(5000, 5001, 7000)) {
    $portName = switch ($port) {
        5000 { "Sensors/Cam0" }
        5001 { "Camera 1" }
        7000 { "MAVProxy" }
    }
    
    $test = Test-NetConnection -ComputerName $PI_HOST -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($test) {
        Write-Host "   [OK] Port $port open ($portName)" -ForegroundColor Green
    }
    else {
        Write-Host "   [FAIL] Port $port closed ($portName)" -ForegroundColor Red
        $allRunning = $false
    }
}

Write-Host ""

# Test 4: Try to get sensor data
Write-Host "4. Testing sensor data connection..." -ForegroundColor Yellow
try {
    $client = New-Object System.Net.Sockets.TcpClient
    $client.Connect($PI_HOST, 5000)
    $stream = $client.GetStream()
    $reader = New-Object System.IO.StreamReader($stream)
    
    # Set timeout
    $stream.ReadTimeout = 2000
    
    $data = $reader.ReadLine()
    if ($data) {
        Write-Host "   [OK] Receiving sensor data" -ForegroundColor Green
        Write-Host "   Sample: $data" -ForegroundColor Gray
    }
    $client.Close()
}
catch {
    Write-Host "   [FAIL] Cannot receive sensor data" -ForegroundColor Red
}

Write-Host ""

# Summary
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "DIAGNOSIS SUMMARY" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if (-not $allRunning) {
    Write-Host "[ACTION NEEDED] SERVICES NOT RUNNING ON PI" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To fix this, SSH into the Raspberry Pi:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  ssh pi@$PI_HOST" -ForegroundColor White
    Write-Host ""
    Write-Host "Then run ONE of these options:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Option A - Quick Start (with your PC IP):" -ForegroundColor Cyan
    Write-Host "    cd ~/mariner/pi_scripts" -ForegroundColor White
    Write-Host "    ./start_all_services.sh YOUR_PC_IP" -ForegroundColor White
    Write-Host ""
    Write-Host "  Option B - Auto-detect PC IP:" -ForegroundColor Cyan
    Write-Host "    cd ~/mariner/pi_scripts" -ForegroundColor White
    Write-Host "    ./START_NOW.sh" -ForegroundColor White
    Write-Host ""
    Write-Host "  Option C - Full setup with autostart:" -ForegroundColor Cyan
    Write-Host "    cd ~/mariner/pi_scripts" -ForegroundColor White
    Write-Host "    ./SETUP_AND_START.sh" -ForegroundColor White
    Write-Host ""
    Write-Host "Your Windows PC IP addresses:" -ForegroundColor Yellow
    Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"} | ForEach-Object {
        Write-Host "  * $($_.IPAddress)" -ForegroundColor Green
    }
}
else {
    Write-Host "[SUCCESS] ALL SERVICES ARE RUNNING!" -ForegroundColor Green
    Write-Host ""
    Write-Host "If you still see connection errors:" -ForegroundColor Yellow
    Write-Host "  1. Check Pixhawk is connected to Pi via USB" -ForegroundColor Yellow
    Write-Host "  2. SSH to Pi and run: ls /dev/ttyACM*" -ForegroundColor Yellow
    Write-Host "  3. Check Pi logs: screen -r mavproxy" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Need to check Pixhawk on Pi?" -ForegroundColor Cyan
Write-Host "   SSH to Pi and run:" -ForegroundColor White
Write-Host "   python3 ~/mariner/pi_scripts/detect_pixhawk.py" -ForegroundColor White
Write-Host ""
