#!/usr/bin/env python3
"""
UIU MARINER - Raspberry Pi Diagnostic Script
Run this on the Pi to check all hardware connections
"""

import subprocess
import sys
import os
import socket

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def run_cmd(cmd, timeout=5):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def check_serial_ports():
    """Check for Pixhawk serial connection"""
    print_header("SERIAL PORTS (Pixhawk)")
    
    ports = ["/dev/ttyAMA0", "/dev/serial0", "/dev/ttyUSB0", "/dev/ttyACM0"]
    found = False
    
    for port in ports:
        if os.path.exists(port):
            print(f"  ✅ {port} EXISTS")
            found = True
            # Check permissions
            code, out, err = run_cmd(f"ls -la {port}")
            if code == 0:
                print(f"     {out.strip()}")
        else:
            print(f"  ❌ {port} not found")
    
    if not found:
        print("\n  ⚠️  No serial ports found!")
        print("  → Check if Pixhawk is connected")
        print("  → Check if serial is enabled in raspi-config")
    
    # Check if serial console is disabled
    code, out, err = run_cmd("cat /boot/cmdline.txt | grep -o 'console=serial0'")
    if code == 0 and out.strip():
        print("\n  ⚠️  Serial console may be enabled (conflicts with Pixhawk)")
        print("  → Run: sudo raspi-config → Interface Options → Serial Port")
        print("  → Disable shell over serial, Enable serial hardware")

def check_pixhawk_connection():
    """Try to connect to Pixhawk"""
    print_header("PIXHAWK CONNECTION TEST")
    
    try:
        from pymavlink import mavutil
        
        port = "/dev/ttyAMA0"
        baud = 57600
        
        if not os.path.exists(port):
            print(f"  ❌ {port} does not exist")
            return
        
        print(f"  Trying {port} @ {baud} baud...")
        
        try:
            conn = mavutil.mavlink_connection(port, baud=baud)
            print("  Waiting for heartbeat (10s timeout)...")
            msg = conn.wait_heartbeat(timeout=10)
            
            if msg:
                print(f"  ✅ PIXHAWK CONNECTED!")
                print(f"     Type: {msg.type}")
                print(f"     Autopilot: {msg.autopilot}")
                print(f"     System ID: {msg.get_srcSystem()}")
            else:
                print("  ❌ No heartbeat received")
                print("  → Check Pixhawk power")
                print("  → Check baud rate (try 115200)")
            
            conn.close()
            
        except Exception as e:
            print(f"  ❌ Connection failed: {e}")
            
    except ImportError:
        print("  ❌ pymavlink not installed")
        print("  → Run: pip3 install pymavlink")

def check_cameras():
    """Check camera availability"""
    print_header("CAMERAS")
    
    # Check for video devices
    code, out, err = run_cmd("ls -la /dev/video*")
    if code == 0:
        print("  Video devices found:")
        for line in out.strip().split('\n'):
            print(f"    {line}")
    else:
        print("  ❌ No /dev/video* devices found")
    
    # Check Pi cameras with libcamera
    print("\n  Checking Pi Camera (libcamera)...")
    code, out, err = run_cmd("libcamera-hello --list-cameras 2>&1", timeout=10)
    if code == 0:
        print(f"  {out[:500]}")
    else:
        print(f"  ❌ libcamera check failed: {err}")
    
    # Check Picamera2
    print("\n  Checking Picamera2...")
    try:
        from picamera2 import Picamera2
        cams = Picamera2.global_camera_info()
        if cams:
            print(f"  ✅ Found {len(cams)} camera(s) via Picamera2:")
            for i, cam in enumerate(cams):
                print(f"     Camera {i}: {cam}")
        else:
            print("  ❌ No cameras found via Picamera2")
    except ImportError:
        print("  ❌ Picamera2 not installed")
    except Exception as e:
        print(f"  ❌ Picamera2 error: {e}")

def check_network():
    """Check network configuration"""
    print_header("NETWORK")
    
    # Get IP addresses
    code, out, err = run_cmd("hostname -I")
    if code == 0:
        print(f"  IP Addresses: {out.strip()}")
    
    # Check if ports are listening
    ports = [5002, 7000, 8080, 8081]
    for port in ports:
        code, out, err = run_cmd(f"netstat -tlnp 2>/dev/null | grep :{port}")
        if code == 0 and out.strip():
            print(f"  ✅ Port {port}: LISTENING")
        else:
            print(f"  ❌ Port {port}: NOT listening")

def check_services():
    """Check running screen sessions"""
    print_header("RUNNING SERVICES (screen)")
    
    code, out, err = run_cmd("screen -ls")
    if code == 0:
        print(out)
    else:
        print("  No screen sessions running")

def check_dependencies():
    """Check Python dependencies"""
    print_header("PYTHON DEPENDENCIES")
    
    packages = ["pymavlink", "flask", "picamera2", "cv2", "numpy"]
    
    for pkg in packages:
        try:
            if pkg == "cv2":
                import cv2
                print(f"  ✅ opencv-python: {cv2.__version__}")
            else:
                mod = __import__(pkg)
                ver = getattr(mod, '__version__', 'unknown')
                print(f"  ✅ {pkg}: {ver}")
        except ImportError:
            print(f"  ❌ {pkg}: NOT INSTALLED")

def main():
    print("\n" + "="*60)
    print("   UIU MARINER - RASPBERRY PI DIAGNOSTICS")
    print("="*60)
    
    check_dependencies()
    check_serial_ports()
    check_pixhawk_connection()
    check_cameras()
    check_network()
    check_services()
    
    print_header("DIAGNOSTIC COMPLETE")
    print("""
  NEXT STEPS:
  
  1. If Pixhawk not connecting:
     → Check wiring (TX→RX, RX→TX, GND→GND)
     → Check baud rate matches Pixhawk config
     → Disable serial console in raspi-config
  
  2. If cameras not found:
     → Check camera cable connection
     → Enable camera in raspi-config
     → For USB cameras, check /dev/video*
  
  3. If ports not listening:
     → Run: ./start_all_services.sh
     → Check screen sessions: screen -ls
     → View logs: screen -r mavproxy
""")

if __name__ == "__main__":
    main()
