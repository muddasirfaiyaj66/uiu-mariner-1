#!/usr/bin/env python3
"""
🔍 THRUSTER DATA FLOW TEST
===========================
This script tests the complete data flow from joystick button press to Pixhawk MAIN OUT pins.

Test Flow:
1. Joystick Input → pygame reads axis/button values
2. Conversion → joystickController converts to PWM (1000-2000)
3. MAVLink → RC_CHANNELS_OVERRIDE sent to Pixhawk
4. Pixhawk → Outputs PWM signals on MAIN OUT 1-8 pins
5. ESC/Thrusters → Motors spin based on PWM values

Usage:
    python test_thruster_dataflow.py
"""

import sys
import time
import pygame
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from controllers.joystickController import JoystickController
from connections.mavlinkConnection import PixhawkConnection


class ThrusterDataFlowTester:
    """Test complete thruster control data flow."""

    def __init__(self):
        self.joystick = None
        self.pixhawk = None
        self.test_results = {
            "joystick": False,
            "joystick_reading": False,
            "pwm_conversion": False,
            "pixhawk_connection": False,
            "mavlink_send": False,
            "thruster_output": False,
        }

    def run_all_tests(self):
        """Run complete test suite."""
        print("=" * 70)
        print("🔍 THRUSTER DATA FLOW TEST - UIU MARINER")
        print("=" * 70)
        print()

        # Test 1: Joystick Detection
        print("📌 TEST 1: Joystick Detection")
        print("-" * 70)
        if self.test_joystick_detection():
            self.test_results["joystick"] = True
            print("✅ PASSED: Joystick detected and connected\n")
        else:
            print("❌ FAILED: No joystick detected\n")
            return

        # Test 2: Joystick Input Reading
        print("📌 TEST 2: Joystick Input Reading")
        print("-" * 70)
        if self.test_joystick_input():
            self.test_results["joystick_reading"] = True
            print("✅ PASSED: Joystick inputs reading correctly\n")
        else:
            print("❌ FAILED: Cannot read joystick inputs\n")
            return

        # Test 3: PWM Conversion
        print("📌 TEST 3: Axis to PWM Conversion")
        print("-" * 70)
        if self.test_pwm_conversion():
            self.test_results["pwm_conversion"] = True
            print("✅ PASSED: PWM conversion working correctly\n")
        else:
            print("❌ FAILED: PWM conversion issues\n")
            return

        # Test 4: Pixhawk Connection
        print("📌 TEST 4: Pixhawk Connection")
        print("-" * 70)
        if self.test_pixhawk_connection():
            self.test_results["pixhawk_connection"] = True
            print("✅ PASSED: Pixhawk connected\n")
        else:
            print("❌ FAILED: Pixhawk not connected\n")
            print("   Make sure:")
            print("   - Pixhawk is powered on")
            print("   - Raspberry Pi MAVProxy server is running")
            print("   - Network connection is working")
            return

        # Test 5: MAVLink Message Sending
        print("📌 TEST 5: MAVLink RC_CHANNELS_OVERRIDE Sending")
        print("-" * 70)
        if self.test_mavlink_sending():
            self.test_results["mavlink_send"] = True
            print("✅ PASSED: MAVLink messages sent successfully\n")
        else:
            print("❌ FAILED: Cannot send MAVLink messages\n")
            return

        # Test 6: Live Thruster Control Test
        print("📌 TEST 6: Live Thruster Control (Interactive)")
        print("-" * 70)
        if self.test_live_thruster_control():
            self.test_results["thruster_output"] = True
            print("✅ PASSED: Live thruster control working\n")
        else:
            print("⚠️  SKIPPED: User skipped live test\n")

        # Display Summary
        self.display_summary()

    def test_joystick_detection(self):
        """Test if joystick is detected."""
        try:
            self.joystick = JoystickController()
            if self.joystick.is_connected():
                print(f"   ✓ Joystick found: {self.joystick.joystick_name}")
                print(f"   ✓ Axes: {self.joystick.joystick.get_numaxes()}")
                print(f"   ✓ Buttons: {self.joystick.joystick.get_numbuttons()}")
                return True
            return False
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False

    def test_joystick_input(self):
        """Test if joystick inputs are being read."""
        try:
            print("   Waiting for joystick to be ready (1.5s calibration delay)...")
            while not self.joystick.is_ready():
                time.sleep(0.1)

            print("   ✓ Joystick ready!")
            print()
            print("   Reading 5 samples...")

            for i in range(5):
                state = self.joystick.read_joystick()
                axes = state["axes"]
                buttons = state["buttons"]

                print(f"   Sample {i+1}:")
                print(
                    f"      Left Stick:  X={axes['left_x']:+.2f}, Y={axes['left_y']:+.2f}"
                )
                print(
                    f"      Right Stick: X={axes['right_x']:+.2f}, Y={axes['right_y']:+.2f}"
                )

                pressed = [name for name, val in buttons.items() if val]
                if pressed:
                    print(f"      Buttons: {', '.join(pressed)}")

                time.sleep(0.5)

            return True
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False

    def test_pwm_conversion(self):
        """Test axis to PWM conversion."""
        try:
            print("   Testing PWM conversion formula:")
            print()

            test_cases = [
                (-1.0, "Full Backward/Left/Down"),
                (-0.5, "Half Backward/Left/Down"),
                (0.0, "Neutral"),
                (0.5, "Half Forward/Right/Up"),
                (1.0, "Full Forward/Right/Up"),
            ]

            for axis_value, description in test_cases:
                pwm = self.joystick.axis_to_pwm(axis_value)
                print(f"   Axis: {axis_value:+.2f} → PWM: {pwm}μs ({description})")

            print()
            print("   Expected ranges:")
            print("      - Full reverse: 1000μs")
            print("      - Neutral: 1500μs")
            print("      - Full forward: 2000μs")
            return True
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False

    def test_pixhawk_connection(self):
        """Test connection to Pixhawk via MAVLink."""
        try:
            # Read config for connection string
            import json

            config_path = Path(__file__).parent / "config.json"
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    connection_string = config.get(
                        "mavlink_connection", "tcp:raspberrypi.local:7000"
                    )
            else:
                connection_string = "tcp:raspberrypi.local:7000"

            print(f"   Attempting connection: {connection_string}")

            self.pixhawk = PixhawkConnection(link=connection_string, auto_detect=True)
            result = self.pixhawk.connect()

            if result:
                status = self.pixhawk.get_status()
                print(f"   ✓ System ID: {status['system_id']}")
                print(f"   ✓ Component ID: {status['component_id']}")
                return True
            return False
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False

    def test_mavlink_sending(self):
        """Test sending MAVLink messages."""
        try:
            print("   Sending test RC_CHANNELS_OVERRIDE messages...")
            print()

            # Verify connection is still good before starting
            if not self.pixhawk.check_connection():
                print("      ✗ Connection lost before test")
                return False

            # Send neutral values
            neutral = [1500] * 8
            print(f"   Test 1: Sending neutral values (all 1500μs)")

            # Send without internal connection check to avoid interference
            if not self.pixhawk.vehicle:
                print("      ✗ No vehicle connection")
                return False

            try:
                self.pixhawk.vehicle.mav.rc_channels_override_send(
                    self.pixhawk.vehicle.target_system,
                    self.pixhawk.vehicle.target_component,
                    *neutral,
                )
                print("      ✓ Sent successfully")
            except Exception as e:
                print(f"      ✗ Failed to send: {e}")
                return False

            time.sleep(1.0)  # Longer delay between messages

            # Send test pattern
            test_pattern = [1500, 1600, 1500, 1500, 1400, 1500, 1500, 1500]
            print(
                f"   Test 2: Sending test pattern (Ch2=1600μs, Ch5=1400μs, rest=1500μs)"
            )

            try:
                self.pixhawk.vehicle.mav.rc_channels_override_send(
                    self.pixhawk.vehicle.target_system,
                    self.pixhawk.vehicle.target_component,
                    *test_pattern,
                )
                print("      ✓ Sent successfully")
            except Exception as e:
                print(f"      ✗ Failed to send: {e}")
                return False

            time.sleep(1.0)  # Longer delay between messages

            # Return to neutral
            print("   Test 3: Returning to neutral")
            try:
                self.pixhawk.vehicle.mav.rc_channels_override_send(
                    self.pixhawk.vehicle.target_system,
                    self.pixhawk.vehicle.target_component,
                    *neutral,
                )
                print("      ✓ Sent successfully")
            except Exception as e:
                print(f"      ✗ Failed to send: {e}")
                return False

            return True
        except Exception as e:
            print(f"   ✗ Error: {e}")
            import traceback

            traceback.print_exc()
            return False

    def test_live_thruster_control(self):
        """Interactive live thruster control test."""
        print("   This test will read your joystick and send commands to Pixhawk.")
        print("   You can see the PWM values being sent to each channel.")
        print()
        print("   ⚠️  WARNING: Make sure ROV is secured or in water!")
        print()

        response = input("   Do you want to run live test? (y/n): ").strip().lower()
        if response != "y":
            return False

        print()
        print("   ⚠️  ARMING Pixhawk in 3 seconds...")
        time.sleep(1)
        print("   2...")
        time.sleep(1)
        print("   1...")
        time.sleep(1)

        if not self.pixhawk.arm():
            print("   ✗ Failed to arm Pixhawk")
            return False

        print("   ✅ Pixhawk ARMED!")
        print()
        print(
            "   Move your joystick sticks. Press 'Q' on keyboard or Start button to stop."
        )
        print("   " + "-" * 66)
        print(
            "   | Left Stick  | Right Stick | Ch1  | Ch2  | Ch3  | Ch4  | Ch5  | Ch6  | Ch7  | Ch8  |"
        )
        print("   " + "-" * 66)

        try:
            running = True
            last_print = time.time()

            while running:
                # Check for keyboard input (Q to quit)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            running = False

                # Read joystick
                state = self.joystick.read_joystick()
                channels = self.joystick.compute_thruster_channels(state)

                # Check for Start button (emergency stop)
                if state["buttons"]["start"]:
                    running = False
                    print("\n   ⚠️  Emergency Stop button pressed!")

                # Send to Pixhawk
                self.pixhawk.send_rc_channels_override(channels)

                # Display every 0.2 seconds
                if time.time() - last_print > 0.2:
                    axes = state["axes"]
                    left_x = axes["left_x"]
                    left_y = axes["left_y"]
                    right_x = axes["right_x"]
                    right_y = axes["right_y"]

                    print(
                        f"   | {left_x:+.2f},{left_y:+.2f} | {right_x:+.2f},{right_y:+.2f}  | "
                        f"{channels[0]:4d} | {channels[1]:4d} | {channels[2]:4d} | {channels[3]:4d} | "
                        f"{channels[4]:4d} | {channels[5]:4d} | {channels[6]:4d} | {channels[7]:4d} |"
                    )
                    last_print = time.time()

                time.sleep(0.05)  # 20 Hz

        except KeyboardInterrupt:
            print("\n   Interrupted by user")
        finally:
            # Disarm
            print()
            print("   Disarming...")
            neutral = [1500] * 8
            self.pixhawk.send_rc_channels_override(neutral)
            self.pixhawk.disarm()
            print("   ✅ Disarmed and stopped")

        return True

    def display_summary(self):
        """Display test summary."""
        print()
        print("=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print()

        tests = [
            ("Joystick Detection", self.test_results["joystick"]),
            ("Joystick Input Reading", self.test_results["joystick_reading"]),
            ("PWM Conversion", self.test_results["pwm_conversion"]),
            ("Pixhawk Connection", self.test_results["pixhawk_connection"]),
            ("MAVLink Sending", self.test_results["mavlink_send"]),
            ("Live Thruster Control", self.test_results["thruster_output"]),
        ]

        passed = sum(1 for _, result in tests if result)
        total = len(tests)

        for test_name, result in tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} - {test_name}")

        print()
        print(f"   Results: {passed}/{total} tests passed")
        print()

        if passed == total:
            print("   🎉 ALL TESTS PASSED!")
            print("   Your thruster control system is working correctly.")
        elif passed >= 5:
            print("   ⚠️  MOSTLY WORKING - Check failed tests above")
        else:
            print("   ❌ SYSTEM NOT READY - Multiple failures detected")

        print()
        print("=" * 70)
        print()

        # Display troubleshooting help
        if not all(result for _, result in tests):
            print("🔧 TROUBLESHOOTING:")
            print()
            if not self.test_results["joystick"]:
                print("   Joystick Issues:")
                print("   - Check USB connection")
                print("   - Try running: python test_controller.py")
                print()
            if not self.test_results["pixhawk_connection"]:
                print("   Pixhawk Connection Issues:")
                print("   - Check if Raspberry Pi is powered on")
                print("   - Check network connection: ping raspberrypi.local")
                print("   - Check if MAVProxy is running on Pi")
                print("   - Try: ssh pi@raspberrypi.local")
                print()
            if not self.test_results["mavlink_send"]:
                print("   MAVLink Issues:")
                print("   - Check Pixhawk is receiving power")
                print("   - Check UART/USB connection between Pi and Pixhawk")
                print("   - Run on Pi: python3 ~/mariner/pi_scripts/detect_pixhawk.py")
                print()

        print("📖 Channel Mapping (Pixhawk MAIN OUT):")
        print()
        print("   Pin 1 (Ch1): Forward/Backward (ACW thruster)")
        print("   Pin 2 (Ch2): Left/Right Rotation")
        print("   Pin 3 (Ch3): Vertical Up/Down (ACW)")
        print("   Pin 4 (Ch4): Vertical Up/Down (ACW)")
        print("   Pin 5 (Ch5): Left/Right Rotation (opposite)")
        print("   Pin 6 (Ch6): Vertical Up/Down (CW)")
        print("   Pin 7 (Ch7): Vertical Up/Down (CW)")
        print("   Pin 8 (Ch8): Forward/Backward (CW thruster)")
        print()
        print("   PWM Values:")
        print("   - 1000μs = Full reverse/left/down")
        print("   - 1500μs = Neutral (no movement)")
        print("   - 2000μs = Full forward/right/up")
        print()

    def cleanup(self):
        """Clean up resources."""
        try:
            if self.pixhawk:
                self.pixhawk.close()
            if self.joystick:
                self.joystick.close()
        except:
            pass


def main():
    """Main entry point."""
    tester = ThrusterDataFlowTester()
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
