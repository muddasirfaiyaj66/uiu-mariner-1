#!/bin/bash

# ========================================
# EMERGENCY START - Start All Services NOW
# No questions asked, just start everything
# ========================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 STARTING ALL ROV SERVICES..."
echo ""

# Auto-detect Ground Station IP or use argument/default
if [ -n "$1" ]; then
    # Use provided argument
    GROUND_STATION_IP="$1"
    echo "📡 Using provided IP: $GROUND_STATION_IP"
else
    # Auto-detect Ground Station IP
    echo "📡 Auto-detecting Ground Station IP..."
    GROUND_STATION_IP=$(python3 "$SCRIPT_DIR/get_ground_station_ip.py" --fallback "192.168.0.104" 2>/dev/null | tail -1)
    
    if [ -z "$GROUND_STATION_IP" ] || [ "$GROUND_STATION_IP" = "None" ]; then
        GROUND_STATION_IP="192.168.0.104"
        echo "⚠️  Auto-detection failed, using fallback: $GROUND_STATION_IP"
    else
        echo "✅ Detected Ground Station: $GROUND_STATION_IP"
    fi
fi

# Make scripts executable
chmod +x *.sh *.py 2>/dev/null

# Kill any existing services
echo "🛑 Stopping any existing services..."
pkill -f "pi_sensor_server.py" 2>/dev/null
pkill -f "pi_mavproxy_server.py" 2>/dev/null
pkill -f "cam0.sh" 2>/dev/null
pkill -f "cam1.sh" 2>/dev/null
pkill -f "libcamera-vid" 2>/dev/null
pkill -f "rpicam-vid" 2>/dev/null
sleep 2

# Auto-detect Pixhawk device
echo ""
echo "🔍 Detecting Pixhawk device..."
PIXHAWK_DEVICE=""
for dev in /dev/ttyACM0 /dev/ttyACM1 /dev/ttyUSB0 /dev/ttyUSB1 /dev/ttyAMA0; do
    if [ -e "$dev" ]; then
        echo "   Found: $dev"
        PIXHAWK_DEVICE="$dev"
        break
    fi
done

if [ -z "$PIXHAWK_DEVICE" ]; then
    echo "⚠️  No Pixhawk device found. MAVProxy may fail."
    PIXHAWK_DEVICE="/dev/ttyACM0"
else
    echo "✅ Using: $PIXHAWK_DEVICE"
fi

# Start Sensor Server
echo ""
echo "1️⃣  Starting Sensor Server..."
nohup python3 "$SCRIPT_DIR/pi_sensor_server.py" > /tmp/rov_sensors.log 2>&1 &
SENSOR_PID=$!
echo "   PID: $SENSOR_PID"

# Start MAVProxy Server
echo ""
echo "2️⃣  Starting MAVProxy (Pixhawk $PIXHAWK_DEVICE @ 115200)..."
nohup python3 "$SCRIPT_DIR/pi_mavproxy_server.py" --master $PIXHAWK_DEVICE --baudrate 115200 --port 7000 > /tmp/rov_mavproxy.log 2>&1 &
MAVPROXY_PID=$!
echo "   PID: $MAVPROXY_PID"

# Start Camera 0
echo ""
echo "3️⃣  Starting Camera 0..."
nohup bash "$SCRIPT_DIR/cam0.sh" "$GROUND_STATION_IP" > /tmp/rov_cam0.log 2>&1 &
CAM0_PID=$!
echo "   PID: $CAM0_PID"

# Start Camera 1
echo ""
echo "4️⃣  Starting Camera 1..."
nohup bash "$SCRIPT_DIR/cam1.sh" "$GROUND_STATION_IP" > /tmp/rov_cam1.log 2>&1 &
CAM1_PID=$!
echo "   PID: $CAM1_PID"

# Wait a moment for services to initialize
echo ""
echo "⏳ Waiting for services to start..."
sleep 3

# Check if processes are running
echo ""
echo "=========================================="
echo "📊 SERVICE STATUS"
echo "=========================================="

if ps -p $SENSOR_PID > /dev/null 2>&1; then
    echo "✅ Sensor Server:  RUNNING (PID: $SENSOR_PID)"
else
    echo "❌ Sensor Server:  FAILED"
fi

if ps -p $MAVPROXY_PID > /dev/null 2>&1; then
    echo "✅ MAVProxy:       RUNNING (PID: $MAVPROXY_PID)"
else
    echo "❌ MAVProxy:       FAILED"
fi

if ps -p $CAM0_PID > /dev/null 2>&1; then
    echo "✅ Camera 0:       RUNNING (PID: $CAM0_PID)"
else
    echo "❌ Camera 0:       FAILED"
fi

if ps -p $CAM1_PID > /dev/null 2>&1; then
    echo "✅ Camera 1:       RUNNING (PID: $CAM1_PID)"
else
    echo "❌ Camera 1:       FAILED"
fi

echo ""
echo "=========================================="
echo "🌐 NETWORK CONFIGURATION"
echo "=========================================="
echo "Raspberry Pi IP:    $(hostname -I | awk '{print $1}')"
echo "Ground Station IP:  $GROUND_STATION_IP"
echo "Pixhawk Device:     $PIXHAWK_DEVICE"
echo ""
echo "📡 Listening on:"
echo "   TCP 5000 - Sensor Data"
echo "   TCP 7000 - MAVLink (Pixhawk)"
echo "   UDP 5000 - Camera 0 → $GROUND_STATION_IP"
echo "   UDP 5001 - Camera 1 → $GROUND_STATION_IP"
echo ""

echo "=========================================="
echo "📋 VIEW LOGS"
echo "=========================================="
echo "tail -f /tmp/rov_sensors.log"
echo "tail -f /tmp/rov_mavproxy.log"
echo "tail -f /tmp/rov_cam0.log"
echo "tail -f /tmp/rov_cam1.log"
echo ""

echo "=========================================="
echo "🛑 STOP ALL SERVICES"
echo "=========================================="
echo "pkill -f 'pi_sensor_server.py'"
echo "pkill -f 'pi_mavproxy_server.py'"
echo "pkill -f 'cam0.sh'"
echo "pkill -f 'cam1.sh'"
echo ""

echo "=========================================="
echo "✅ ALL SERVICES STARTED!"
echo "=========================================="
echo ""
echo "🖥️  NOW ON WINDOWS: python launch_mariner.py"
echo ""
