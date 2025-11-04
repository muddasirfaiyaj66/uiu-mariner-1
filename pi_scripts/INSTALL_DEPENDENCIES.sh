#!/bin/bash

# ========================================
# Install Required Packages on Raspberry Pi
# Run this ONCE to install all dependencies
# ========================================

echo "=========================================="
echo "  Installing ROV Dependencies"
echo "=========================================="
echo ""

# Update package list
echo "📦 Updating package list..."
sudo apt-get update -qq

# Install libcamera tools (for Pi Camera)
echo ""
echo "📦 Installing libcamera tools..."
sudo apt-get install -y libcamera-apps libcamera-tools

# Install GStreamer (for video streaming)
echo ""
echo "📦 Installing GStreamer..."
sudo apt-get install -y \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav

# Install MAVProxy (for Pixhawk communication)
echo ""
echo "📦 Installing MAVProxy..."
sudo apt-get install -y python3-pip
sudo pip3 install pymavlink mavproxy

# Install Python packages for sensors
echo ""
echo "📦 Installing Python sensor libraries..."
sudo pip3 install adafruit-circuitpython-bmp3xx

# Install v4l2-utils (for USB cameras)
echo ""
echo "📦 Installing v4l2-utils..."
sudo apt-get install -y v4l2-utils

echo ""
echo "=========================================="
echo "  ✅ Installation Complete!"
echo "=========================================="
echo ""
echo "Installed:"
echo "  ✅ libcamera-apps"
echo "  ✅ GStreamer"
echo "  ✅ MAVProxy"
echo "  ✅ Python sensor libraries"
echo "  ✅ v4l2-utils"
echo ""
echo "Next steps:"
echo "  1. Connect Pixhawk to USB"
echo "  2. Connect camera(s)"
echo "  3. Run: ./START_NOW.sh 192.168.0.104"
echo ""
