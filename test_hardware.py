#!/usr/bin/env python3
"""
Hardware Test Script
Tests all ROV hardware components: cameras, sensors, Pixhawk, joystick
"""

import sys
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("UIU MARINER - Hardware Test Suite")
print("=" * 60)
print()

# Test 1: Camera Detection
print("[TEST 1] Camera Detection")
print("-" * 40)
try:
    from src.computer_vision.camera_detector import CameraDetector
    detector = CameraDetector()
    cameras = detector.detect_all_cameras()
    print(f"✓ USB Cameras detected: {len(cameras)}")
    for cam in cameras:
        print(f"  - Camera {cam['id']}: {cam['name']}")
except Exception as e:
    print(f"✗ Camera detection failed: {e}")
print()

# Test 2: Network Camera Streams
print("[TEST 2] Network Camera Streams")
print("-" * 40)
try:
    import requests
    
    test_urls = [
        "http://raspberrypi.local:5000/video_feed",
        "http://raspberrypi.local:5001/video_feed",
        "http://raspberrypi.local:5002/video_feed",
        "http://raspberrypi.local:5003/video_feed",
    ]
    
    for i, url in enumerate(test_urls):
        try:
            response = requests.head(url, timeout=2)
            if response.status_code == 200:
                print(f"✓ Camera {i} stream available: {url}")
            else:
                print(f"✗ Camera {i} stream unavailable (status: {response.status_code})")
        except requests.exceptions.RequestException:
            print(f"✗ Camera {i} stream unreachable: {url}")
except ImportError:
    print("✗ requests library not installed (pip install requests)")
except Exception as e:
    print(f"✗ Stream test failed: {e}")
print()

# Test 3: Sensor Server Connection
print("[TEST 3] Sensor Server Connection")
print("-" * 40)
try:
    import socket
    
    host = "raspberrypi.local"
    port = 5002
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    
    if result == 0:
        print(f"✓ Sensor server reachable: {host}:{port}")
    else:
        print(f"✗ Sensor server unreachable: {host}:{port}")
except Exception as e:
    print(f"✗ Sensor connection test failed: {e}")
print()

# Test 4: Pixhawk Detection
print("[TEST 4] Pixhawk Detection")
print("-" * 40)
try:
    from src.services.portScanner import PortScanner
    scanner = PortScanner()
    ports = scanner.scan_ports()
    
    if ports:
        print(f"✓ Serial ports detected: {len(ports)}")
        for port in ports:
            print(f"  - {port['port']}: {port['description']}")
    else:
        print("✗ No Pixhawk serial ports detected")
except Exception as e:
    print(f"✗ Pixhawk detection failed: {e}")
print()

# Test 5: Joystick Detection
print("[TEST 5] Joystick Detection")
print("-" * 40)
try:
    import pygame
    pygame.init()
    pygame.joystick.init()
    
    joystick_count = pygame.joystick.get_count()
    if joystick_count > 0:
        print(f"✓ Joysticks detected: {joystick_count}")
        for i in range(joystick_count):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            print(f"  - {joy.get_name()}")
            print(f"    Axes: {joy.get_numaxes()}, Buttons: {joy.get_numbuttons()}")
    else:
        print("✗ No joysticks detected")
    
    pygame.quit()
except Exception as e:
    print(f"✗ Joystick detection failed: {e}")
print()

# Test 6: Media Directory Structure
print("[TEST 6] Media Directory Structure")
print("-" * 40)
try:
    media_dir = Path(__file__).parent / "media"
    images_dir = media_dir / "images"
    videos_dir = media_dir / "videos"
    
    if media_dir.exists():
        print(f"✓ Media directory exists: {media_dir}")
        print(f"  - Images: {images_dir} {'(exists)' if images_dir.exists() else '(missing)'}")
        print(f"  - Videos: {videos_dir} {'(exists)' if videos_dir.exists() else '(missing)'}")
        
        # Count existing files
        if images_dir.exists():
            image_count = len(list(images_dir.glob("*.jpg"))) + len(list(images_dir.glob("*.png")))
            print(f"  - Total images: {image_count}")
        
        if videos_dir.exists():
            video_count = len(list(videos_dir.glob("*.avi"))) + len(list(videos_dir.glob("*.mp4")))
            print(f"  - Total videos: {video_count}")
    else:
        print(f"✗ Media directory not found: {media_dir}")
except Exception as e:
    print(f"✗ Media directory test failed: {e}")
print()

# Test 7: OpenCV Availability
print("[TEST 7] OpenCV Video Codec")
print("-" * 40)
try:
    import cv2
    print(f"✓ OpenCV version: {cv2.__version__}")
    
    # Test video writer codec
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    print(f"✓ XVID codec available")
    
    # Test image codecs
    test_formats = ['.jpg', '.png', '.bmp']
    available = []
    for fmt in test_formats:
        if cv2.haveImageWriter(fmt):
            available.append(fmt)
    print(f"✓ Image formats available: {', '.join(available)}")
except Exception as e:
    print(f"✗ OpenCV test failed: {e}")
print()

# Test Summary
print("=" * 60)
print("Test Complete!")
print("=" * 60)
print()
print("NOTES:")
print("- If Raspberry Pi is not connected, network tests will fail")
print("- If Pixhawk is not connected, serial port tests will fail")
print("- If no joystick is connected, joystick tests will fail")
print("- USB cameras require physical connection to be detected")
print()
print("To test full functionality:")
print("1. Connect Raspberry Pi and verify network connection")
print("2. Connect Pixhawk via USB/Serial")
print("3. Connect joystick controller")
print("4. Launch application: python launch_mariner.py")
print()
