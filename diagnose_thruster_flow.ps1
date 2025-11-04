# Thruster Data Flow Diagnostic Script
# This script helps diagnose the complete flow from joystick to Pixhawk

Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host "=" * 69 -ForegroundColor Cyan
Write-Host "🔍 THRUSTER DATA FLOW DIAGNOSTIC - UIU MARINER" -ForegroundColor Yellow
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host "=" * 69 -ForegroundColor Cyan
Write-Host ""

# Check 1: Python Environment
Write-Host "📌 CHECK 1: Python Environment" -ForegroundColor Yellow
Write-Host "-" * 70 -ForegroundColor Gray
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Python not found in PATH" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check 2: Required Python Packages
Write-Host "📌 CHECK 2: Required Python Packages" -ForegroundColor Yellow
Write-Host "-" * 70 -ForegroundColor Gray

$packages = @("pygame", "pymavlink", "PyQt6")
foreach ($pkg in $packages) {
    $result = python -c "import $pkg; print('OK')" 2>&1
    if ($result -match "OK") {
        Write-Host "   ✅ $pkg installed" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $pkg NOT installed" -ForegroundColor Red
        Write-Host "      Run: pip install $pkg" -ForegroundColor Yellow
    }
}
Write-Host ""

# Check 3: Joystick Connection
Write-Host "📌 CHECK 3: Joystick/Controller Detection" -ForegroundColor Yellow
Write-Host "-" * 70 -ForegroundColor Gray
Write-Host "   Running joystick test..." -ForegroundColor Cyan
python -c @"
import pygame
pygame.init()
pygame.joystick.init()
count = pygame.joystick.get_count()
if count > 0:
    for i in range(count):
        js = pygame.joystick.Joystick(i)
        js.init()
        print(f'   ✅ Joystick {i}: {js.get_name()}')
        print(f'      - Axes: {js.get_numaxes()}')
        print(f'      - Buttons: {js.get_numbuttons()}')
else:
    print('   ❌ No joystick detected')
    print('      - Check USB connection')
    print('      - Try running: python test_controller.py')
"@
Write-Host ""

# Check 4: Network Connection to Pi
Write-Host "📌 CHECK 4: Raspberry Pi Network Connection" -ForegroundColor Yellow
Write-Host "-" * 70 -ForegroundColor Gray

# Try to ping Raspberry Pi
Write-Host "   Testing connection to raspberrypi.local..." -ForegroundColor Cyan
$pingResult = Test-Connection -ComputerName "raspberrypi.local" -Count 2 -Quiet -ErrorAction SilentlyContinue

if ($pingResult) {
    Write-Host "   ✅ Raspberry Pi reachable at raspberrypi.local" -ForegroundColor Green
    
    # Try to get IP address
    $piIP = (Resolve-DnsName "raspberrypi.local" -ErrorAction SilentlyContinue).IPAddress
    if ($piIP) {
        Write-Host "      IP Address: $piIP" -ForegroundColor Cyan
    }
} else {
    Write-Host "   ❌ Cannot reach raspberrypi.local" -ForegroundColor Red
    Write-Host "      Troubleshooting:" -ForegroundColor Yellow
    Write-Host "      - Check if Pi is powered on" -ForegroundColor Yellow
    Write-Host "      - Check network cable connection" -ForegroundColor Yellow
    Write-Host "      - Try: ping raspberrypi.local" -ForegroundColor Yellow
}
Write-Host ""

# Check 5: MAVProxy Port
Write-Host "📌 CHECK 5: MAVProxy Server Port" -ForegroundColor Yellow
Write-Host "-" * 70 -ForegroundColor Gray
Write-Host "   Testing MAVProxy TCP port 7000..." -ForegroundColor Cyan

$tcpTest = Test-NetConnection -ComputerName "raspberrypi.local" -Port 7000 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue

