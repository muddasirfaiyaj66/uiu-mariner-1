# ========================================
# RASPBERRY PI SETUP - MANUAL STEPS
# ========================================
# Follow these steps to set up your Raspberry Pi
# Copy and paste commands one at a time

Write-Host "========================================"
Write-Host "🍓 UIU MARINER - Raspberry Pi Setup"
Write-Host "========================================"
Write-Host ""
Write-Host "Your Raspberry Pi Info:"
Write-Host "  Hostname: raspberrypi.local"
Write-Host "  Username: pi"
Write-Host "  Password: 1234"
Write-Host ""
Write-Host "========================================"
Write-Host ""

# Test connection
Write-Host "STEP 1: Testing connection to Raspberry Pi..."
Write-Host "----------------------------------------"
Write-Host "Command: ping -n 4 raspberrypi.local"
Write-Host ""
ping -n 4 raspberrypi.local
Write-Host ""

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SUCCESS: Raspberry Pi is reachable!" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: Cannot reach Raspberry Pi" -ForegroundColor Red
    Write-Host "   Check that Pi is powered on and connected to network"
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host ""

# SSH connection test
Write-Host "STEP 2: Creating directory on Raspberry Pi..."
Write-Host "----------------------------------------"
Write-Host "This will ask for password: 1234"
Write-Host ""
Write-Host "Command: ssh pi@raspberrypi.local `"mkdir -p ~/mariner`""
Write-Host ""

ssh pi@raspberrypi.local "mkdir -p ~/mariner"

Write-Host ""
Write-Host "========================================"
Write-Host ""

# Copy scripts
Write-Host "STEP 3: Copying scripts to Raspberry Pi..."
Write-Host "----------------------------------------"
Write-Host "This will ask for password: 1234"
Write-Host ""
Write-Host "Command: scp -r pi_scripts pi@raspberrypi.local:~/mariner/"
Write-Host ""

scp -r pi_scripts pi@raspberrypi.local:~/mariner/

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SUCCESS: Scripts copied to Raspberry Pi!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ ERROR: Failed to copy scripts" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host ""

Write-Host "STEP 4: What to do next..."
Write-Host "----------------------------------------"
Write-Host ""
Write-Host "1. Connect to your Raspberry Pi:"
Write-Host "   ssh pi@raspberrypi.local"
Write-Host "   Password: 1234"
Write-Host ""
Write-Host "2. Make scripts executable:"
Write-Host "   cd ~/mariner/pi_scripts"
Write-Host "   chmod +x *.sh *.py"
Write-Host ""
Write-Host "3. Find your PC's IP address:"
Write-Host "   ipconfig"
Write-Host "   Look for IPv4 Address (e.g., 192.168.1.100)"
Write-Host ""
Write-Host "4. Start all services on Pi:"
Write-Host "   ./start_all_services.sh YOUR_PC_IP"
Write-Host ""
Write-Host "5. Launch application on Windows:"
Write-Host "   python launch_mariner.py"
Write-Host ""
Write-Host "========================================"
Write-Host ""
Write-Host "📖 For detailed instructions, see:"
Write-Host "   - QUICK_START_PI.md (quick reference)"
Write-Host "   - pi_scripts/SETUP_RASPBERRY_PI.md (full guide)"
Write-Host ""
Write-Host "✅ Setup script complete!"
Write-Host ""
