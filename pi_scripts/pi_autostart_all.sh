#!/bin/bash
# ============================================================================
# UIU MARINER - Pi Automated Startup Script
# ============================================================================
# This script automatically initializes all PIU components on Raspberry Pi:
#   - PyMAVLink connection to Pixhawk
#   - Sensor server (BMP388)
#   - Camera streaming servers (H.264 UDP)
#   - Thruster control setup
#   - Logging system
#
# Usage:
#   bash pi_autostart_all.sh     (Start all services)
#   bash pi_autostart_all.sh stop (Stop all services)
#
# Installation:
#   chmod +x pi_autostart_all.sh
#   sudo cp pi_autostart_all.sh /opt/mariner/
#   sudo chown pi:pi /opt/mariner/pi_autostart_all.sh
#
# Autostart on Boot (via cron):
#   crontab -e
#   Add: @reboot bash /opt/mariner/pi_autostart_all.sh
#
# Or via systemd:
#   sudo cp pi_autostart_all.service /etc/systemd/system/
#   sudo systemctl daemon-reload
#   sudo systemctl enable pi_autostart_all.service
#   sudo systemctl start pi_autostart_all.service
# ============================================================================

set -e  # Exit on error

# ============================================================================
# CONFIGURATION
# ============================================================================

PI_USER="pi"
PI_HOME="/home/pi"
PROJECT_DIR="/opt/mariner"
VENV_DIR="${PROJECT_DIR}/venv"
LOGS_DIR="${PROJECT_DIR}/logs"
PID_DIR="/var/run/mariner"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_error() {
    echo -e "${RED}[✗] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

print_info() {
    echo -e "${BLUE}[*] $1${NC}"
}

check_directory() {
    if [ ! -d "$1" ]; then
        print_error "Directory not found: $1"
        return 1
    fi
    print_success "Found: $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "Command not found: $1"
        return 1
    fi
    print_success "Found: $1"
}

# ============================================================================
# STARTUP FUNCTIONS
# ============================================================================

setup_environment() {
    print_header "Setting up environment"
    
    # Create directories
    mkdir -p "$LOGS_DIR"
    mkdir -p "$PID_DIR"
    
    # Create virtual environment if not exists
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    print_info "Updating pip..."
    pip install --upgrade pip > /dev/null 2>&1
    
    # Install requirements
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        print_info "Installing dependencies from requirements.txt..."
        pip install -r "$PROJECT_DIR/requirements.txt" > /dev/null 2>&1
        print_success "Dependencies installed"
    fi
}

check_pixhawk_connection() {
    print_header "Checking Pixhawk Connection"
    
    print_info "Testing MAVLink connection to Pixhawk..."
    
    python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/mariner')

try:
    from src.services.mavlinkConnection import PixhawkConnection
    import time
    
    print("[*] Attempting connection to Pixhawk...")
    pixhawk = PixhawkConnection(link="/dev/ttyAMA0:57600", auto_detect=True)
    
    if pixhawk.connect():
        print("[✓] Pixhawk connected successfully!")
        print(f"[✓] Pixhawk mode: {pixhawk.vehicle.flightmode if pixhawk.vehicle else 'Unknown'}")
        print("[✓] MAVLink connection working")
        sys.exit(0)
    else:
        print("[✗] Failed to connect to Pixhawk")
        sys.exit(1)
        
except Exception as e:
    print(f"[✗] Error: {e}")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Pixhawk connection verified"
        return 0
    else
        print_error "Pixhawk connection failed"
        return 1
    fi
}

start_sensor_server() {
    print_header "Starting Sensor Server"
    
    print_info "Launching sensor telemetry server (BMP388)..."
    
    source "$VENV_DIR/bin/activate"
    
    nohup python3 "$PROJECT_DIR/pi_scripts/pi_sensor_server.py" \
        > "$LOGS_DIR/sensor_server.log" 2>&1 &
    
    SENSOR_PID=$!
    echo "$SENSOR_PID" > "$PID_DIR/sensor_server.pid"
    
    sleep 2
    
    if ps -p $SENSOR_PID > /dev/null; then
        print_success "Sensor server started (PID: $SENSOR_PID)"
        return 0
    else
        print_error "Sensor server failed to start"
        return 1
    fi
}

start_camera_servers() {
    print_header "Starting Camera Servers"
    
    print_info "Launching camera 1 streaming server (UDP port 5000)..."
    source "$VENV_DIR/bin/activate"
    
    nohup python3 "$PROJECT_DIR/pi_scripts/pi_camera_server.py" camera_0 \
        > "$LOGS_DIR/camera_server_0.log" 2>&1 &
    
    CAM0_PID=$!
    echo "$CAM0_PID" > "$PID_DIR/camera_server_0.pid"
    
    sleep 1
    print_info "Launching camera 2 streaming server (UDP port 5001)..."
    
    nohup python3 "$PROJECT_DIR/pi_scripts/pi_camera_server.py" camera_1 \
        > "$LOGS_DIR/camera_server_1.log" 2>&1 &
    
    CAM1_PID=$!
    echo "$CAM1_PID" > "$PID_DIR/camera_server_1.pid"
    
    sleep 2
    
    if ps -p $CAM0_PID > /dev/null && ps -p $CAM1_PID > /dev/null; then
        print_success "Camera servers started (PIDs: $CAM0_PID, $CAM1_PID)"
        return 0
    else
        print_error "Camera servers failed to start"
        return 1
    fi
}

start_mavproxy_relay() {
    print_header "Starting MAVProxy TCP Relay"
    
    print_info "Launching MAVProxy relay server (TCP port 7000)..."
    
    # Check if MAVProxy is installed
    if ! check_command "mavproxy.py"; then
        print_warning "MAVProxy not installed. Installing..."
        pip install MAVProxy > /dev/null 2>&1
    fi
    
    nohup mavproxy.py --master=/dev/ttyAMA0:57600 --out=tcpin:0.0.0.0:7000 \
        > "$LOGS_DIR/mavproxy.log" 2>&1 &
    
    MAVPROXY_PID=$!
    echo "$MAVPROXY_PID" > "$PID_DIR/mavproxy.pid"
    
    sleep 2
    
    if ps -p $MAVPROXY_PID > /dev/null; then
        print_success "MAVProxy relay started (PID: $MAVPROXY_PID)"
        return 0
    else
        print_error "MAVProxy relay failed to start"
        return 1
    fi
}

initialize_thrusters() {
    print_header "Initializing Thruster Control"
    
    print_info "Setting thruster outputs to neutral (1500 μs)..."
    
    python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/mariner')

try:
    from src.services.mavlinkConnection import PixhawkConnection
    import time
    
    print("[*] Connecting to Pixhawk for thruster initialization...")
    pixhawk = PixhawkConnection(link="/dev/ttyAMA0:57600", auto_detect=True)
    
    if pixhawk.connect():
        print("[✓] Connected to Pixhawk")
        
        # Set all thrusters to neutral (1500 = no thrust)
        neutral_channels = [1500] * 8
        
        print("[*] Setting thrusters to neutral...")
        if pixhawk.send_rc_channels_override(neutral_channels):
            print("[✓] All 8 thrusters set to neutral (1500 μs)")
            print("[✓] Thruster channels ready for commands")
            sys.exit(0)
        else:
            print("[✗] Failed to set thruster channels")
            sys.exit(1)
    else:
        print("[✗] Failed to connect to Pixhawk")
        sys.exit(1)
        
except Exception as e:
    print(f"[✗] Error: {e}")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Thrusters initialized and set to neutral"
        return 0
    else
        print_error "Thruster initialization failed"
        return 1
    fi
}

# ============================================================================
# SHUTDOWN FUNCTIONS
# ============================================================================

stop_all_services() {
    print_header "Stopping all services"
    
    # Stop sensor server
    if [ -f "$PID_DIR/sensor_server.pid" ]; then
        SENSOR_PID=$(cat "$PID_DIR/sensor_server.pid")
        if ps -p $SENSOR_PID > /dev/null; then
            kill $SENSOR_PID
            print_success "Sensor server stopped"
        fi
        rm -f "$PID_DIR/sensor_server.pid"
    fi
    
    # Stop camera servers
    for i in 0 1; do
        if [ -f "$PID_DIR/camera_server_${i}.pid" ]; then
            CAM_PID=$(cat "$PID_DIR/camera_server_${i}.pid")
            if ps -p $CAM_PID > /dev/null; then
                kill $CAM_PID
                print_success "Camera server $i stopped"
            fi
            rm -f "$PID_DIR/camera_server_${i}.pid"
        fi
    done
    
    # Stop MAVProxy
    if [ -f "$PID_DIR/mavproxy.pid" ]; then
        MAVPROXY_PID=$(cat "$PID_DIR/mavproxy.pid")
        if ps -p $MAVPROXY_PID > /dev/null; then
            kill $MAVPROXY_PID
            print_success "MAVProxy relay stopped"
        fi
        rm -f "$PID_DIR/mavproxy.pid"
    fi
    
    print_success "All services stopped"
}

show_status() {
    print_header "Service Status"
    
    echo -e "${BLUE}Running Services:${NC}"
    
    [ -f "$PID_DIR/sensor_server.pid" ] && ps -p $(cat "$PID_DIR/sensor_server.pid") > /dev/null && \
        echo -e "  ${GREEN}✓${NC} Sensor Server (PID: $(cat "$PID_DIR/sensor_server.pid"))" || \
        echo -e "  ${RED}✗${NC} Sensor Server (stopped)"
    
    for i in 0 1; do
        [ -f "$PID_DIR/camera_server_${i}.pid" ] && ps -p $(cat "$PID_DIR/camera_server_${i}.pid") > /dev/null && \
            echo -e "  ${GREEN}✓${NC} Camera Server $i (PID: $(cat "$PID_DIR/camera_server_${i}.pid"))" || \
            echo -e "  ${RED}✗${NC} Camera Server $i (stopped)"
    done
    
    [ -f "$PID_DIR/mavproxy.pid" ] && ps -p $(cat "$PID_DIR/mavproxy.pid") > /dev/null && \
        echo -e "  ${GREEN}✓${NC} MAVProxy Relay (PID: $(cat "$PID_DIR/mavproxy.pid"))" || \
        echo -e "  ${RED}✗${NC} MAVProxy Relay (stopped)"
    
    echo -e "\n${BLUE}Pixhawk Connection:${NC}"
    python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/mariner')
try:
    from src.services.mavlinkConnection import PixhawkConnection
    pixhawk = PixhawkConnection(link="/dev/ttyAMA0:57600", auto_detect=True)
    if pixhawk.connect():
        print(f"  ✓ Connected ({pixhawk.link})")
    else:
        print("  ✗ Disconnected")
except:
    print("  ✗ Error checking connection")
EOF
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    case "${1:-start}" in
        start)
            print_header "UIU MARINER - Automatic Startup"
            
            # Setup
            setup_environment || exit 1
            
            # Checks
            check_directory "$PROJECT_DIR" || exit 1
            check_command "python3" || exit 1
            
            # Start services
            check_pixhawk_connection || exit 1
            start_sensor_server || exit 1
            start_camera_servers || exit 1
            start_mavproxy_relay || exit 1
            initialize_thrusters || exit 1
            
            print_header "All systems initialized successfully!"
            sleep 1
            show_status
            ;;
            
        stop)
            stop_all_services
            ;;
            
        status)
            show_status
            ;;
            
        restart)
            stop_all_services
            sleep 2
            main start
            ;;
            
        *)
            echo "Usage: $0 {start|stop|status|restart}"
            exit 1
            ;;
    esac
}

main "$@"
