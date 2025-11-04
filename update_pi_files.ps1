# ========================================
# UPDATE PI FILES - Deploy Latest Changes
# PowerShell script for Windows
# ========================================

param(
    [string]$PiUser = "pi",
    [string]$PiHost = "raspberrypi.local"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "UIU MARINER - Update Pi Scripts" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PiScriptsDir = Join-Path $ScriptDir "pi_scripts"
$PiDest = "/home/$PiUser/mariner/pi_scripts"

Write-Host "📡 Target: $PiUser@$PiHost" -ForegroundColor Yellow
Write-Host "📁 Source: $PiScriptsDir" -ForegroundColor Gray
Write-Host "📁 Destination: $PiDest" -ForegroundColor Gray
Write-Host ""

# Check if pi_scripts directory exists
if (-not (Test-Path $PiScriptsDir)) {
    Write-Host "❌ Error: pi_scripts directory not found at $PiScriptsDir" -ForegroundColor Red
    exit 1
}

# Test SSH connection
Write-Host "🔍 Testing connection to Pi..." -ForegroundColor Yellow
$testConnection = ssh -o ConnectTimeout=5 "$PiUser@$PiHost" "echo 'Connection OK'" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Connection successful" -ForegroundColor Green
} else {
    Write-Host "❌ Cannot connect to $PiUser@$PiHost" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check Pi is powered on and connected"
    Write-Host "  2. Verify network connection:"
    Write-Host "     ping $PiHost"
    Write-Host "  3. Try using IP address:"
    Write-Host "     .\update_pi_files.ps1 -PiHost 192.168.X.X"
    exit 1
}

Write-Host ""
Write-Host "📦 Copying updated scripts..." -ForegroundColor Yellow

# Create destination directory
ssh "$PiUser@$PiHost" "mkdir -p $PiDest" 2>$null

# Get list of files to copy
$filesToCopy = @(
    "get_ground_station_ip.py",
    "START_NOW.sh",
    "cam0.sh",
    "cam1.sh",
    "pi_sensor_server.py",
    "pi_mavproxy_server.py",
    "pi_camera_server.py",
    "detect_cameras.py",
    "detect_cameras.sh",
    "detect_pixhawk.py",
    "INSTALL_DEPENDENCIES.sh",
    "COMPLETE_SETUP_GUIDE.md"
)

$successCount = 0
$failCount = 0

foreach ($file in $filesToCopy) {
    $sourcePath = Join-Path $PiScriptsDir $file
    
    if (Test-Path $sourcePath) {
        Write-Host "  Copying $file..." -ForegroundColor Gray -NoNewline
        
        # Use scp to copy file
        scp "$sourcePath" "$PiUser@${PiHost}:$PiDest/$file" 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✅" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host " ❌" -ForegroundColor Red
            $failCount++
        }
    }
}

Write-Host ""
Write-Host "🔧 Setting execute permissions..." -ForegroundColor Yellow
ssh "$PiUser@$PiHost" "chmod +x $PiDest/*.sh $PiDest/*.py" 2>$null

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ UPDATE COMPLETE" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Yellow
Write-Host "  • Files copied: $successCount" -ForegroundColor Green
if ($failCount -gt 0) {
    Write-Host "  • Files failed: $failCount" -ForegroundColor Red
}
Write-Host ""
Write-Host "📋 New/Updated files on Pi:" -ForegroundColor Yellow
Write-Host "  • get_ground_station_ip.py (NEW - Auto-detect Ground Station)" -ForegroundColor Cyan
Write-Host "  • START_NOW.sh (Updated - auto-detect IP)" -ForegroundColor Cyan
Write-Host "  • cam0.sh (Updated - auto-detect IP)" -ForegroundColor Cyan
Write-Host "  • cam1.sh (Updated - auto-detect IP)" -ForegroundColor Cyan
Write-Host "  • pi_sensor_server.py" -ForegroundColor Gray
Write-Host "  • pi_mavproxy_server.py" -ForegroundColor Gray
Write-Host "  • pi_camera_server.py" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. SSH to Pi:" -ForegroundColor White
Write-Host "     ssh $PiUser@$PiHost" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Start services (auto-detect IP):" -ForegroundColor White
Write-Host "     cd $PiDest && ./START_NOW.sh" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Or specify your PC's IP manually:" -ForegroundColor White
Write-Host "     ./START_NOW.sh 192.168.X.X" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 To find your PC's IP:" -ForegroundColor Yellow
Write-Host "   ipconfig" -ForegroundColor Gray
Write-Host "   Look for 'Ethernet adapter' → 'IPv4 Address'" -ForegroundColor Gray
Write-Host ""
