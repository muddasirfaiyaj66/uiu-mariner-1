#!/usr/bin/env python3
"""
Auto-connect MAVLink Connection Manager
Automatically detects Pi IP, starts MAVProxy if needed, and connects
"""

import socket
import subprocess
import time
import os
import sys
from pathlib import Path


class AutoMAVLinkConnection:
    def __init__(self):
        self.pi_ip = None
        self.pi_user = "pi"
        self.mavproxy_port = 7000
        self.connection_string = None

    def find_pi_ip(self):
        """Auto-detect Raspberry Pi IP address"""
        print("🔍 Searching for Raspberry Pi on network...")

        # Try to run PowerShell script to detect Pi
        script_path = Path(__file__).parent / "pi_scripts" / "auto_detect_pi.ps1"

        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                self.pi_ip = result.stdout.strip().split("\n")[-1]
                print(f"✅ Found Pi at: {self.pi_ip}")
                return True
            else:
                print("❌ Could not detect Pi automatically")
                return False

        except Exception as e:
            print(f"❌ Error detecting Pi: {e}")
            return False

    def check_ssh_connection(self):
        """Verify SSH connection to Pi"""
        try:
            result = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "ConnectTimeout=3",
                    "-o",
                    "BatchMode=yes",
                    f"{self.pi_user}@{self.pi_ip}",
                    "echo",
                    "OK",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except:
            return False

    def is_mavproxy_running(self):
        """Check if MAVProxy server is running on Pi"""
        try:
            result = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "ConnectTimeout=3",
                    f"{self.pi_user}@{self.pi_ip}",
                    "pgrep -f pi_mavproxy_server.py",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except:
            return False

    def is_port_open(self):
        """Check if MAVProxy port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.pi_ip, self.mavproxy_port))
            sock.close()
            return result == 0
        except:
            return False

    def start_mavproxy(self):
        """Start MAVProxy server on Pi"""
        print("🚀 Starting MAVProxy server on Pi...")

        script_path = Path(__file__).parent / "start_pi_mavproxy_safe.ps1"

        try:
            # Update the script to use detected IP
            result = subprocess.run(
                [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    f"& '{script_path}' -PiHost '{self.pi_ip}'",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print("✅ MAVProxy server started")
                time.sleep(2)  # Wait for server to initialize
                return True
            else:
                print(f"❌ Failed to start MAVProxy: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error starting MAVProxy: {e}")
            return False

    def get_connection_string(self):
        """Get MAVLink connection string"""
        if not self.pi_ip:
            if not self.find_pi_ip():
                return None

        # Check if MAVProxy is running
        if not self.is_mavproxy_running() or not self.is_port_open():
            print("⚠️  MAVProxy not running, attempting to start...")
            if not self.start_mavproxy():
                return None

        # Verify port is accessible
        if not self.is_port_open():
            print("❌ MAVProxy port not accessible")
            return None

        self.connection_string = f"tcp:{self.pi_ip}:{self.mavproxy_port}"
        print(f"✅ Connection ready: {self.connection_string}")
        return self.connection_string

    def connect(self):
        """
        Main connection method - handles everything automatically
        Returns: connection_string if successful, None otherwise
        """
        print("=" * 50)
        print("🔌 Auto-Connecting to Pixhawk via Pi")
        print("=" * 50)

        # Step 1: Find Pi
        if not self.find_pi_ip():
            print("\n❌ Cannot proceed without Pi IP address")
            print("Please ensure:")
            print("  1. Raspberry Pi is powered on")
            print("  2. Ethernet cable is connected")
            print("  3. Both devices are on same network")
            return None

        # Step 2: Verify SSH
        print(f"\n🔐 Verifying SSH connection to {self.pi_ip}...")
        if not self.check_ssh_connection():
            print("⚠️  SSH connection not available (may need password)")
            print("This is normal - continuing anyway...")
        else:
            print("✅ SSH connection verified")

        # Step 3: Check/Start MAVProxy
        print(f"\n🔍 Checking MAVProxy status...")
        if self.is_mavproxy_running():
            print("✅ MAVProxy already running")
        else:
            print("⚠️  MAVProxy not running")
            if not self.start_mavproxy():
                print("❌ Failed to start MAVProxy")
                return None

        # Step 4: Verify port
        print(f"\n🔌 Checking port {self.mavproxy_port}...")
        if not self.is_port_open():
            print(f"❌ Port {self.mavproxy_port} not accessible")
            return None
        print("✅ Port is open and ready")

        # Step 5: Build connection string
        self.connection_string = f"tcp:{self.pi_ip}:{self.mavproxy_port}"

        print("\n" + "=" * 50)
        print("✅ READY TO CONNECT")
        print("=" * 50)
        print(f"Connection String: {self.connection_string}")
        print("=" * 50)

        return self.connection_string


# Convenience function for easy import
def auto_connect():
    """
    Simple function to auto-connect to Pixhawk via Pi
    Returns connection string or None
    """
    connector = AutoMAVLinkConnection()
    return connector.connect()


# Test if run directly
if __name__ == "__main__":
    connection_string = auto_connect()

    if connection_string:
        print(f"\n✅ Success! Use this connection string:")
        print(f"   {connection_string}")
        sys.exit(0)
    else:
        print("\n❌ Failed to establish connection")
        sys.exit(1)
