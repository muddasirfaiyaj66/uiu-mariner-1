#!/bin/bash

# ========================================
# AUTO-START ROV SERVICES ON BOOT
# Installs systemd services for automatic startup
# ========================================

echo "=========================================="
echo "⚙️  ROV AUTO-START INSTALLER"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    echo "   sudo ./install_autostart.sh"
    exit 1
fi

# Get the actual user (not root when using sudo)
ACTUAL_USER="${SUDO_USER:-$USER}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing auto-start services for user: $ACTUAL_USER"
echo "Script directory: $SCRIPT_DIR"
echo ""

# Get Ground Station IP from user
read -p "Enter Ground Station IP address (e.g., 192.168.0.104): " GROUND_STATION_IP

if [ -z "$GROUND_STATION_IP" ]; then
    echo "❌ Ground Station IP is required!"
    exit 1
fi

echo ""
echo "Ground Station IP: $GROUND_STATION_IP"
echo ""

# ========================================
# 1. SENSOR SERVER SERVICE
# ========================================
echo "1️⃣  Creating sensor server service..."

cat > /etc/systemd/system/rov-sensors.service << EOF
[Unit]
Description=ROV Sensor Server (BMP388)
After=network.target
Wants=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/pi_sensor_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "   ✅ Sensor service created"

# ========================================
# 2. MAVPROXY SERVER SERVICE
# ========================================
echo "2️⃣  Creating MAVProxy server service..."

cat > /etc/systemd/system/rov-mavproxy.service << EOF
[Unit]
Description=ROV MAVProxy Server (Pixhawk)
After=network.target
Wants=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/pi_mavproxy_server.py --master /dev/ttyACM0 --baudrate 115200 --port 7000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "   ✅ MAVProxy service created"

# ========================================
# 3. CAMERA 0 SERVICE
# ========================================
echo "3️⃣  Creating camera 0 service..."

cat > /etc/systemd/system/rov-camera0.service << EOF
[Unit]
Description=ROV Camera 0 Stream
After=network.target
Wants=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/pi_camera_server.py 0 $GROUND_STATION_IP 5000 --payload 96
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "   ✅ Camera 0 service created"

# ========================================
# 4. CAMERA 1 SERVICE
# ========================================
echo "4️⃣  Creating camera 1 service..."

cat > /etc/systemd/system/rov-camera1.service << EOF
[Unit]
Description=ROV Camera 1 Stream
After=network.target
Wants=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/pi_camera_server.py 1 $GROUND_STATION_IP 5001 --payload 97
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "   ✅ Camera 1 service created"

# ========================================
# RELOAD AND ENABLE SERVICES
# ========================================
echo ""
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

echo ""
echo "✅ Enabling services to start on boot..."

systemctl enable rov-sensors.service
systemctl enable rov-mavproxy.service
systemctl enable rov-camera0.service
systemctl enable rov-camera1.service

echo ""
echo "=========================================="
echo "✅ AUTO-START INSTALLATION COMPLETE!"
echo "=========================================="
echo ""
echo "📋 Services installed:"
echo "   • rov-sensors    - BMP388 sensor server"
echo "   • rov-mavproxy   - Pixhawk MAVProxy"
echo "   • rov-camera0    - Camera 0 stream"
echo "   • rov-camera1    - Camera 1 stream"
echo ""
echo "🚀 Services will start automatically on boot!"
echo ""
echo "💡 Management commands:"
echo "   Start all:   sudo systemctl start rov-sensors rov-mavproxy rov-camera0 rov-camera1"
echo "   Stop all:    sudo systemctl stop rov-sensors rov-mavproxy rov-camera0 rov-camera1"
echo "   Status:      sudo systemctl status rov-sensors"
echo "   View logs:   sudo journalctl -u rov-sensors -f"
echo "   Disable:     sudo systemctl disable rov-sensors"
echo ""
echo "🔄 Starting services now..."
systemctl start rov-sensors.service
systemctl start rov-mavproxy.service
systemctl start rov-camera0.service
systemctl start rov-camera1.service

sleep 2

echo ""
echo "📊 Service Status:"
systemctl is-active rov-sensors && echo "   ✅ Sensors: Running" || echo "   ❌ Sensors: Failed"
systemctl is-active rov-mavproxy && echo "   ✅ MAVProxy: Running" || echo "   ❌ MAVProxy: Failed"
systemctl is-active rov-camera0 && echo "   ✅ Camera 0: Running" || echo "   ❌ Camera 0: Failed"
systemctl is-active rov-camera1 && echo "   ✅ Camera 1: Running" || echo "   ❌ Camera 1: Failed"

echo ""
echo "=========================================="
echo "✅ DONE! Reboot to test auto-start"
echo "=========================================="
echo ""
