#!/usr/bin/env python3
"""
Thruster Test & Diagnostic Tool
================================
Comprehensive test for ROV thruster system.
Tests connection, arming, and individual thruster control.

Author: UIU MARINER Development Team
"""

import sys
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.mavlinkConnection import PixhawkConnection

print("=" * 70)
print("UIU MARINER - THRUSTER DIAGNOSTIC & TEST TOOL")
print("=" * 70)
print()

def test_connection(connection_string):
    """Test Pixhawk connection"""
    print("[STEP 1] Testing Pixhawk Connection")
    print("-" * 70)
    print(f"Attempting connection to: {connection_string}")
    
    pixhawk = PixhawkConnection(connection_string)
    
    if pixhawk.connect():
        print("✅ Connected to Pixhawk!")
        status = pixhawk.get_status()
        print(f"   System ID: {status['system_id']}")
        print(f"   Component ID: {status['component_id']}")
        print(f"   Last heartbeat: {status['last_heartbeat']:.2f}s ago")
        return pixhawk
    else:
        print("❌ Failed to connect to Pixhawk")
        print("\nTROUBLESHOOTING:")
        print("1. Check if Pixhawk is powered on")
        print("2. Verify connection string:")
        print("   - TCP: tcp:raspberrypi.local:7000")
        print("   - Serial: /dev/ttyAMA0:57600")
        print("   - USB: /dev/ttyUSB0:115200")
        print("3. Check if MAVProxy is running on Raspberry Pi")
        print("4. Verify network connectivity to Raspberry Pi")
        return None


def test_mode_setting(pixhawk):
    """Test flight mode setting"""
    print("\n[STEP 2] Testing Flight Mode")
    print("-" * 70)
    
    # Try setting MANUAL mode
    print("Setting mode to MANUAL...")
    if pixhawk.set_mode("MANUAL"):
        print("✅ Mode set to MANUAL")
        time.sleep(1)
        return True
    else:
        print("❌ Failed to set mode to MANUAL")
        print("\nTROUBLESHOOTING:")
        print("1. Check if Pixhawk is responding")
        print("2. Try setting mode through QGroundControl first")
        print("3. Verify ArduSub firmware is loaded")
        return False


def test_arming(pixhawk):
    """Test vehicle arming"""
    print("\n[STEP 3] Testing Vehicle Arming")
    print("-" * 70)
    
    print("⚠️  SAFETY WARNING: Vehicle will be armed!")
    print("⚠️  Ensure NO propellers are attached during testing!")
    print()
    input("Press ENTER to continue or Ctrl+C to abort...")
    print()
    
    print("Attempting to arm vehicle...")
    if pixhawk.arm():
        print("✅ Vehicle armed successfully!")
        time.sleep(1)
        return True
    else:
        print("❌ Failed to arm vehicle")
        print("\nCOMMON ARMING FAILURES:")
        print("1. PRE-ARM: RC not calibrated")
        print("   Solution: Set ARMING_CHECK=0 in parameters (TESTING ONLY!)")
        print()
        print("2. PRE-ARM: Barometer not healthy")
        print("   Solution: Wait for sensors to calibrate, or disable checks")
        print()
        print("3. PRE-ARM: Compass not calibrated")
        print("   Solution: Calibrate compass in QGroundControl")
        print()
        print("4. PRE-ARM: GPS required but not present")
        print("   Solution: Set ARMING_CHECK to disable GPS check")
        print()
        print("5. Mode not armable")
        print("   Solution: Ensure mode is MANUAL or STABILIZE")
        print()
        print("BYPASS FOR TESTING (use with caution):")
        print("Connect to Pixhawk with QGroundControl and set:")
        print("  ARMING_CHECK = 0 (disables all pre-arm checks)")
        return False


def test_neutral_thrusters(pixhawk):
    """Test sending neutral thruster commands"""
    print("\n[STEP 4] Testing Neutral Thruster Commands")
    print("-" * 70)
    
    neutral = [1500] * 8
    print(f"Sending neutral PWM to all 8 thrusters: {neutral}")
    
    # Try multiple times with connection check
    for attempt in range(3):
        # Check/restore connection
        if not pixhawk.connected:
            print(f"[ATTEMPT {attempt+1}] Checking connection...")
            pixhawk.check_connection()
            time.sleep(0.5)
        
        success = pixhawk.send_rc_channels_override(neutral)
        if success:
            print("✅ Neutral commands sent successfully")
            time.sleep(2)
            return True
        else:
            if attempt < 2:
                print(f"⚠️  Attempt {attempt+1} failed, retrying...")
                time.sleep(1)
            else:
                print("❌ Failed to send neutral commands after 3 attempts")
                return False
    
    return False


