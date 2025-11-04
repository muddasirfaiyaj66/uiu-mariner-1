#!/bin/bash

# ========================================
# UPDATE PI FILES - Deploy Latest Changes
# Copy updated scripts to Raspberry Pi
# ========================================

echo "=========================================="
echo "UIU MARINER - Update Pi Scripts"
echo "=========================================="
echo ""

# Check if running on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "ℹ️  Running on Windows (Git Bash/MSYS)"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "ℹ️  Running on Linux"
else
    echo "ℹ️  Running on $OSTYPE"
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PI_SCRIPTS_DIR="$SCRIPT_DIR/pi_scripts"

# Pi connection settings
PI_USER="${1:-pi}"
PI_HOST="${2:-raspberrypi.local}"
PI_DEST="/home/$PI_USER/mariner/pi_scripts"

echo ""
echo "📡 Target: $PI_USER@$PI_HOST"
echo "📁 Source: $PI_SCRIPTS_DIR"
echo "📁 Destination: $PI_DEST"
echo ""

# Check if pi_scripts directory exists
if [ ! -d "$PI_SCRIPTS_DIR" ]; then
    echo "❌ Error: pi_scripts directory not found at $PI_SCRIPTS_DIR"
    exit 1
fi

# Test SSH connection
echo "🔍 Testing connection to Pi..."
if ssh -o ConnectTimeout=5 "$PI_USER@$PI_HOST" "echo 'Connection OK'" 2>/dev/null; then
    echo "✅ Connection successful"
else
    echo "❌ Cannot connect to $PI_USER@$PI_HOST"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check Pi is powered on and connected"
    echo "  2. Verify network connection:"
    echo "     ping $PI_HOST"
    echo "  3. Try using IP address:"
    echo "     $0 pi 192.168.X.X"
    exit 1
fi

echo ""
echo "📦 Copying updated scripts..."

# Create destination directory if it doesn't exist
ssh "$PI_USER@$PI_HOST" "mkdir -p $PI_DEST" 2>/dev/null

# Copy all Python and shell scripts
rsync -av --progress \
    --include='*.py' \
    --include='*.sh' \
    --include='INSTALL_DEPENDENCIES.sh' \
    --include='COMPLETE_SETUP_GUIDE.md' \
    --exclude='*' \
    "$PI_SCRIPTS_DIR/" "$PI_USER@$PI_HOST:$PI_DEST/"

if [ $? -eq 0 ]; then
    echo "✅ Files copied successfully"
else
    echo "❌ Copy failed"
    exit 1
fi

echo ""
echo "🔧 Setting execute permissions..."
ssh "$PI_USER@$PI_HOST" "chmod +x $PI_DEST/*.sh $PI_DEST/*.py" 2>/dev/null

echo ""
echo "=========================================="
echo "✅ UPDATE COMPLETE"
echo "=========================================="
echo ""
echo "📋 Files updated on Pi:"
echo "  • get_ground_station_ip.py (NEW)"
echo "  • START_NOW.sh (Updated - auto-detect IP)"
echo "  • cam0.sh (Updated - auto-detect IP)"
echo "  • cam1.sh (Updated - auto-detect IP)"
echo "  • pi_sensor_server.py"
echo "  • pi_mavproxy_server.py"
echo "  • pi_camera_server.py"
echo ""
echo "🚀 Next Steps:"
echo "  1. SSH to Pi: ssh $PI_USER@$PI_HOST"
echo "  2. Start services: cd $PI_DEST && ./START_NOW.sh"
echo "  3. Services will auto-detect your PC's IP"
echo ""
echo "💡 Manual IP (if needed): ./START_NOW.sh 192.168.X.X"
echo ""
