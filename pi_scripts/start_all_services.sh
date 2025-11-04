#!/bin/bash

# ========================================
# Start All ROV Services on Raspberry Pi
# ========================================

echo "🚀 Starting UIU MARINER ROV Services..."
echo "========================================"

# Get Ground Station IP from user or use default
GROUND_STATION_IP="${1:-192.168.1.100}"
echo "📡 Ground Station IP: $GROUND_STATION_IP"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Start Sensor Server (BMP388)
echo ""
echo "1️⃣  Starting Sensor Server (BMP388)..."
if screen -list | grep -q "sensors"; then
    echo "   ⚠️  Sensor server already running"
else
    screen -dmS sensors python3 "$SCRIPT_DIR/pi_sensor_server.py"
    sleep 1
    if screen -list | grep -q "sensors"; then
        echo "   ✅ Sensor server started"
    else
        echo "   ❌ Failed to start sensor server"
    fi
fi

# Start MAVProxy Server (Pixhawk)
echo ""
echo "2️⃣  Starting MAVProxy Server (Pixhawk)..."
if screen -list | grep -q "mavproxy"; then
    echo "   ⚠️  MAVProxy already running"
else
    screen -dmS mavproxy python3 "$SCRIPT_DIR/pi_mavproxy_server.py" --master /dev/ttyACM0 --baudrate 115200 --port 7000
    sleep 1
    if screen -list | grep -q "mavproxy"; then
        echo "   ✅ MAVProxy started (Port: /dev/ttyACM0, Baud: 115200)"
    else
        echo "   ❌ Failed to start MAVProxy"
    fi
fi

# Start Camera 0
echo ""
echo "3️⃣  Starting Camera 0 Stream..."
if screen -list | grep -q "cam0"; then
    echo "   ⚠️  Camera 0 already running"
else
    screen -dmS cam0 bash -c "cd $SCRIPT_DIR && ./cam0.sh $GROUND_STATION_IP"
    sleep 1
    if screen -list | grep -q "cam0"; then
        echo "   ✅ Camera 0 started (streaming to $GROUND_STATION_IP:5000)"
    else
        echo "   ❌ Failed to start camera 0"
    fi
fi

# Start Camera 1
echo ""
echo "4️⃣  Starting Camera 1 Stream..."
if screen -list | grep -q "cam1"; then
    echo "   ⚠️  Camera 1 already running"
else
    screen -dmS cam1 bash -c "cd $SCRIPT_DIR && ./cam1.sh $GROUND_STATION_IP"
    sleep 1
    if screen -list | grep -q "cam1"; then
        echo "   ✅ Camera 1 started (streaming to $GROUND_STATION_IP:5001)"
    else
        echo "   ❌ Failed to start camera 1"
    fi
fi

# Show status
echo ""
echo "========================================"
echo "✅ Service Startup Complete!"
echo "========================================"
echo ""
echo "📊 Running Services:"
screen -ls | grep -E "sensors|mavproxy|cam0|cam1" || echo "   ⚠️  No services running"

echo ""
echo "💡 Useful Commands:"
echo "   View all services:    screen -ls"
echo "   View sensor logs:     screen -r sensors"
echo "   View MAVProxy logs:   screen -r mavproxy"
echo "   View camera 0 logs:   screen -r cam0"
echo "   View camera 1 logs:   screen -r cam1"
echo "   Detach from screen:   Ctrl+A then D"
echo "   Stop all services:    ./stop_all_services.sh"
echo ""
echo "🎉 Ready for ROV operations!"
