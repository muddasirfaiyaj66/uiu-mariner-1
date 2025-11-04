#!/bin/bash

# ========================================
# Camera Detection Script for Raspberry Pi
# Detects Pi Camera Module and USB Webcams
# ========================================

echo "========================================"
echo "📹 CAMERA DETECTION - Raspberry Pi"
echo "========================================"
echo ""

# Check for libcamera (Pi Camera)
echo "1️⃣  Checking for Raspberry Pi Camera Module..."
echo "----------------------------------------"

if command -v libcamera-hello &> /dev/null; then
    echo "✅ libcamera tools installed"
    
    # List cameras
    echo ""
    echo "Detecting Pi cameras with libcamera-hello --list-cameras..."
    LIBCAM_OUTPUT=$(libcamera-hello --list-cameras 2>&1)
    LIBCAM_EXIT=$?
    
    echo "$LIBCAM_OUTPUT"
    
    if [ $LIBCAM_EXIT -eq 0 ]; then
        # Check if any cameras are actually listed
        if echo "$LIBCAM_OUTPUT" | grep -q "Available cameras"; then
            echo ""
            echo "✅ Pi Camera Module(s) detected!"
            echo ""
            echo "📝 To use Pi Camera, update config.json camera pipelines:"
            echo "   Use pi_camera_server.py to stream H.264"
            echo "   Example: python3 pi_camera_server.py 0 GROUND_STATION_IP 5000"
        else
            echo ""
            echo "❌ No Pi Camera Module detected (no cameras in list)"
            echo ""
            echo "🔧 Troubleshooting:"
            echo "   1. Check camera cable connection (CSI connector)"
            echo "   2. Enable camera in raspi-config:"
            echo "      sudo raspi-config → Interface Options → Legacy Camera → Disable"
            echo "      (Use libcamera, not legacy camera interface)"
            echo "   3. Reboot after changing settings: sudo reboot"
        fi
    else
        echo ""
        echo "❌ No Pi Camera Module detected (libcamera-hello failed)"
        echo ""
        echo "🔧 Troubleshooting:"
        echo "   1. Check camera cable connection"
        echo "   2. Enable camera in raspi-config:"
        echo "      sudo raspi-config → Interface Options → Camera → Enable"
        echo "   3. Reboot after enabling"
    fi
else
    echo "❌ libcamera tools not installed"
    echo ""
    echo "📦 Install with:"
    echo "   sudo apt-get update"
    echo "   sudo apt-get install -y libcamera-apps libcamera-tools"
fi

echo ""
echo ""

# Check for USB webcams
echo "2️⃣  Checking for USB Webcams..."
echo "----------------------------------------"

# List video devices
if ls /dev/video* 2>/dev/null; then
    echo "✅ Video devices found:"
    ls -l /dev/video*
    echo ""
    
    # Check if v4l2-ctl is available
    if command -v v4l2-ctl &> /dev/null; then
        echo "📋 Device Details:"
        echo ""
        
        for device in /dev/video*; do
            echo "Device: $device"
            v4l2-ctl --device=$device --info 2>/dev/null | grep -E "Card type|Driver name"
            echo ""
        done
        
        echo "✅ USB webcams detected!"
        echo ""
        echo "📝 To use USB webcam, update config.json camera pipelines:"
        echo "   Pipeline: v4l2src device=/dev/video0 ! videoconvert ! appsink"
        echo "   Or use cv2.VideoCapture(0) in Python"
        
    else
        echo "⚠️  v4l2-utils not installed"
        echo ""
        echo "📦 Install for more info:"
        echo "   sudo apt-get install v4l2-utils"
    fi
else
    echo "❌ No video devices found at /dev/video*"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Check USB webcam is plugged in"
    echo "   2. Try different USB port"
    echo "   3. Check 'lsusb' to see if device is detected"
fi

echo ""
echo ""

# Summary
echo "========================================"
echo "📊 CAMERA SUMMARY"
echo "========================================"
echo ""

# Count Pi cameras
PI_CAM_COUNT=0
if command -v libcamera-hello &> /dev/null; then
    PI_CAM_COUNT=$(libcamera-hello --list-cameras 2>&1 | grep -c "^[0-9]")
fi

# Count USB cameras
USB_CAM_COUNT=0
if ls /dev/video* 2>/dev/null; then
    USB_CAM_COUNT=$(ls /dev/video* 2>/dev/null | wc -l)
fi

echo "Pi Camera Modules: $PI_CAM_COUNT"
echo "USB Webcams: $USB_CAM_COUNT"
echo ""

if [ $PI_CAM_COUNT -gt 0 ] || [ $USB_CAM_COUNT -gt 0 ]; then
    echo "✅ Camera(s) available for streaming!"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. For Pi Camera: Use pi_camera_server.py"
    echo "   2. For USB Camera: Use USB camera streaming script"
    echo "   3. Update Ground Station config.json with correct pipeline"
else
    echo "❌ No cameras detected"
    echo ""
    echo "🔧 Check connections and enable cameras in raspi-config"
fi

echo ""
echo "========================================"
echo "✅ Detection Complete"
echo "========================================"
echo ""
