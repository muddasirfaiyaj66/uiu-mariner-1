# Update MAVProxy Configuration
# New Port: /dev/ttyAMA0 @ 57600 baud

Write-Host "============================================"
Write-Host "Updating MAVProxy Port Configuration"
Write-Host "New Port: /dev/ttyAMA0 @ 57600 baud"
Write-Host "============================================"
Write-Host ""

$PI_HOST = "pi@raspberrypi.local"

# Upload files
Write-Host "[1/5] Uploading updated scripts..."
scp pi_scripts/mavproxy_service_wrapper.sh "${PI_HOST}:/tmp/"
scp smart_start_mavproxy.sh "${PI_HOST}:/tmp/"
scp pi_scripts/pi_mavproxy_server.py "${PI_HOST}:/tmp/"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to upload files"
    exit 1
}
Write-Host "Files uploaded successfully"
Write-Host ""

# Stop service
Write-Host "[2/5] Stopping MAVProxy service..."
ssh $PI_HOST "sudo systemctl stop mavproxy.service"
Start-Sleep -Seconds 2
Write-Host "Service stopped"
Write-Host ""

# Update files
Write-Host "[3/5] Updating configuration files..."
ssh $PI_HOST "sudo cp /tmp/mavproxy_service_wrapper.sh /usr/local/bin/ && sudo chmod +x /usr/local/bin/mavproxy_service_wrapper.sh && cp /tmp/smart_start_mavproxy.sh ~/ && chmod +x ~/smart_start_mavproxy.sh && mkdir -p ~/mariner/pi_scripts && cp /tmp/pi_mavproxy_server.py ~/mariner/pi_scripts/ && chmod +x ~/mariner/pi_scripts/pi_mavproxy_server.py"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to update files"
    exit 1
}
Write-Host "Files updated successfully"
Write-Host ""

# Restart service
Write-Host "[4/5] Restarting MAVProxy service..."
ssh $PI_HOST "sudo systemctl restart mavproxy.service"
Start-Sleep -Seconds 3
Write-Host "Service restarted"
Write-Host ""

# Check status
Write-Host "[5/5] Checking service status..."
Write-Host ""
ssh $PI_HOST "sudo systemctl status mavproxy.service --no-pager -l"
Write-Host ""

# Test connection
Write-Host "============================================"
Write-Host "Testing Connection"
Write-Host "============================================"
Write-Host ""
Write-Host "Waiting 5 seconds for MAVProxy to stabilize..."
Start-Sleep -Seconds 5

Write-Host "Testing TCP port 7000..."
$result = Test-NetConnection -ComputerName raspberrypi.local -Port 7000 -WarningAction SilentlyContinue

if ($result.TcpTestSucceeded) {
    Write-Host "Port 7000 is OPEN - MAVProxy ready!"
} else {
    Write-Host "Port 7000 is closed"
    Write-Host "Check logs: ssh pi@raspberrypi.local sudo journalctl -u mavproxy.service -n 50"
}

Write-Host ""
Write-Host "============================================"
Write-Host "Configuration Update Complete!"
Write-Host "============================================"
Write-Host ""
Write-Host "Next: python launch_mariner.py"
Write-Host ""
