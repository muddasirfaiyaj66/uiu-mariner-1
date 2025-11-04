param(
    [string]$PiHost = "192.168.0.182",
    [string]$PiUser = "pi"
)

Write-Host "`nStarting MAVProxy Server on Raspberry Pi" -ForegroundColor Cyan
Write-Host "Pi Address: $PiUser@$PiHost`n" -ForegroundColor Yellow

Write-Host "[1/4] Uploading safe startup script..." -ForegroundColor Cyan
$scriptContent = Get-Content ".\pi_scripts\start_mavproxy_safe.sh" -Raw
$scriptContent | ssh "$PiUser@$PiHost" "cat > /home/pi/mariner/pi_scripts/start_mavproxy_safe.sh"
Write-Host "[OK] Script uploaded`n" -ForegroundColor Green

Write-Host "[2/4] Making script executable..." -ForegroundColor Cyan
ssh "$PiUser@$PiHost" "chmod +x /home/pi/mariner/pi_scripts/start_mavproxy_safe.sh"
Write-Host "[OK] Permissions set`n" -ForegroundColor Green

Write-Host "[3/4] Stopping existing MAVProxy instances..." -ForegroundColor Cyan
ssh "$PiUser@$PiHost" "pkill -f pi_mavproxy_server.py" 2>$null
Start-Sleep -Seconds 2
Write-Host "[OK] Cleanup complete`n" -ForegroundColor Green

Write-Host "[4/4] Starting MAVProxy server...`n" -ForegroundColor Cyan
$result = ssh "$PiUser@$PiHost" "cd /home/pi/mariner/pi_scripts; ./start_mavproxy_safe.sh"

Write-Host $result
Write-Host "`nDone!" -ForegroundColor Green
