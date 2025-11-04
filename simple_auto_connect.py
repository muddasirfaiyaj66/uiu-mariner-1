#!/usr/bin/env python3
"""
Simple Auto-Connect for Ground Station Software
Minimizes SSH calls and handles dynamic IP
"""

import socket
import subprocess
import time
from pathlib import Path


def find_pi_quick():
    """Quick Pi detection - tries common IPs first"""
    print("🔍 Looking for Raspberry Pi...")

    # Try common IPs first
    common_ips = [
        "192.168.0.182",
        "192.168.0.100",
        "192.168.0.101",
        "192.168.1.182",
        "192.168.1.100",
    ]

    for ip in common_ips:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, 22))
            sock.close()

            if result == 0:
                print(f"✅ Found Pi at: {ip}")
                return ip
        except:
            continue

    # If not found, try PowerShell script for full scan
    print("⏳ Scanning network (this may take a moment)...")
    try:
        script_path = Path(__file__).parent / "pi_scripts" / "auto_detect_pi.ps1"
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode == 0:
            ip = result.stdout.strip().split("\n")[-1]
            if ip and "." in ip:
                print(f"✅ Found Pi at: {ip}")
                return ip
    except:
        pass

    print("❌ Could not find Raspberry Pi")
    return None


def check_mavproxy_port(ip, port=7000):
    """Check if MAVProxy port is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False


def start_mavproxy(ip):
    """Start MAVProxy on Pi using single SSH command"""
    print("🚀 Starting MAVProxy...")

    # Single SSH command that does everything
    command = (
        f"pkill -f pi_mavproxy_server.py 2>/dev/null; "
        f"sleep 1; "
        f"cd /home/pi/mariner/pi_scripts && "
        f"nohup python3 pi_mavproxy_server.py "
        f"--master /dev/ttyACM1 --baudrate 115200 --port 7000 "
        f">/tmp/mavproxy.log 2>&1 & "
        f"sleep 2; "
        f"pgrep -f pi_mavproxy_server.py >/dev/null && echo OK || echo FAILED"
    )

    try:
        result = subprocess.run(
            [
                "ssh",
                "-o",
                "ConnectTimeout=5",
                "-o",
                "StrictHostKeyChecking=no",
                f"pi@{ip}",
                command,
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )

        if "OK" in result.stdout:
            print("✅ MAVProxy started")
            return True
        else:
            print("⚠️  MAVProxy may not have started properly")
            return False
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return False


def get_connection_string():
    """
    Main function - returns connection string for Pixhawk
    Returns: "tcp:IP:PORT" or None
    """
    print("=" * 50)
    print("🔌 AUTO-CONNECT TO PIXHAWK")
    print("=" * 50)

    # Step 1: Find Pi
    pi_ip = find_pi_quick()
    if not pi_ip:
        print("\n❌ Cannot find Raspberry Pi")
        print("Please check:")
        print("  • Pi is powered on")
        print("  • Ethernet cable connected")
        print("  • Same network as this computer")
        return None

    # Step 2: Check if MAVProxy is already running
    print("\n🔍 Checking MAVProxy...")
    if check_mavproxy_port(pi_ip):
        print("✅ MAVProxy is running")
    else:
        print("⚠️  MAVProxy not running, starting it...")
        start_mavproxy(pi_ip)

        # Wait and check again
        time.sleep(3)
        if not check_mavproxy_port(pi_ip):
            print("❌ MAVProxy port not accessible")
            print("Try manually: ssh pi@{pi_ip}")
            return None
        print("✅ MAVProxy is now running")

    # Step 3: Build connection string
    connection_string = f"tcp:{pi_ip}:7000"

    print("\n" + "=" * 50)
    print("✅ READY!")
    print("=" * 50)
    print(f"Connection: {connection_string}")
    print("=" * 50)

    return connection_string


if __name__ == "__main__":
    import sys

    conn_str = get_connection_string()
    if conn_str:
        print(f"\n✅ Use: {conn_str}")
        sys.exit(0)
    else:
        print("\n❌ Failed")
        sys.exit(1)
