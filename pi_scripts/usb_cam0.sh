#!/bin/bash
# Start USB Camera 0 streaming to Ground Station
# Usage: ./usb_cam0.sh [GROUND_STATION_IP]

GROUND_STATION_IP="${1:-192.168.0.100}"
PORT=5000
PAYLOAD=96

echo "================================"
echo "USB CAMERA 0 STREAM - UIU MARINER"
echo "================================"
echo "Device: /dev/video0"
echo "Destination: $GROUND_STATION_IP:$PORT"
echo "Payload: $PAYLOAD"
echo "================================"

python3 usb_camera_server.py /dev/video0 "$GROUND_STATION_IP" $PORT --payload $PAYLOAD
