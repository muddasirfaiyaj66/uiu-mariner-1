# Update Pi Sensor Server
# Deploy updated sensor server to Raspberry Pi

param(
    [string]$PiUser = "pi",
    [string]$PiHost = "raspberrypi.local",
    [int]$Port = 5002
)

Write-Host "=========================================="
Write-Host "UPDATE PI SENSOR SERVER"
Write-Host "=========================================="
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SensorServerFile = Join-Path $ScriptDir "pi_scripts\pi_sensor_server.py"

if (-not (Test-Path $SensorServerFile)) {
    Write-Host "ERROR: pi_sensor_server.py not found"
    exit 1
}

Write-Host "Target: $PiUser@$PiHost"
Write-Host "Port: $Port"
Write-Host ""

# Test connection
Write-Host "Testing connection..."
$test = ssh -o ConnectTimeout=5 "$PiUser@$PiHost" "echo OK" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Cannot connect to Pi"
    exit 1
}
Write-Host "Connected successfully"
Write-Host ""

# Stop existing server
Write-Host "Stopping existing sensor server..."
ssh "$PiUser@$PiHost" "sudo pkill -f pi_sensor_server.py" 2>$null
Start-Sleep -Seconds 1

# Upload file
Write-Host "Uploading pi_sensor_server.py..."
scp "$SensorServerFile" "${PiUser}@${PiHost}:~/" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "File uploaded successfully"
} else {
    Write-Host "ERROR: Upload failed"
    exit 1
}
Write-Host ""

# Start server
Write-Host "Starting sensor server on port $Port..."
$startCmd = "sudo nohup python3 ~/pi_sensor_server.py --port $Port > ~/sensor_server.log 2>&1 &"
ssh "$PiUser@$PiHost" $startCmd
Start-Sleep -Seconds 2

# Check status
Write-Host ""
Write-Host "Checking server status..."
$checkCmd = "ps aux | grep 'pi_sensor_server.py' | grep -v grep"
$result = ssh "$PiUser@$PiHost" $checkCmd 2>$null

if ($LASTEXITCODE -eq 0 -and $result) {
    Write-Host "SUCCESS: Sensor server is running!"
    Write-Host ""
    Write-Host $result
} else {
    Write-Host "WARNING: Server may not be running"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "UPDATE COMPLETE"
Write-Host "=========================================="
Write-Host ""
$serverUrl = "tcp://${PiHost}:${Port}"
Write-Host "Sensor server: $serverUrl"
Write-Host ""
