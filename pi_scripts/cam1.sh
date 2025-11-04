#!/bin/bash
# Start Camera 1 streaming to Ground Station
# Usage: ./cam1.sh [GROUND_STATION_IP]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Auto-detect or use provided IP
if [ -n "$1" ]; then
    GROUND_STATION_IP="$1"
else
    GROUND_STATION_IP=$(python3 "$SCRIPT_DIR/get_ground_station_ip.py" --fallback "192.168.0.100" 2>/dev/null | tail -1)
    if [ -z "$GROUND_STATION_IP" ] || [ "$GROUND_STATION_IP" = "None" ]; then
        GROUND_STATION_IP="192.168.0.100"
    fi
fi

PORT=5001
PAYLOAD=97

echo "================================"
echo "CAMERA 1 STREAM - UIU MARINER"
echo "================================"
echo "Destination: $GROUND_STATION_IP:$PORT"
echo "Payload: $PAYLOAD"
echo "================================"

python3 pi_camera_server.py 1 "$GROUND_STATION_IP" $PORT --payload $PAYLOAD
