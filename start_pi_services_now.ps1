# Start All ROV Services on Raspberry Pi
# Fixes Pixhawk connection, sensor data, and camera streams

param(
    [string]$PiHost = "192.168.0.182",
    [string]$PiUser = "pi",
    [string]$GroundStationIP = ""  # Auto-detect if empty
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "STARTING ALL ROV SERVICES ON RASPBERRY PI" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Auto-detect Ground Station IP if not provided
if ([string]::IsNullOrEmpty($GroundStationIP)) {
    Write-Host "Auto-detecting Ground Station IP..." -ForegroundColor Yellow
    try {
        $GroundStationIP = (Get-NetIPAddress -AddressFamily IPv4 | 
            Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -like "192.168.*" } |
            Select-Object -First 1).IPAddress
        
        if ([string]::IsNullOrEmpty($GroundStationIP)) {
            $GroundStationIP = "192.168.0.104"
            Write-Host "   Using fallback IP: $GroundStationIP" -ForegroundColor Yellow
        } else {
            Write-Host "   Detected: $GroundStationIP" -ForegroundColor Green
        }
    } catch {
        $GroundStationIP = "192.168.0.104"
        Write-Host "   Detection failed, using: $GroundStationIP" -ForegroundColor Yellow
    }
}

Write-Host "Configuration:" -ForegroundColor White
Write-Host "  Pi: $PiUser@$PiHost" -ForegroundColor Gray
Write-Host "  Ground Station: $GroundStationIP" -ForegroundColor Gray
Write-Host ""

# Step 1: Upload all necessary files
Write-Host "1. Uploading scripts to Raspberry Pi..." -ForegroundColor Yellow

$filesToUpload = @(
    "pi_scripts/START_NOW.sh",
    "pi_scripts/pi_sensor_server.py",
    "pi_scripts/pi_mavproxy_server.py",
    "pi_scripts/cam0.sh",
    "pi_scripts/cam1.sh",
    "pi_scripts/stop_all_services.sh",
    "pi_scripts/fix_serial_conflict.sh"
)

foreach ($file in $filesToUpload) {
    if (Test-Path $file) {
        $fileName = Split-Path $file -Leaf
        Write-Host "   Uploading $fileName..." -ForegroundColor Gray -NoNewline
        scp $file "${PiUser}@${PiHost}:~/mariner/pi_scripts/" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host " OK" -ForegroundColor Green
        } else {
            Write-Host " WARN" -ForegroundColor Yellow
        }
    }
}
Write-Host ""

# Step 2: Stop any existing services
Write-Host "2. Stopping existing services..." -ForegroundColor Yellow
ssh -t "${PiUser}@${PiHost}" @"
cd ~/mariner/pi_scripts
chmod +x *.sh 2>/dev/null
pkill -f 'pi_sensor_server.py' 2>/dev/null
pkill -f 'pi_mavproxy_server.py' 2>/dev/null
pkill -f 'cam0.sh' 2>/dev/null
pkill -f 'cam1.sh' 2>/dev/null
pkill -f 'libcamera-vid' 2>/dev/null
pkill -f 'rpicam-vid' 2>/dev/null
sleep 2
echo '   Cleanup complete'
"@ 2>$null
Write-Host ""

# Step 3: Fix serial port conflicts
Write-Host "3. Fixing serial port conflicts..." -ForegroundColor Yellow
ssh -t "${PiUser}@${PiHost}" @"
cd ~/mariner/pi_scripts
./fix_serial_conflict.sh
"@ 2>$null
Write-Host ""

# Step 4: Start all services
Write-Host "4. Starting all ROV services..." -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Cyan

ssh -t "${PiUser}@${PiHost}" @"
cd ~/mariner/pi_scripts
./START_NOW.sh $GroundStationIP
"@

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Step 5: Wait and verify
Write-Host "5. Verifying services..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

$serviceCheck = ssh "${PiUser}@${PiHost}" "pgrep -f 'pi_sensor_server.py' > /dev/null && echo 'SENSOR_OK' || echo 'SENSOR_FAIL'; pgrep -f 'pi_mavproxy_server.py' > /dev/null && echo 'MAVPROXY_OK' || echo 'MAVPROXY_FAIL'; pgrep -f 'cam0.sh' > /dev/null && echo 'CAM0_OK' || echo 'CAM0_FAIL'; pgrep -f 'cam1.sh' > /dev/null && echo 'CAM1_OK' || echo 'CAM1_FAIL'"

Write-Host ""
Write-Host "Service Status:" -ForegroundColor White
if ($serviceCheck -match "SENSOR_OK") {
    Write-Host "  [OK] Sensor Server (TCP 5002)" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Sensor Server (TCP 5002)" -ForegroundColor Red
}

if ($serviceCheck -match "MAVPROXY_OK") {
    Write-Host "  [OK] MAVProxy/Pixhawk (TCP 7000)" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] MAVProxy/Pixhawk (TCP 7000)" -ForegroundColor Red
}

if ($serviceCheck -match "CAM0_OK") {
    Write-Host "  [OK] Camera 0 (UDP 5000)" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Camera 0 (UDP 5000)" -ForegroundColor Red
}

if ($serviceCheck -match "CAM1_OK") {
    Write-Host "  [OK] Camera 1 (UDP 5001)" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Camera 1 (UDP 5001)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NOW RUN ON WINDOWS:" -ForegroundColor Yellow
Write-Host "   python launch_mariner.py" -ForegroundColor White
Write-Host ""
Write-Host "Troubleshooting:" -ForegroundColor Yellow
Write-Host "   View logs: ssh ${PiUser}@${PiHost} 'tail -f /tmp/rov_*.log'" -ForegroundColor Gray
Write-Host "   Stop all:  ssh ${PiUser}@${PiHost} 'pkill -f pi_'" -ForegroundColor Gray
Write-Host "   Reboot Pi: ssh ${PiUser}@${PiHost} 'sudo reboot'" -ForegroundColor Gray
Write-Host ""
