# ========================================
# UPDATE PI SENSOR SERVER
# Deploy updated sensor server to Pi
# ========================================

param(
    [string]$PiUser = "pi",
    [string]$PiHost = "raspberrypi.local",
    [int]$Port = 5002
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "UPDATE PI SENSOR SERVER" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SensorServerFile = Join-Path $ScriptDir "pi_scripts\pi_sensor_server.py"

# Check if file exists
if (-not (Test-Path $SensorServerFile)) {
    Write-Host "❌ Error: pi_sensor_server.py not found" -ForegroundColor Red
    exit 1
}

Write-Host "📡 Target: $PiUser@$PiHost" -ForegroundColor Yellow
Write-Host "🔌 Port: $Port" -ForegroundColor Yellow
Write-Host ""

# Test connection
Write-Host "🔍 Testing connection..." -ForegroundColor Yellow
$testResult = ssh -o ConnectTimeout=5 "$PiUser@$PiHost" "echo OK" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Cannot connect to Pi" -ForegroundColor Red
    Write-Host "   Try: ping $PiHost" -ForegroundColor Gray
    exit 1
}
Write-Host "✅ Connected" -ForegroundColor Green
Write-Host ""

# Stop existing sensor server
Write-Host "⏹️  Stopping existing sensor server..." -ForegroundColor Yellow
ssh "$PiUser@$PiHost" "sudo pkill -f pi_sensor_server.py" 2>$null
Start-Sleep -Seconds 1

# Copy new file
Write-Host "📤 Uploading pi_sensor_server.py..." -ForegroundColor Yellow
scp "$SensorServerFile" "${PiUser}@${PiHost}:~/" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ File uploaded" -ForegroundColor Green
} else {
    Write-Host "❌ Upload failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Start sensor server
Write-Host "🚀 Starting sensor server on port $Port..." -ForegroundColor Yellow
$startCmd = "sudo nohup python3 ~/pi_sensor_server.py --port $Port > ~/sensor_server.log 2>&1 &"
ssh "$PiUser@$PiHost" $startCmd

Start-Sleep -Seconds 2

# Check if running
Write-Host ""
Write-Host "🔍 Checking if server is running..." -ForegroundColor Yellow
$checkCmd = "ps aux | grep 'pi_sensor_server.py' | grep -v grep"
$result = ssh "$PiUser@$PiHost" $checkCmd 2>$null

if ($LASTEXITCODE -eq 0 -and $result) {
    Write-Host "✅ Sensor server is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Server details:" -ForegroundColor Cyan
    Write-Host $result -ForegroundColor Gray
} else {
    Write-Host "⚠️  Server may not be running" -ForegroundColor Yellow
    Write-Host "   Check logs: ssh $PiUser@$PiHost 'cat ~/sensor_server.log'" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ UPDATE COMPLETE" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Sensor server should be accessible at:" -ForegroundColor Yellow
Write-Host "  tcp://${PiHost}:${Port}" -ForegroundColor Cyan
Write-Host ""
