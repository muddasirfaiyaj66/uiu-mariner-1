#!/bin/bash

# ========================================
# QUICK UPDATE - Change Ground Station IP
# Updates all services with new IP address
# ========================================

echo "=========================================="
echo "🔄 UPDATE GROUND STATION IP"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    echo "   sudo ./update_ground_station_ip.sh"
    exit 1
fi

# Get current IP from camera0 service
CURRENT_IP=$(grep ExecStart /etc/systemd/system/rov-camera0.service 2>/dev/null | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1)

if [ -n "$CURRENT_IP" ]; then
    echo "Current Ground Station IP: $CURRENT_IP"
fi

echo ""
read -p "Enter NEW Ground Station IP: " NEW_IP

if [ -z "$NEW_IP" ]; then
    echo "❌ IP address is required!"
    exit 1
fi

# Validate IP format (basic check)
if ! [[ $NEW_IP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Invalid IP format!"
    exit 1
fi

echo ""
echo "Updating services to use: $NEW_IP"
echo ""

# Update camera services
if [ -f /etc/systemd/system/rov-camera0.service ]; then
    sed -i "s/$CURRENT_IP/$NEW_IP/g" /etc/systemd/system/rov-camera0.service
    echo "✅ Updated rov-camera0"
fi

if [ -f /etc/systemd/system/rov-camera1.service ]; then
    sed -i "s/$CURRENT_IP/$NEW_IP/g" /etc/systemd/system/rov-camera1.service
    echo "✅ Updated rov-camera1"
fi

# Reload and restart services
echo ""
echo "🔄 Reloading services..."
systemctl daemon-reload

echo "🔄 Restarting camera services..."
systemctl restart rov-camera0.service
systemctl restart rov-camera1.service

echo ""
echo "=========================================="
echo "✅ UPDATE COMPLETE!"
echo "=========================================="
echo "Ground Station IP changed to: $NEW_IP"
echo ""
