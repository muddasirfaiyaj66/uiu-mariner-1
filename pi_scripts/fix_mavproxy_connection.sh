#!/bin/bash
# 🔧 Fix MAVProxy Connection Issues on Raspberry Pi

echo "========================================================================"
echo "🔧 MAVPROXY CONNECTION FIX"
echo "========================================================================"
echo ""

echo "Step 1: Finding Pixhawk serial port..."
echo "----------------------------------------"
PORTS=$(ls /dev/ttyACM* 2>/dev/null)

if [ -z "$PORTS" ]; then
    echo "❌ No /dev/ttyACM* ports found!"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check USB cable is connected"
    echo "  2. Check Pixhawk is powered"
    echo "  3. Try: dmesg | tail -20"
    exit 1
fi

echo "✅ Found ports:"
for port in $PORTS; do
    echo "   - $port"
done
echo ""

echo "Step 2: Checking for processes using serial ports..."
echo "----------------------------------------"
PROCS=$(sudo lsof 2>/dev/null | grep ttyACM || true)

if [ -n "$PROCS" ]; then
    echo "⚠️  Found processes using serial ports:"
    echo "$PROCS"
    echo ""
    echo "Killing these processes..."
    
    # Kill MAVProxy
    sudo pkill -9 mavproxy 2>/dev/null || true
    
    # Kill any Python scripts
    ps aux | grep -E "(mavutil|pymavlink)" | grep -v grep | awk '{print $2}' | xargs -r sudo kill -9 2>/dev/null || true
    
    sleep 2
    echo "✅ Processes killed"
else
    echo "✅ No processes using serial ports"
fi
echo ""

echo "Step 3: Testing connection to Pixhawk..."
echo "----------------------------------------"

# Try each port
for port in $PORTS; do
    echo "Testing $port..."
    
    # Quick Python test
    python3 -c "
from pymavlink import mavutil
import sys
try:
    m = mavutil.mavlink_connection('$port', baud=115200)
    m.wait_heartbeat(timeout=3)
    print(f'✅ {sys.argv[1]} - Connected! System ID: {m.target_system}')
    m.close()
    sys.exit(0)
except Exception as e:
    print(f'❌ {sys.argv[1]} - Failed: {e}')
    sys.exit(1)
" "$port"
    
    if [ $? -eq 0 ]; then
        WORKING_PORT=$port
        break
    fi
done

echo ""

if [ -z "$WORKING_PORT" ]; then
    echo "❌ Could not connect to any port!"
    echo ""
    echo "Advanced troubleshooting:"
    echo "  1. Check kernel messages: dmesg | tail -50"
    echo "  2. Check USB devices: lsusb"
    echo "  3. Check permissions: ls -la /dev/ttyACM*"
    echo "  4. Try replugging USB cable"
    exit 1
fi

echo "Step 4: Starting MAVProxy..."
echo "----------------------------------------"
echo "Using port: $WORKING_PORT"
echo ""

# Start MAVProxy with TCP output
echo "Starting MAVProxy..."
mavproxy.py --master=$WORKING_PORT --baudrate=115200 --out=tcpin:0.0.0.0:7000 &
MAVPROXY_PID=$!

sleep 3

# Check if it's still running
if ps -p $MAVPROXY_PID > /dev/null 2>&1; then
    echo "✅ MAVProxy started successfully (PID: $MAVPROXY_PID)"
    echo ""
    echo "MAVProxy is now running and listening on:"
    echo "  - TCP: raspberrypi.local:7000"
    echo "  - Serial: $WORKING_PORT"
    echo ""
    echo "You can now connect from your Windows PC!"
else
    echo "❌ MAVProxy failed to start"
    echo ""
    echo "Check logs: journalctl -u mavproxy -f"
    exit 1
fi

echo ""
echo "========================================================================"
echo "✅ CONNECTION FIX COMPLETE"
echo "========================================================================"
echo ""
echo "To test from Windows:"
echo "  python test_thruster_dataflow.py"
echo ""
echo "To stop MAVProxy:"
echo "  sudo pkill mavproxy"
echo ""
