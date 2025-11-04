#!/usr/bin/env python3
"""
Pixhawk Detection Script for Raspberry Pi
Scans all serial ports and baud rates to find Pixhawk connection
"""

from pymavlink import mavutil
import time
import sys

# Common serial ports on Raspberry Pi
serial_ports = [
    "/dev/ttyAMA0",  # Primary UART (GPIO 14/15)
    "/dev/serial0",  # Alias to primary UART
    "/dev/ttyUSB0",  # USB serial adapter
    "/dev/ttyUSB1",  # Additional USB
    "/dev/ttyACM0",  # USB CDC (Arduino/Pixhawk)
    "/dev/ttyACM1",  # Additional USB CDC
    "/dev/ttyS0",  # Another serial port option
]

# Common baud rates for Pixhawk
baud_rates = [115200, 57600, 38400, 19200, 9600]

print("=" * 60)
print("🔍 PIXHAWK DETECTION SCRIPT")
print("=" * 60)
print()
print("Scanning serial ports for Pixhawk/MAVLink device...")
print()


def check_heartbeat(port, baud):
    """
    Try to connect to a port and wait for HEARTBEAT message
    """
    try:
        print(f"⏳ Checking {port} at {baud} baud...", end=" ")
        sys.stdout.flush()

        # Try to open connection
        master = mavutil.mavlink_connection(port, baud=baud, timeout=3)

        # Wait for heartbeat (timeout 5 seconds)
        msg = master.recv_match(type="HEARTBEAT", blocking=True, timeout=5)

        if msg:
            print("✅ HEARTBEAT RECEIVED!")
            print(f"   Device Type: {msg.type}")
            print(f"   Autopilot: {msg.autopilot}")
            print(f"   System ID: {msg.get_srcSystem()}")
            print(f"   Component ID: {msg.get_srcComponent()}")
            return True, master
        else:
            print("❌ No heartbeat")
            return False, None

    except Exception as e:
        print(f"❌ Error: {str(e)[:40]}")
        return False, None


# Scan all ports and baud rates
found = False
connection = None

for port in serial_ports:
    if found:
        break

    for baud in baud_rates:
        success, conn = check_heartbeat(port, baud)

        if success:
            print()
            print("=" * 60)
            print("✅ PIXHAWK FOUND!")
            print("=" * 60)
            print(f"Port: {port}")
            print(f"Baud Rate: {baud}")
            print()
            print("🔧 Use these settings in your configuration:")
            print(f"   MAVLink Master: {port}")
            print(f"   Baud Rate: {baud}")
            print()
            print("📝 Update pi_mavproxy_server.py with:")
            print(f"   --master {port} --baudrate {baud}")
            print()
            found = True
            connection = conn
            break

if not found:
    print()
    print("=" * 60)
    print("❌ NO PIXHAWK FOUND")
    print("=" * 60)
    print()
    print("🔧 Troubleshooting:")
    print("   1. Check physical connection (USB or UART)")
    print("   2. Verify Pixhawk is powered on")
    print("   3. Check cable is data-capable (not charge-only)")
    print("   4. Enable UART in raspi-config:")
    print("      sudo raspi-config → Interface Options → Serial Port")
    print("      - Login shell over serial: NO")
    print("      - Serial hardware enabled: YES")
    print("   5. Check device permissions:")
    print("      ls -l /dev/tty*")
    print("      sudo usermod -a -G dialout $USER")
    print("   6. Try different USB port")
    print()
    print("📋 Available serial devices:")
    import subprocess

    try:
        result = subprocess.run(
            ["ls", "-l", "/dev/tty*"], capture_output=True, text=True
        )
        print(result.stdout)
    except:
        print("   Could not list devices")

    sys.exit(1)

# Test communication
if connection:
    print("=" * 60)
    print("🧪 TESTING COMMUNICATION")
    print("=" * 60)
    print()
    print("Requesting parameter list...")

    try:
        # Request parameters
        connection.mav.param_request_list_send(
            connection.target_system, connection.target_component
        )

        # Wait for first parameter
        msg = connection.recv_match(type="PARAM_VALUE", blocking=True, timeout=5)
        if msg:
            print(f"✅ Parameter received: {msg.param_id} = {msg.param_value}")
            print()
            print("✅ Communication working properly!")
        else:
            print("⚠️  No parameter response (but heartbeat OK)")

    except Exception as e:
        print(f"⚠️  Communication test error: {e}")

    print()
    print("=" * 60)
    print("✅ DETECTION COMPLETE")
    print("=" * 60)

    connection.close()
    sys.exit(0)
