# 🔧 Test Thrusters Directly on Raspberry Pi
# This script uploads and runs the thruster test on the Pi

$PI_HOST = "pi@raspberrypi.local"
$PI_DIR = "~/mariner/pi_scripts"

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 69)
Write-Host "🚀 DIRECT THRUSTER TEST ON RASPBERRY PI" -ForegroundColor Yellow
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 69)
Write-Host ""

Write-Host "This script will:" -ForegroundColor White
Write-Host "  1. Upload test_thruster_direct.py to Raspberry Pi" -ForegroundColor Gray
Write-Host "  2. Run it directly on the Pi (bypassing network issues)" -ForegroundColor Gray
Write-Host "  3. Test each thruster channel individually" -ForegroundColor Gray
Write-Host ""

Write-Host "⚠️  Make sure:" -ForegroundColor Yellow
Write-Host "  - ROV is in water OR propellers are removed" -ForegroundColor White
Write-Host "  - Battery is connected and charged" -ForegroundColor White
Write-Host "  - ESCs are powered" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Aborted." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "📤 Uploading test script to Pi..." -ForegroundColor Cyan

# Upload the script
scp pi_scripts\test_thruster_direct.py "${PI_HOST}:${PI_DIR}/test_thruster_direct.py"

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Upload successful!" -ForegroundColor Green
} else {
    Write-Host "   ❌ Upload failed!" -ForegroundColor Red
    Write-Host "   Check SSH connection: ping raspberrypi.local" -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "🚀 Running test on Raspberry Pi..." -ForegroundColor Cyan
Write-Host ""

# Run the test on Pi (using ; instead of && for compatibility)
ssh -t $PI_HOST "cd $PI_DIR ; python3 test_thruster_direct.py"

Write-Host ""
$separator = "=" * 69
Write-Host $separator -ForegroundColor Cyan
Write-Host "✅ Test Complete!" -ForegroundColor Green
Write-Host $separator -ForegroundColor Cyan
Write-Host ""
