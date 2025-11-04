#!/bin/bash
# Smart MAVProxy Startup - Wait for Pixhawk to fully boot

echo "🚀 Smart MAVProxy Startup"
echo "========================="
echo ""

# Stop any existing MAVProxy
echo "1. Stopping existing MAVProxy..."
pkill -f "pi_mavproxy"
sleep 2

# Wait for Pixhawk to appear and be stable
echo "2. Waiting for Pixhawk to boot..."
ATTEMPTS=0
MAX_ATTEMPTS=20

while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
    if [ -e /dev/ttyAMA0 ]; then
        PIXHAWK_DEV=/dev/ttyAMA0
        echo "   Found /dev/ttyAMA0 (attempt $((ATTEMPTS+1)))"
        sleep 2  # Wait 2 more seconds for firmware to fully load
        break
    elif [ -e /dev/ttyACM0 ]; then
        PIXHAWK_DEV=/dev/ttyACM0
        echo "   Found /dev/ttyACM0 (attempt $((ATTEMPTS+1)))"
        sleep 2
        break
    elif [ -e /dev/ttyACM1 ]; then
        PIXHAWK_DEV=/dev/ttyACM1
        echo "   Found /dev/ttyACM1 (attempt $((ATTEMPTS+1)))"
        sleep 2
        break
    fi
    sleep 1
    ATTEMPTS=$((ATTEMPTS+1))
done

if [ -z "$PIXHAWK_DEV" ]; then
    echo "❌ Pixhawk not found after $MAX_ATTEMPTS seconds"
    exit 1
fi

echo "3. Waiting 3 seconds for Pixhawk firmware to initialize..."
sleep 3

echo "4. Starting MAVProxy on $PIXHAWK_DEV..."
cd /home/pi/mariner/pi_scripts
nohup python3 pi_mavproxy_server.py --master $PIXHAWK_DEV --baudrate 57600 --port 7000 > /tmp/rov_mavproxy.log 2>&1 &
MAV_PID=$!

sleep 3

echo ""
if ps -p $MAV_PID > /dev/null; then
    echo "✅ MAVProxy started successfully (PID: $MAV_PID)"
    echo ""
    echo "Check connection:"
    echo "  nc -zv localhost 7000"
else
    echo "❌ MAVProxy failed to start"
    echo "Check log: cat /tmp/rov_mavproxy.log"
fi
