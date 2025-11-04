#!/bin/bash
# Simple ROV Service Startup Script
# Run with: bash start_all.sh

echo "Starting ROV Services..."
echo ""

# Kill existing
echo "1. Stopping existing services..."
pkill -f "pi_sensor_server.py"
pkill -f "pi_mavproxy_server.py"
pkill -f "cam0.sh"
pkill -f "cam1.sh"
sleep 2

# Find Pixhawk
echo "2. Finding Pixhawk..."
PIXHAWK=/dev/ttyACM0
if [ ! -e "$PIXHAWK" ]; then
    PIXHAWK=/dev/ttyACM1
fi
echo "   Using: $PIXHAWK"

# Start services
echo "3. Starting sensor server (port 5002)..."
nohup python3 /home/pi/mariner/pi_scripts/pi_sensor_server.py --port 5002 > /tmp/rov_sensors.log 2>&1 &
sleep 1

echo "4. Starting MAVProxy server (port 7000)..."
nohup python3 /home/pi/mariner/pi_scripts/pi_mavproxy_server.py --master $PIXHAWK --baudrate 115200 --port 7000 > /tmp/rov_mavproxy.log 2>&1 &
sleep 2

# Check status
echo ""
echo "Status:"
pgrep -f "pi_sensor_server.py" > /dev/null && echo "  [OK] Sensor Server" || echo "  [FAIL] Sensor Server"
pgrep -f "pi_mavproxy_server.py" > /dev/null && echo "  [OK] MAVProxy" || echo "  [FAIL] MAVProxy"

echo ""
echo "View logs:"
echo "  tail -f /tmp/rov_sensors.log"
echo "  tail -f /tmp/rov_mavproxy.log"
echo ""
echo "Done!"
