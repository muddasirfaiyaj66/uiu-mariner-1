#!/bin/bash
# Start USB Camera 1 streaming to Ground Station
# Usage: ./usb_cam1.sh [GROUND_STATION_IP]

GROUND_STATION_IP="${1:-192.168.0.100}"
PORT=5001
PAYLOAD=97

echo "================================"
echo "USB CAMERA 1 STREAM - UIU MARINER"
echo "================================"
echo "Device: /dev/video1"
echo "Destination: $GROUND_STATION_IP:$PORT"
echo "Payload: $PAYLOAD"
echo "================================"

python3 usb_camera_server.py /dev/video1 "$GROUND_STATION_IP" $PORT --payload $PAYLOAD
