#!/bin/bash
# Fix Serial Port Conflict on Raspberry Pi
# This script stops all processes accessing the serial port

echo "🔧 Fixing Serial Port Conflict..."
echo "=================================="
echo ""

# Find the Pixhawk device
PIXHAWK_DEVICE=$(ls /dev/serial/by-id/*Pixhawk* 2>/dev/null | head -n 1)
if [ -z "$PIXHAWK_DEVICE" ]; then
    PIXHAWK_DEVICE=$(ls /dev/ttyACM* 2>/dev/null | head -n 1)
fi

if [ -z "$PIXHAWK_DEVICE" ]; then
    echo "❌ No Pixhawk device found!"
    echo "   Check USB connection"
    exit 1
fi

echo "📍 Pixhawk found: $PIXHAWK_DEVICE"
echo ""

# Stop all MAVProxy processes
echo "1️⃣  Stopping MAVProxy processes..."
pkill -f "mavproxy" 2>/dev/null
pkill -f "pi_mavproxy_server.py" 2>/dev/null
sleep 2

# Kill any process using the serial port
echo "2️⃣  Checking for processes using $PIXHAWK_DEVICE..."
PIDS=$(lsof "$PIXHAWK_DEVICE" 2>/dev/null | awk 'NR>1 {print $2}' | sort -u)

if [ -n "$PIDS" ]; then
    echo "   Found processes: $PIDS"
    for PID in $PIDS; do
        echo "   Killing PID: $PID"
        kill -9 "$PID" 2>/dev/null
    done
    sleep 1
else
    echo "   ✅ No processes using the port"
fi

# Verify port is free
echo ""
echo "3️⃣  Verifying port is free..."
if lsof "$PIXHAWK_DEVICE" 2>/dev/null; then
    echo "   ⚠️  Port still in use!"
    lsof "$PIXHAWK_DEVICE"
else
    echo "   ✅ Port is free"
fi

echo ""
echo "=================================="
echo "✅ Serial port conflict resolved!"
echo ""
echo "You can now run:"
echo "  python3 test_thruster_direct.py"
echo ""
