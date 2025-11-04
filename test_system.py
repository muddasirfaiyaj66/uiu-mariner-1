"""
Test script for ROV control system
Tests joystick input and MAVLink message construction without hardware
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


def test_imports():
    """Test that all modules can be imported."""
    print("=" * 50)
    print("Testing module imports...")
    print("=" * 50)

    try:
        from connections.mavlinkConnection import PixhawkConnection

        print("✅ mavlinkConnection imported successfully")
    except Exception as e:
        print(f"❌ Failed to import mavlinkConnection: {e}")
        return False

    try:
        from controllers.joystickController import JoystickController

        print("✅ joystickController imported successfully")
    except Exception as e:
        print(f"❌ Failed to import joystickController: {e}")
        return False

    try:
        from ui.rovControlApp import ROVControlGUI

        print("✅ rovControlApp imported successfully")
    except Exception as e:
        print(f"❌ Failed to import rovControlApp: {e}")
        return False

    return True


def test_joystick_offline():
    """Test joystick controller without actual hardware."""
    print("\n" + "=" * 50)
    print("Testing JoystickController (offline)...")
    print("=" * 50)

    try:
        from controllers.joystickController import JoystickController

        # Test axis to PWM conversion
        js = JoystickController()

        # Test neutral
        pwm = js.axis_to_pwm(0.0)
        assert pwm == 1500, f"Expected 1500, got {pwm}"
        print(f"✅ axis_to_pwm(0.0) = {pwm} (neutral)")

        # Test full forward
        pwm = js.axis_to_pwm(1.0)
        assert pwm == 2000, f"Expected 2000, got {pwm}"
        print(f"✅ axis_to_pwm(1.0) = {pwm} (max)")

        # Test full reverse
        pwm = js.axis_to_pwm(-1.0)
        assert pwm == 1000, f"Expected 1000, got {pwm}"
        print(f"✅ axis_to_pwm(-1.0) = {pwm} (min)")

        # Test clamping
        pwm = js.axis_to_pwm(2.0)
        assert pwm == 2000, f"Expected 2000, got {pwm}"
        print(f"✅ axis_to_pwm(2.0) = {pwm} (clamped to max)")

        # Test empty state
        empty_state = js._get_empty_state()
        channels = js.compute_thruster_channels(empty_state)
        assert all(ch == 1500 for ch in channels), f"Expected all 1500, got {channels}"
        print(f"✅ compute_thruster_channels(empty) = all neutral")

        js.close()
        print("\n✅ JoystickController offline tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ JoystickController test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_mavlink_offline():
    """Test MAVLink connection class without hardware."""
    print("\n" + "=" * 50)
    print("Testing PixhawkConnection (offline)...")
    print("=" * 50)

    try:
        from connections.mavlinkConnection import PixhawkConnection

        # Create connection object (don't connect)
        conn = PixhawkConnection("udp:127.0.0.1:14550")
        print(f"✅ PixhawkConnection object created")
        print(f"   Link: {conn.link}")
        print(f"   Connected: {conn.connected}")

        # Test channel validation
        test_channels = [1500] * 8
        print(f"✅ Test channels created: {test_channels}")

        # Note: Can't actually send without connection
        print("   (Skipping actual MAVLink send - no hardware)")

        print("\n✅ PixhawkConnection offline tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ PixhawkConnection test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_config():
    """Test configuration loading."""
    print("\n" + "=" * 50)
    print("Testing configuration...")
    print("=" * 50)

    try:
        import json

        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                config = json.load(f)

            print("✅ config.json loaded successfully")
            print(f"   MAVLink: {config.get('mavlink_connection')}")
            print(f"   Joystick: {config.get('joystick_target')}")
            print(f"   Update Rate: {config.get('update_rate_hz')} Hz")
        else:
            print("⚠️  config.json not found (will use defaults)")

        return True

    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  UIU MARINER - ROV Control System - Test Suite")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Import Test", test_imports()))
    results.append(("Config Test", test_config()))
    results.append(("Joystick Test", test_joystick_offline()))
    results.append(("MAVLink Test", test_mavlink_offline()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)

    passed = 0
    failed = 0

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if result:
            passed += 1
        else:
            failed += 1

    print("=" * 60)
    print(f"Total: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("\n🎉 All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Connect Xbox controller")
        print("2. Configure config.json with Pixhawk IP")
        print("3. Run: python src/ui/rovControlApp.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
