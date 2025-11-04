#!/bin/bash

# ========================================
# QUICK START - ROV Services with Hardcoded Pixhawk
# ========================================

echo "🚀 UIU MARINER ROV - Quick Start"
echo "========================================"
echo ""
echo "📡 Pixhawk Configuration:"
echo "   Port: /dev/ttyACM0"
echo "   Baud: 115200"
echo "   TCP:  Port 7000"
echo ""
echo "========================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Get Ground Station IP
GROUND_STATION_IP="${1:-192.168.0.104}"
echo "🖥️  Ground Station: $GROUND_STATION_IP"
echo ""

# Start all services with correct Pixhawk settings
./start_all_services.sh "$GROUND_STATION_IP"
