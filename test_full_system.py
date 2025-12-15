#!/usr/bin/env python3
"""
Full System Test - Joystick → Pixhawk → Thrusters
This script tests the complete control path to identify where it breaks.
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("="*60)
print("FULL SYSTEM TEST - Joystick → Pixhawk → Thrusters")
print("="*60)

# Step 1: Test joystick
print("\n[Step 1] Testing Joystick Controller...")
try:
    from joystickController import JoystickController
    joystick = JoystickController()
    # Note: init happens in constructor
    
    # Wait for joystick to be ready (there's a warmup delay)
    print("   Waiting for joystick warmup...")
    time.sleep(1.5)  # Wait for ready_time
    
    if joystick.is_ready():
        print("✅ Joystick connected!")
        state = joystick.read_joystick()
        manual = joystick.compute_manual_control(state)
        print(f"   Current state: x={manual['x']}, y={manual['y']}, z={manual['z']}, r={manual['r']}")
    else:
        print("❌ Joystick NOT connected!")
        sys.exit(1)
except Exception as e:
    print(f"❌ Joystick error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Test Pixhawk connection
print("\n[Step 2] Testing Pixhawk Connection...")
try:
    from services.mavlinkConnection import PixhawkConnection
    
    # Try different connection strings
    connection_strings = [
        "tcp:192.168.1.100:7000",  # Pi MAVProxy
        "tcp:127.0.0.1:5762",      # Local MAVProxy
        "udp:127.0.0.1:14550",     # Local UDP
    ]
    
    pixhawk = None
    for conn_str in connection_strings:
        print(f"   Trying {conn_str}...")
        test_pixhawk = PixhawkConnection(link=conn_str, auto_detect=False)
        if test_pixhawk.connect():
            print(f"✅ Connected to Pixhawk via {conn_str}")
            pixhawk = test_pixhawk
            break
        else:
            print(f"   ❌ Failed")
    
    if not pixhawk:
        print("❌ Could not connect to Pixhawk on any port!")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Pixhawk connection error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Set MANUAL mode
print("\n[Step 3] Setting MANUAL Mode...")
try:
    result = pixhawk.set_mode("MANUAL")
    print(f"   Set mode result: {result}")
    
    # Verify mode
    time.sleep(0.5)
    if pixhawk.vehicle:
        hb = pixhawk.vehicle.messages.get('HEARTBEAT')
        if hb:
            print(f"   Current mode number: {hb.custom_mode}")
    print("✅ MANUAL mode set!")
except Exception as e:
    print(f"❌ Mode setting error: {e}")

# Step 4: Arm
print("\n[Step 4] Arming (force=True)...")
try:
    result = pixhawk.arm(force=True)
    print(f"   Arm result: {result}")
    time.sleep(0.5)
    
    # Check armed status
    hb = pixhawk.vehicle.messages.get('HEARTBEAT')
    if hb:
        armed = (hb.base_mode & 0x80) != 0
        print(f"   Armed status from heartbeat: {armed}")
    print("✅ Armed!")
except Exception as e:
    print(f"❌ Arming error: {e}")

# Step 5: Test manual control sending
print("\n[Step 5] Testing MANUAL_CONTROL sending...")
print("   Move the joystick to test! (10 seconds)")
print("-"*40)

start_time = time.time()
while time.time() - start_time < 10:
    try:
        # Read joystick
        state = joystick.read_joystick()
        manual = joystick.compute_manual_control(state)
        
        x, y, z, r = manual['x'], manual['y'], manual['z'], manual['r']
        
        # Only print and send if there's input
        if x != 0 or y != 0 or z != 500 or r != 0:
            print(f"   Joystick: surge={x:+5d}, sway={y:+5d}, heave={z:4d}, yaw={r:+5d}")
            
            # Send to Pixhawk
            result = pixhawk.send_manual_control(x=x, y=y, z=z, r=r, buttons=0)
            if result:
                print(f"   ✅ Sent!")
            else:
                print(f"   ❌ Send failed!")
        else:
            # Send neutral to keep connection alive
            pixhawk.send_manual_control(x=0, y=0, z=500, r=0, buttons=0)
        
        time.sleep(0.05)  # 20 Hz
        
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"   Error: {e}")

print("\n" + "="*60)
print("[Step 6] Cleanup - Disarming...")
try:
    pixhawk.disarm()
    print("✅ Disarmed!")
except:
    pass

print("\n" + "="*60)
print("TEST COMPLETE!")
print("="*60)
print("""
If thrusters DID NOT spin during this test:
1. Check ESC calibration
2. Check motor connections
3. Check frame type in ArduSub parameters
4. Ensure thrusters are submerged in water (or set MOT_WET_TST=1)

If thrusters DID spin during this test:
The hardware is working! The issue is in the application code.
Check that the application is:
1. Actually calling send_manual_control()
2. The thruster_armed flag is True when commands are sent
3. The control_timer is running
""")
