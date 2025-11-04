## ========================================
## AUTOMATED PI SERVICES STARTUP
## Start all Raspberry Pi services automatically
## ========================================

param(
    [string]$PiHostname = "raspberrypi.local",
    [string]$PiUser = "pi",
    [string]$PixhawkPort = "/dev/ttyACM0",
    [int]$PixhawkBaud = 115200
)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " UIU MARINER - Pi Services Startup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Get PC IP Address
Write-Host "[1/6] Detecting Ground Station IP..." -ForegroundColor Yellow
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.InterfaceAlias -notmatch "Loopback" -and 
    $_.IPAddress -notmatch "^169" -and
    $_.PrefixOrigin -eq "Dhcp" -or $_.PrefixOrigin -eq "Manual"
} | Select-Object -First 1).IPAddress

if (-not $ipAddress) {
    Write-Host "❌ Could not detect IP address" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Ground Station IP: $ipAddress" -ForegroundColor Green
Write-Host ""

# Test Pi connectivity
Write-Host "[2/6] Testing Raspberry Pi connection..." -ForegroundColor Yellow
$pingResult = Test-Connection -ComputerName $PiHostname -Count 1 -Quiet -ErrorAction SilentlyContinue

if (-not $pingResult) {
    Write-Host "❌ Cannot reach $PiHostname" -ForegroundColor Red
    Write-Host "   Make sure Raspberry Pi is powered on and connected to network" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ Raspberry Pi is reachable" -ForegroundColor Green
Write-Host ""

# Build the startup command
Write-Host "[3/6] Building startup commands..." -ForegroundColor Yellow

$startupCommands = @"
# Kill any existing services
echo '🔄 Stopping existing services...'
pkill -9 -f 'sensorServer.py' 2>/dev/null
pkill -9 -f 'mavproxy' 2>/dev/null
pkill -9 -f 'libcamera-vid' 2>/dev/null
sleep 2

# Start Sensor Server
echo '📡 Starting sensor server...'
cd ~/pi_scripts
python3 sensorServer.py > /tmp/sensor.log 2>&1 &
SENSOR_PID=`$!
sleep 1
if ps -p `$SENSOR_PID > /dev/null; then
    echo '✅ Sensor server started (PID: '`$SENSOR_PID')'
else
    echo '❌ Sensor server failed to start'
    cat /tmp/sensor.log
fi

# Start MAVProxy
echo '🚁 Starting MAVProxy...'
mavproxy.py --master=$PixhawkPort --baudrate=$PixhawkBaud --out=tcpin:0.0.0.0:7000 > /tmp/mavproxy.log 2>&1 &
MAVPROXY_PID=`$!
sleep 2
if ps -p `$MAVPROXY_PID > /dev/null; then
    echo '✅ MAVProxy started (PID: '`$MAVPROXY_PID')'
else
    echo '❌ MAVProxy failed to start'
    cat /tmp/mavproxy.log
fi

# Start Camera 0
echo '📹 Starting Camera 0...'
cd ~/pi_scripts
if [ -f cam0.sh ]; then
    chmod +x cam0.sh
    GS_IP=$ipAddress ./cam0.sh > /tmp/cam0.log 2>&1 &
    CAM0_PID=`$!
    sleep 1
    if ps -p `$CAM0_PID > /dev/null; then
        echo '✅ Camera 0 started (PID: '`$CAM0_PID') → UDP 5000'
    else
        echo '❌ Camera 0 failed to start'
        cat /tmp/cam0.log
    fi
else
    echo '⚠️  cam0.sh not found, skipping'
fi

# Start Camera 1
echo '📹 Starting Camera 1...'
if [ -f cam1.sh ]; then
    chmod +x cam1.sh
    GS_IP=$ipAddress ./cam1.sh > /tmp/cam1.log 2>&1 &
    CAM1_PID=`$!
    sleep 1
    if ps -p `$CAM1_PID > /dev/null; then
        echo '✅ Camera 1 started (PID: '`$CAM1_PID') → UDP 5001'
    else
        echo '❌ Camera 1 failed to start'
        cat /tmp/cam1.log
    fi
else
    echo '⚠️  cam1.sh not found, skipping'
fi

# Summary
echo ''
echo '============================================'
echo ' Services Status Summary'
echo '============================================'
echo 'Ground Station IP: $ipAddress'
echo 'Pixhawk Port: $PixhawkPort @ $PixhawkBaud baud'
echo ''
ps aux | grep -E 'sensorServer|mavproxy|libcamera-vid' | grep -v grep
echo ''
echo '============================================'
echo ' Connection Test'
echo '============================================'
echo 'Sensor Server:'
netstat -tuln | grep 5002 || echo '  ⚠️  Not listening on port 5002'
echo 'MAVProxy:'
netstat -tuln | grep 7000 || echo '  ⚠️  Not listening on port 7000'
echo ''
echo '✅ All services started!'
echo 'Launch Mariner on Ground Station now: python launch_mariner.py'
"@

Write-Host "✅ Commands prepared" -ForegroundColor Green
Write-Host ""

# Execute via SSH
Write-Host "[4/6] Connecting to Pi and starting services..." -ForegroundColor Yellow
Write-Host "    This may take 10-15 seconds..." -ForegroundColor Gray
Write-Host ""

try {
    # Use plink if available (PuTTY), otherwise try ssh
    $sshCommand = "ssh"
    
    # Execute the commands
    $result = $startupCommands | & $sshCommand "${PiUser}@${PiHostname}" "bash -s"
    
    Write-Host $result
    
    Write-Host ""
    Write-Host "[5/6] Verifying connections from Ground Station..." -ForegroundColor Yellow
    Write-Host ""
    
    # Test sensor port
    Write-Host "Testing Sensor Server (TCP 5002)..." -NoNewline
    Start-Sleep -Seconds 2
    $sensorTest = Test-NetConnection -ComputerName $PiHostname -Port 5002 -WarningAction SilentlyContinue
    if ($sensorTest.TcpTestSucceeded) {
        Write-Host " ✅ Connected" -ForegroundColor Green
    } else {
        Write-Host " ❌ Failed" -ForegroundColor Red
    }
    
    # Test MAVLink port
    Write-Host "Testing MAVProxy (TCP 7000)..." -NoNewline
    $mavlinkTest = Test-NetConnection -ComputerName $PiHostname -Port 7000 -WarningAction SilentlyContinue
    if ($mavlinkTest.TcpTestSucceeded) {
        Write-Host " ✅ Connected" -ForegroundColor Green
    } else {
        Write-Host " ❌ Failed" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "[6/6] Startup Complete!" -ForegroundColor Yellow
    Write-Host ""
    
    if ($sensorTest.TcpTestSucceeded -and $mavlinkTest.TcpTestSucceeded) {
        Write-Host "============================================" -ForegroundColor Green
        Write-Host " ✅ ALL SERVICES RUNNING!" -ForegroundColor Green
        Write-Host "============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Ready to launch Mariner:" -ForegroundColor Cyan
        Write-Host "  python launch_mariner.py" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host "============================================" -ForegroundColor Yellow
        Write-Host " ⚠️  SOME SERVICES MAY NOT BE RUNNING" -ForegroundColor Yellow
        Write-Host "============================================" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Check logs on Pi:" -ForegroundColor Cyan
        Write-Host "  ssh $PiUser@$PiHostname" -ForegroundColor Yellow
        Write-Host "  tail -f /tmp/sensor.log /tmp/mavproxy.log" -ForegroundColor Yellow
        Write-Host ""
    }
    
    Write-Host "Camera streams will appear when Mariner connects" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ Error executing commands on Pi:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual SSH command:" -ForegroundColor Yellow
    Write-Host "  ssh $PiUser@$PiHostname" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Optional: Auto-launch Mariner
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Launch Mariner Now?" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press ENTER to launch Mariner, or Ctrl+C to exit" -ForegroundColor Yellow
Read-Host

Write-Host ""
Write-Host "🚀 Launching UIU MARINER..." -ForegroundColor Green
Write-Host ""

# Launch Mariner
python launch_mariner.py