if ($tcpTest) {
    Write-Host "   ✅ MAVProxy server port 7000 is open" -ForegroundColor Green
} else {
    Write-Host "   ❌ Cannot connect to MAVProxy port 7000" -ForegroundColor Red
    Write-Host "      Troubleshooting:" -ForegroundColor Yellow
    Write-Host "      - Check if MAVProxy is running on Pi" -ForegroundColor Yellow
    Write-Host "      - SSH to Pi: ssh pi@raspberrypi.local" -ForegroundColor Yellow
    Write-Host "      - Start MAVProxy: ./start_pi_services.sh" -ForegroundColor Yellow
}
Write-Host ""

# Check 6: Config File
Write-Host "📌 CHECK 6: Configuration File" -ForegroundColor Yellow
Write-Host "-" * 70 -ForegroundColor Gray

if (Test-Path "config.json") {
    Write-Host "   ✅ config.json found" -ForegroundColor Green
    $config = Get-Content "config.json" | ConvertFrom-Json
    Write-Host "      MAVLink Connection: $($config.mavlink_connection)" -ForegroundColor Cyan
    Write-Host "      Joystick Target: $($config.joystick_target)" -ForegroundColor Cyan
    Write-Host "      Update Rate: $($config.update_rate_hz) Hz" -ForegroundColor Cyan
} else {
    Write-Host "   ❌ config.json not found" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host "=" * 69 -ForegroundColor Cyan
Write-Host "📊 DIAGNOSTIC SUMMARY" -ForegroundColor Yellow
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host "=" * 69 -ForegroundColor Cyan
Write-Host ""
Write-Host "Data Flow Path:" -ForegroundColor Cyan
Write-Host "   1. Joystick (USB) → Your PC" -ForegroundColor White
Write-Host "   2. pygame reads button/axis values" -ForegroundColor White
Write-Host "   3. joystickController.py converts to PWM (1000-2000μs)" -ForegroundColor White
Write-Host "   4. mavlinkConnection.py sends RC_CHANNELS_OVERRIDE" -ForegroundColor White
Write-Host "   5. Network → Raspberry Pi → MAVProxy (port 7000)" -ForegroundColor White
Write-Host "   6. MAVProxy → Pixhawk (UART/USB)" -ForegroundColor White
Write-Host "   7. Pixhawk processes and outputs PWM to MAIN OUT 1-8" -ForegroundColor White
Write-Host "   8. ESCs receive PWM and control thruster motors" -ForegroundColor White
Write-Host ""
Write-Host "Channel Mapping (Pixhawk MAIN OUT pins):" -ForegroundColor Cyan
Write-Host "   Pin 1 (Ch1) → Forward/Backward thruster (ACW)" -ForegroundColor White
Write-Host "   Pin 2 (Ch2) → Left/Right rotation" -ForegroundColor White
Write-Host "   Pin 3 (Ch3) → Vertical thruster (ACW)" -ForegroundColor White
Write-Host "   Pin 4 (Ch4) → Vertical thruster (ACW)" -ForegroundColor White
Write-Host "   Pin 5 (Ch5) → Left/Right rotation (opposite)" -ForegroundColor White
Write-Host "   Pin 6 (Ch6) → Vertical thruster (CW)" -ForegroundColor White
Write-Host "   Pin 7 (Ch7) → Vertical thruster (CW)" -ForegroundColor White
Write-Host "   Pin 8 (Ch8) → Forward/Backward thruster (CW)" -ForegroundColor White
Write-Host ""
Write-Host "PWM Signal Values:" -ForegroundColor Cyan
Write-Host "   1000μs = Full reverse/left/down" -ForegroundColor White
Write-Host "   1500μs = Neutral (stopped)" -ForegroundColor White
Write-Host "   2000μs = Full forward/right/up" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Run: python test_thruster_dataflow.py" -ForegroundColor Cyan
Write-Host "      (Complete end-to-end test with live control)" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Run: python launch_mariner.py" -ForegroundColor Cyan
Write-Host "      (Start the full ROV control application)" -ForegroundColor Gray
Write-Host ""
Write-Host "   3. Check thruster movement in QGroundControl" -ForegroundColor Cyan
Write-Host "      (Monitor MAIN OUT 1-8 PWM values in real-time)" -ForegroundColor Gray
Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host "=" * 69 -ForegroundColor Cyan
