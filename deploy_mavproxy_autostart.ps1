# Deploy MAVProxy Auto-Start to Raspberry Pi
# This script uploads the necessary files and sets up auto-start

$PI_HOST = "192.168.0.182"
$PI_USER = "pi"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "MAVProxy Auto-Start Deployment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if files exist
$files = @(
    "pi_scripts\mavproxy_service_wrapper.sh",
    "pi_scripts\setup_mavproxy_autostart.sh"
)

foreach ($file in $files) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Error: $file not found!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "📤 Step 1: Uploading files to Pi..." -ForegroundColor Yellow
Write-Host ""

# Upload service wrapper
Write-Host "   Uploading mavproxy_service_wrapper.sh..."
scp pi_scripts\mavproxy_service_wrapper.sh ${PI_USER}@${PI_HOST}:/home/pi/

# Upload setup script
Write-Host "   Uploading setup_mavproxy_autostart.sh..."
scp pi_scripts\setup_mavproxy_autostart.sh ${PI_USER}@${PI_HOST}:/home/pi/

# Upload pi_mavproxy_server.py if it exists
if (Test-Path "pi_scripts\pi_mavproxy_server.py") {
    Write-Host "   Uploading pi_mavproxy_server.py..."
    scp pi_scripts\pi_mavproxy_server.py ${PI_USER}@${PI_HOST}:/home/pi/
}

Write-Host ""
Write-Host "✅ Files uploaded successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Step 2: Running setup on Pi..." -ForegroundColor Yellow
Write-Host ""

# Make scripts executable and run setup
ssh ${PI_USER}@${PI_HOST} "chmod +x /home/pi/mavproxy_service_wrapper.sh /home/pi/setup_mavproxy_autostart.sh && sudo /home/pi/setup_mavproxy_autostart.sh"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 MAVProxy will now start automatically when Pi boots!" -ForegroundColor Green
Write-Host ""
Write-Host "Test connection:" -ForegroundColor Yellow
Write-Host "   Test-NetConnection -ComputerName $PI_HOST -Port 7000" -ForegroundColor White
Write-Host ""
Write-Host "View logs on Pi:" -ForegroundColor Yellow
Write-Host "   ssh ${PI_USER}@${PI_HOST} `"sudo journalctl -u mavproxy -f`"" -ForegroundColor White
Write-Host ""
