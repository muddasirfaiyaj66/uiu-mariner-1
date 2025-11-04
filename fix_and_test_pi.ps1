# Fix Serial Conflict and Test Thrusters on Raspberry Pi
# Run from Windows to fix the Pi and test thrusters

param(
    [string]$PiHost = "raspberrypi.local",
    [string]$PiUser = "pi",
    [string]$PiDir = "~/mariner"
)

$ErrorActionPreference = "Continue"

Write-Host "🚀 Fix Serial Conflict & Test Thrusters" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Upload fix script
Write-Host "1️⃣  Uploading fix script..." -ForegroundColor Yellow
scp "pi_scripts/fix_serial_conflict.sh" "${PiUser}@${PiHost}:${PiDir}/fix_serial_conflict.sh"
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Failed to upload fix script" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Fix script uploaded" -ForegroundColor Green
Write-Host ""

# Step 2: Upload test script
Write-Host "2️⃣  Uploading test script..." -ForegroundColor Yellow
scp "pi_scripts/test_thruster_direct.py" "${PiUser}@${PiHost}:${PiDir}/test_thruster_direct.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Failed to upload test script" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Test script uploaded" -ForegroundColor Green
Write-Host ""

# Step 3: Make scripts executable
Write-Host "3️⃣  Making scripts executable..." -ForegroundColor Yellow
ssh -t "${PiUser}@${PiHost}" "cd $PiDir && chmod +x fix_serial_conflict.sh"
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Failed to set permissions" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Scripts are executable" -ForegroundColor Green
Write-Host ""

# Step 4: Run fix script
Write-Host "4️⃣  Running fix script on Pi..." -ForegroundColor Yellow
ssh -t "${PiUser}@${PiHost}" "cd $PiDir && ./fix_serial_conflict.sh"
Write-Host ""

# Step 5: Wait a moment
Write-Host "5️⃣  Waiting for port to stabilize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Write-Host "   ✅ Ready" -ForegroundColor Green
Write-Host ""

# Step 6: Run test
Write-Host "6️⃣  Running thruster test..." -ForegroundColor Yellow
Write-Host "=======================================" -ForegroundColor Cyan
ssh -t "${PiUser}@${PiHost}" "cd $PiDir && python3 test_thruster_direct.py"
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Done!" -ForegroundColor Green
Write-Host ""
Write-Host "If the test still fails, try:" -ForegroundColor Yellow
Write-Host "  1. Reboot the Pi: ssh ${PiUser}@${PiHost} 'sudo reboot'" -ForegroundColor Gray
Write-Host "  2. Check USB cable connection" -ForegroundColor Gray
Write-Host "  3. Run: ssh ${PiUser}@${PiHost} 'lsusb' to verify Pixhawk" -ForegroundColor Gray
Write-Host ""
