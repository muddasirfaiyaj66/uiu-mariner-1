#!/bin/bash
# Reconnect Pixhawk - Quick Diagnostic and Fix

echo "🔍 PIXHAWK CONNECTION DIAGNOSTIC"
echo "================================="
echo ""

echo "Step 1: Physical Connection"
echo "----------------------------"
echo "✓ Check USB cable from Pixhawk to Raspberry Pi"
echo "✓ Ensure Pixhawk is powered (LED lights should be on)"
echo "✓ Try a different USB port on the Pi"
echo "✓ Try a different USB cable"
echo ""

echo "Step 2: Check USB Devices"
echo "-------------------------"
echo "Connected USB devices:"
lsusb
echo ""

echo "Serial ports:"
ls -l /dev/tty{ACM,USB,AMA}* 2>/dev/null || echo "❌ No serial devices found"
echo ""

echo "Step 3: Restart MAVProxy"
echo "------------------------"
echo "Stopping old MAVProxy..."
pkill -f "pi_mavproxy_server.py"
sleep 2

# Try to find Pixhawk
if [ -e /dev/ttyACM0 ]; then
    DEVICE=/dev/ttyACM0
    echo "✅ Found Pixhawk on $DEVICE"
elif [ -e /dev/ttyUSB0 ]; then
    DEVICE=/dev/ttyUSB0
    echo "✅ Found Pixhawk on $DEVICE"
else
    echo "❌ No Pixhawk device found!"
    echo ""
    echo "TROUBLESHOOTING:"
    echo "1. Physically reconnect Pixhawk USB cable"
    echo "2. Check Pixhawk power LED is on"
    echo "3. Run: sudo dmesg | tail -20"
    echo "4. Try different USB cable"
    exit 1
fi

echo "Starting MAVProxy on $DEVICE..."
cd /home/pi/mariner/pi_scripts
nohup python3 pi_mavproxy_server.py --master $DEVICE --baudrate 115200 --port 7000 > /tmp/rov_mavproxy.log 2>&1 &
sleep 2

echo ""
echo "Status:"
if pgrep -f "pi_mavproxy_server" > /dev/null; then
    echo "✅ MAVProxy running (PID: $(pgrep -f 'pi_mavproxy_server'))"
else
    echo "❌ MAVProxy failed to start"
    echo "Check log: tail -20 /tmp/rov_mavproxy.log"
fi

echo ""
echo "================================="
echo "Done! Now try: python launch_mariner.py"
