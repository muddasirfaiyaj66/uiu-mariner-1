#!/bin/bash
# Setup MAVProxy Auto-Start on Raspberry Pi
# Run this script on the Pi to enable auto-start

echo "============================================"
echo "MAVProxy Auto-Start Setup"
echo "============================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root: sudo ./setup_mavproxy_autostart.sh"
    exit 1
fi

echo "📋 Step 1: Installing required files..."

# Copy service wrapper to /usr/local/bin
if [ -f "/home/pi/mavproxy_service_wrapper.sh" ]; then
    cp /home/pi/mavproxy_service_wrapper.sh /usr/local/bin/
    chmod +x /usr/local/bin/mavproxy_service_wrapper.sh
    echo "   ✅ Service wrapper installed"
else
    echo "   ❌ Error: mavproxy_service_wrapper.sh not found in /home/pi/"
    exit 1
fi

# Copy pi_mavproxy_server.py to /home/pi if not exists
if [ ! -f "/home/pi/pi_mavproxy_server.py" ]; then
    echo "   ⚠️  Warning: pi_mavproxy_server.py not found in /home/pi/"
fi

echo ""
echo "📋 Step 2: Creating systemd service..."

# Create systemd service file
cat > /etc/systemd/system/mavproxy.service << 'EOF'
[Unit]
Description=MAVProxy Auto-Start for Pixhawk
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/local/bin/mavproxy_service_wrapper.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "   ✅ Service file created"

echo ""
echo "📋 Step 3: Enabling and starting service..."

# Reload systemd
systemctl daemon-reload

# Enable service to start on boot
systemctl enable mavproxy.service

# Start service now
systemctl start mavproxy.service

echo "   ✅ Service enabled and started"

echo ""
echo "============================================"
echo "✅ MAVProxy Auto-Start Setup Complete!"
echo "============================================"
echo ""
echo "📊 Service Status:"
systemctl status mavproxy.service --no-pager -l

echo ""
echo "📚 Useful Commands:"
echo "   Check status:    sudo systemctl status mavproxy"
echo "   Stop service:    sudo systemctl stop mavproxy"
echo "   Start service:   sudo systemctl start mavproxy"
echo "   Restart service: sudo systemctl restart mavproxy"
echo "   View logs:       sudo journalctl -u mavproxy -f"
echo "   Disable auto-start: sudo systemctl disable mavproxy"
echo ""