def test_individual_thrusters(pixhawk):
    """Test each thruster individually"""
    print("\n[STEP 5] Testing Individual Thrusters")
    print("-" * 70)
    print("⚠️  Testing each thruster at LOW power (1600 PWM)")
    print("⚠️  Ensure propellers are REMOVED or ROV is in water!")
    print()
    input("Press ENTER to continue or Ctrl+C to abort...")
    print()
    
    test_pwm = 1600  # Low power forward
    test_duration = 2  # seconds
    
    for channel in range(1, 9):
        channels = [1500] * 8
        channels[channel - 1] = test_pwm
        
        print(f"Testing Channel {channel}... (PWM: {test_pwm})")
        
        # Ensure connection before each send
        pixhawk.check_connection()
        
        # Send command with retry
        for attempt in range(2):
            if pixhawk.send_rc_channels_override(channels):
                break
            elif attempt < 1:
                print(f"  Retry sending...")
                time.sleep(0.5)
        
        time.sleep(test_duration)
        
        # Return to neutral
        pixhawk.send_rc_channels_override([1500] * 8)
        time.sleep(0.5)
        print(f"  Channel {channel} test complete")
    
    print("\n✅ Individual thruster tests complete")
    print("\nDid you hear/see the thrusters spin?")
    response = input("(yes/no): ").strip().lower()
    
    return response in ['yes', 'y']


def test_all_thrusters_forward(pixhawk):
    """Test all thrusters forward simultaneously"""
    print("\n[STEP 6] Testing All Thrusters Forward")
    print("-" * 70)
    print("⚠️  Testing ALL thrusters at LOW power (1600 PWM)")
    print()
    input("Press ENTER to continue or Ctrl+C to abort...")
    print()
    
    forward = [1600] * 8  # All thrusters forward at low power
    
    print("Sending forward command to all thrusters...")
    pixhawk.send_rc_channels_override(forward)
    
    for countdown in range(3, 0, -1):
        print(f"  Running... {countdown}s")
        time.sleep(1)
    
    # Return to neutral
    pixhawk.send_rc_channels_override([1500] * 8)
    print("\n✅ All thrusters test complete")


def safe_disarm(pixhawk):
    """Safely disarm vehicle"""
    print("\n[STEP 7] Disarming Vehicle")
    print("-" * 70)
    
    # Return to neutral first
    pixhawk.send_rc_channels_override([1500] * 8)
    time.sleep(0.5)
    
    if pixhawk.disarm():
        print("✅ Vehicle disarmed safely")
    else:
        print("⚠️  Failed to disarm - may already be disarmed")


def main():
    """Main test procedure"""
    
    # Connection strings to try (in order)
    connection_options = [
        "tcp:raspberrypi.local:7000",  # MAVProxy TCP relay
        "/dev/ttyAMA0:57600",           # Direct GPIO UART (Pi)
        "/dev/ttyUSB0:115200",          # USB serial adapter
        "tcp:192.168.1.104:7000",       # Ethernet IP fallback
    ]
    
    print("Connection options:")
    for i, conn in enumerate(connection_options, 1):
        print(f"  {i}. {conn}")
    print()
    
    choice = input("Select connection (1-4) or enter custom string: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(connection_options):
        connection_string = connection_options[int(choice) - 1]
    else:
        connection_string = choice
    
    print()
    
    try:
        # Test connection
        pixhawk = test_connection(connection_string)
        if not pixhawk:
            sys.exit(1)
        
        # Test mode setting
        if not test_mode_setting(pixhawk):
            print("\n⚠️  Continuing anyway...")
        
        # Test arming
        if not test_arming(pixhawk):
            print("\n❌ Cannot continue without arming")
            print("\nRECOMMENDATION:")
            print("1. Use QGroundControl to check pre-arm failures")
            print("2. Set parameter ARMING_CHECK=0 for testing")
            print("3. Ensure mode is MANUAL")
            pixhawk.close()
            sys.exit(1)
        
        # Test neutral commands
        if not test_neutral_thrusters(pixhawk):
            print("⚠️  Warning: Neutral commands failed")
        
        # Test individual thrusters
        thrusters_work = test_individual_thrusters(pixhawk)
        
        if thrusters_work:
            # Test all thrusters together
            test_all_thrusters_forward(pixhawk)
        else:
            print("\n❌ THRUSTER PROBLEM DETECTED")
            print("\nTROUBLESHOOTING:")
            print("1. Check ESC connections to Pixhawk")
            print("2. Verify ESC power supply (11.1-14.8V)")
            print("3. Check if ESCs are initialized (beep sequence)")
            print("4. Verify servo outputs are enabled in ArduSub")
            print("5. Check if SERVO functions are assigned:")
            print("   SERVO1_FUNCTION = 33 (Motor1)")
            print("   SERVO2_FUNCTION = 34 (Motor2)")
            print("   ... etc up to Motor8")
        
        # Disarm
        safe_disarm(pixhawk)
        
        # Close connection
        pixhawk.close()
        
        print("\n" + "=" * 70)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 70)
        print()
        
        if thrusters_work:
            print("✅ THRUSTERS ARE WORKING!")
            print("\nYour thrusters are functioning correctly.")
            print("If they don't work in the main application, check:")
            print("1. Joystick is connected and detected")
            print("2. Application is armed before using joystick")
            print("3. Joystick axes are mapped correctly")
        else:
            print("❌ THRUSTERS NOT WORKING")
            print("\nPlease check the hardware connections and")
            print("ArduSub configuration parameters.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        if 'pixhawk' in locals():
            pixhawk.send_rc_channels_override([1500] * 8)
            pixhawk.disarm()
            pixhawk.close()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
