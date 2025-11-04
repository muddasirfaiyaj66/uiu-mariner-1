#!/usr/bin/env pwsh
# Update MAVProxy configuration for /dev/ttyAMA0 @ 57600 baud

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Updating MAVProxy Port Configuration" -ForegroundColor Cyan
Write-Host "  New Port: /dev/ttyAMA0 @ 57600 baud" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$PI_HOST = "pi@raspberrypi.local"

# 1. Upload updated scripts
Write-Host "[1/5] 📤 Uploading updated scripts..." -ForegroundColor Green

Write-Host "  - mavproxy_service_wrapper.sh"
scp pi_scripts/mavproxy_service_wrapper.sh "${PI_HOST}:/tmp/"

Write-Host "  - smart_start_mavproxy.sh"
scp smart_start_mavproxy.sh "${PI_HOST}:/tmp/"

Write-Host "  - pi_mavproxy_server.py"
scp pi_scripts/pi_mavproxy_server.py "${PI_HOST}:/tmp/"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to upload files" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Files uploaded" -ForegroundColor Green
Write-Host ""

# 2. Stop existing MAVProxy service
Write-Host "[2/5] ⏸️  Stopping MAVProxy service..." -ForegroundColor Green
ssh $PI_HOST "sudo systemctl stop mavproxy.service"
Start-Sleep -Seconds 2
Write-Host "✅ Service stopped" -ForegroundColor Green
Write-Host ""

# 3. Update files
Write-Host "[3/5] 📝 Updating configuration files..." -ForegroundColor Green
ssh $PI_HOST @"
sudo cp /tmp/mavproxy_service_wrapper.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/mavproxy_service_wrapper.sh
cp /tmp/smart_start_mavproxy.sh ~/
chmod +x ~/smart_start_mavproxy.sh
mkdir -p ~/mariner/pi_scripts
cp /tmp/pi_mavproxy_server.py ~/mariner/pi_scripts/
chmod +x ~/mariner/pi_scripts/pi_mavproxy_server.py
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to update files" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Files updated" -ForegroundColor Green
Write-Host ""

# 4. Restart MAVProxy service
Write-Host "[4/5] 🔄 Restarting MAVProxy service..." -ForegroundColor Green
ssh $PI_HOST "sudo systemctl restart mavproxy.service"
Start-Sleep -Seconds 3
Write-Host "✅ Service restarted" -ForegroundColor Green
Write-Host ""

# 5. Check status
Write-Host "[5/5] 🔍 Checking service status..." -ForegroundColor Green
Write-Host ""
ssh $PI_HOST "sudo systemctl status mavproxy.service --no-pager -l"
Write-Host ""

# 6. Test connection
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Testing Connection" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Waiting 5 seconds for MAVProxy to stabilize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "Testing TCP port 7000..." -ForegroundColor Yellow
$result = Test-NetConnection -ComputerName raspberrypi.local -Port 7000 -WarningAction SilentlyContinue

if ($result.TcpTestSucceeded) {
    Write-Host "✅ Port 7000 is OPEN - MAVProxy ready!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Port 7000 is closed - Check logs:" -ForegroundColor Yellow
    Write-Host "   ssh pi@raspberrypi.local `"sudo journalctl -u mavproxy.service -n 50`"" -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Configuration Update Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Launch the ROV application: python launch_mariner.py" -ForegroundColor White
Write-Host "  2. Check for green Pixhawk connection status" -ForegroundColor White
Write-Host "  3. ARM and test manual control buttons" -ForegroundColor White
Write-Host ""
Write-Host "Troubleshooting:" -ForegroundColor Yellow
Write-Host "  • Check logs: ssh pi@raspberrypi.local `"sudo journalctl -u mavproxy.service -f`"" -ForegroundColor Gray
Write-Host "  • Verify device: ssh pi@raspberrypi.local `"ls -la /dev/ttyAMA*`"" -ForegroundColor Gray
Write-Host "  • Manual test: ssh pi@raspberrypi.local `"~/smart_start_mavproxy.sh`"" -ForegroundColor Gray
Write-Host ""
