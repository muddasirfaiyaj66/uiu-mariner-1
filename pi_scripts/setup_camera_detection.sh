#!/bin/bash

# ========================================
# Camera Detection Setup Script
# Install and configure camera detection on Raspberry Pi
# ========================================

echo "══════════════════════════════════════════════════════"
echo "  UIU MARINER - Camera Detection Setup"
echo "══════════════════════════════════════════════════════"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Warning: This script is designed for Raspberry Pi${NC}"
    read -p "Continue anyway? (y/N): " continue
    if [[ ! $continue =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "─────────────────────────────────────────────────────"
echo "1️⃣  Installing Required Packages"
echo "─────────────────────────────────────────────────────"
echo ""

# Update package list
echo "Updating package list..."
sudo apt-get update -qq

# Install libcamera tools
echo ""
echo "📦 Installing libcamera tools (for Pi Camera)..."
if ! command -v libcamera-hello &> /dev/null; then
    sudo apt-get install -y libcamera-apps libcamera-tools
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ libcamera tools installed${NC}"
    else
        echo -e "${RED}❌ Failed to install libcamera tools${NC}"
    fi
else
    echo -e "${GREEN}✅ libcamera tools already installed${NC}"
fi

# Install v4l2-utils
echo ""
echo "📦 Installing v4l2-utils (for USB cameras)..."
if ! command -v v4l2-ctl &> /dev/null; then
    sudo apt-get install -y v4l2-utils
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ v4l2-utils installed${NC}"
    else
        echo -e "${RED}❌ Failed to install v4l2-utils${NC}"
    fi
else
    echo -e "${GREEN}✅ v4l2-utils already installed${NC}"
fi

# Install Python3 (should already be there)
echo ""
echo "📦 Checking Python3..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python3 installed: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python3 not found${NC}"
    echo "Installing Python3..."
    sudo apt-get install -y python3
fi

echo ""
echo "─────────────────────────────────────────────────────"
echo "2️⃣  Creating Directory Structure"
echo "─────────────────────────────────────────────────────"
echo ""

# Create mariner directory
MARINER_DIR="/home/pi/mariner"
if [ ! -d "$MARINER_DIR" ]; then
    mkdir -p "$MARINER_DIR"
    echo -e "${GREEN}✅ Created directory: $MARINER_DIR${NC}"
else
    echo -e "${GREEN}✅ Directory exists: $MARINER_DIR${NC}"
fi

echo ""
echo "─────────────────────────────────────────────────────"
echo "3️⃣  Copying Detection Scripts"
echo "─────────────────────────────────────────────────────"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Copy detection scripts
if [ -f "$SCRIPT_DIR/detect_cameras.py" ]; then
    cp "$SCRIPT_DIR/detect_cameras.py" "$MARINER_DIR/"
    chmod +x "$MARINER_DIR/detect_cameras.py"
    echo -e "${GREEN}✅ Copied detect_cameras.py${NC}"
else
    echo -e "${YELLOW}⚠️  detect_cameras.py not found in current directory${NC}"
fi

if [ -f "$SCRIPT_DIR/detect_cameras.sh" ]; then
    cp "$SCRIPT_DIR/detect_cameras.sh" "$MARINER_DIR/"
    chmod +x "$MARINER_DIR/detect_cameras.sh"
    echo -e "${GREEN}✅ Copied detect_cameras.sh${NC}"
else
    echo -e "${YELLOW}⚠️  detect_cameras.sh not found in current directory${NC}"
fi

echo ""
echo "─────────────────────────────────────────────────────"
echo "4️⃣  Testing Camera Detection"
echo "─────────────────────────────────────────────────────"
echo ""

# Run detection test
if [ -f "$MARINER_DIR/detect_cameras.py" ]; then
    echo "Running camera detection test..."
    echo ""
    python3 "$MARINER_DIR/detect_cameras.py"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Camera detection test successful${NC}"
    else
        echo ""
        echo -e "${YELLOW}⚠️  Camera detection test completed with warnings${NC}"
    fi
else
    echo -e "${RED}❌ Cannot run test - detect_cameras.py not found${NC}"
fi

echo ""
echo "─────────────────────────────────────────────────────"
echo "5️⃣  Configuration Summary"
echo "─────────────────────────────────────────────────────"
echo ""

echo "Installation complete!"
echo ""
echo "Scripts installed in: $MARINER_DIR"
echo ""
echo "Available commands:"
echo "  • python3 $MARINER_DIR/detect_cameras.py"
echo "  • $MARINER_DIR/detect_cameras.sh"
echo ""

# Check camera interface status
echo "Checking camera interface status..."
CAMERA_STATUS=$(vcgencmd get_camera 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "Camera interface: $CAMERA_STATUS"
    
    if [[ $CAMERA_STATUS == *"detected=0"* ]]; then
        echo ""
        echo -e "${YELLOW}⚠️  Pi Camera not detected${NC}"
        echo ""
        echo "To enable Pi Camera:"
        echo "  1. Run: sudo raspi-config"
        echo "  2. Navigate to: Interface Options → Camera"
        echo "  3. Select: Enable"
        echo "  4. Reboot: sudo reboot"
    fi
else
    echo "Unable to check camera status"
fi

echo ""
echo "─────────────────────────────────────────────────────"
echo "6️⃣  Next Steps"
echo "─────────────────────────────────────────────────────"
echo ""

echo "1. If using Pi Camera, ensure it's enabled in raspi-config"
echo "2. Connect your cameras (Pi Camera and/or USB cameras)"
echo "3. Run detection: python3 $MARINER_DIR/detect_cameras.py"
echo "4. Configure cameras in MARINER GUI on ground station"
echo "5. Start streaming with pi_camera_server.py"
echo ""

echo "For detailed instructions, see:"
echo "  • CAMERA_CONFIG_GUIDE.md"
echo "  • CAMERA_QUICK_REF.md"
echo ""

echo "══════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "══════════════════════════════════════════════════════"
echo ""

# Ask if user wants to enable camera interface now
read -p "Do you want to enable the camera interface now? (y/N): " enable_cam
if [[ $enable_cam =~ ^[Yy]$ ]]; then
    echo ""
    echo "Opening raspi-config..."
    echo "Navigate to: Interface Options → Camera → Enable"
    echo "Then reboot when prompted"
    sleep 2
    sudo raspi-config
fi
