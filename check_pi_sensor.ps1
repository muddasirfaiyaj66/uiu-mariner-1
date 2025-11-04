# Check Pi Sensor Server Status

param(
    [string]$PiUser = "pi",
    [string]$PiHost = "raspberrypi.local"
)

Write-Host "Checking sensor server on $PiHost..." -ForegroundColor Yellow
Write-Host ""

# Check if process is running
Write-Host "Process status:" -ForegroundColor Cyan
ssh "$PiUser@$PiHost" "ps aux | grep pi_sensor_server | grep -v grep"

Write-Host ""
Write-Host "Recent logs:" -ForegroundColor Cyan
ssh "$PiUser@$PiHost" "tail -20 sensor_server.log 2>/dev/null || echo 'No log file found'"

Write-Host ""
