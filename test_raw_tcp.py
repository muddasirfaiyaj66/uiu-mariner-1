#!/usr/bin/env python3
"""Check raw TCP data from Pi relay server"""
import socket
import time

print("[INFO] Connecting to tcp:raspberrypi.local:7000...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("raspberrypi.local", 7000))
print("[✅] Connected!")

print("[INFO] Reading raw bytes for 3 seconds...")
start = time.time()
total_bytes = 0
message_count = 0

while time.time() - start < 3:
    try:
        data = sock.recv(1024)
        if data:
            total_bytes += len(data)
            # Count MAVLink messages (start with 0xFE or 0xFD)
            for byte in data:
                if byte == 0xFE or byte == 0xFD:
                    message_count += 1
            print(
                f"  Received {len(data)} bytes (Total: {total_bytes} bytes, Est. messages: {message_count})"
            )
            # Show first few bytes
            print(f"    First 20 bytes: {data[:20].hex()}")
    except socket.timeout:
        pass

sock.close()
print(f"\n[✅] Total received: {total_bytes} bytes")
print(f"[INFO] Messages detected: ~{message_count}")
