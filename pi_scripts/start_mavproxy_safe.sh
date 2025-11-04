#!/bin/bash
# Safe MAVProxy startup script - ensures only one instance runs

# Configuration
MASTER_PORT="/dev/ttyACM1"
BAUDRATE="115200"
TCP_PORT="7000"
LOG_FILE="/tmp/mavproxy.log"
SCRIPT_NAME="pi_mavproxy_server.py"

echo "Starting MAVProxy Server safely..."
echo "=================================="

# Step 1: Kill any existing instances
echo "Checking for existing MAVProxy instances..."
if pgrep -f "$SCRIPT_NAME" > /dev/null; then
    echo "Found existing MAVProxy process(es). Stopping them..."
    pkill -f "$SCRIPT_NAME"
    sleep 2
    
    # Force kill if still running
    if pgrep -f "$SCRIPT_NAME" > /dev/null; then
        echo "Force stopping remaining processes..."
        pkill -9 -f "$SCRIPT_NAME"
        sleep 1
    fi
    echo "✓ Old processes stopped"
else
    echo "✓ No existing processes found"
fi

# Step 2: Check if port is still in use
echo "Checking if port $TCP_PORT is free..."
if netstat -tuln 2>/dev/null | grep -q ":$TCP_PORT "; then
    echo "⚠ Port $TCP_PORT is still in use. Finding process..."
    PORT_PID=$(lsof -ti :$TCP_PORT 2>/dev/null)
    if [ ! -z "$PORT_PID" ]; then
        echo "Killing process $PORT_PID using port $TCP_PORT..."
        kill -9 $PORT_PID 2>/dev/null
        sleep 1
    fi
fi

# Step 3: Verify Pixhawk connection
echo "Checking Pixhawk connection on $MASTER_PORT..."
if [ ! -e "$MASTER_PORT" ]; then
    echo "❌ ERROR: Pixhawk not found at $MASTER_PORT"
    echo "Please check USB connection and run: ls -l /dev/ttyACM*"
    exit 1
fi
echo "✓ Pixhawk found at $MASTER_PORT"

# Step 4: Clear old log
if [ -f "$LOG_FILE" ]; then
    echo "Backing up old log..."
    mv "$LOG_FILE" "${LOG_FILE}.old"
fi

# Step 5: Start the MAVProxy server
echo "Starting MAVProxy server..."
echo "  Master: $MASTER_PORT @ $BAUDRATE baud"
echo "  TCP Port: $TCP_PORT"
echo "  Log: $LOG_FILE"

cd /home/pi/mariner/pi_scripts || exit 1
nohup python3 "$SCRIPT_NAME" \
    --master "$MASTER_PORT" \
    --baudrate "$BAUDRATE" \
    --port "$TCP_PORT" \
    > "$LOG_FILE" 2>&1 &

NEW_PID=$!
sleep 2

# Step 6: Verify startup
if ps -p $NEW_PID > /dev/null; then
    echo ""
    echo "=================================="
    echo "✅ MAVProxy server started successfully!"
    echo "PID: $NEW_PID"
    echo "TCP Port: $TCP_PORT"
    echo "Log: $LOG_FILE"
    echo ""
    echo "To view logs: tail -f $LOG_FILE"
    echo "To stop: pkill -f $SCRIPT_NAME"
    echo "=================================="
    
    # Show initial log output
    echo ""
    echo "Initial log output:"
    sleep 1
    tail -15 "$LOG_FILE" 2>/dev/null || echo "(log file not ready yet)"
    
    exit 0
else
    echo ""
    echo "❌ ERROR: MAVProxy server failed to start"
    echo "Check log: cat $LOG_FILE"
    exit 1
fi
