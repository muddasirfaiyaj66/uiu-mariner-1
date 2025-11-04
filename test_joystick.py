"""
Quick test script to verify joystick/gamepad detection and input.
Run this to test your Nintendo Switch Pro Controller or any gamepad.
"""

import pygame
import sys
import time


def test_joystick():
    """Test joystick detection and input."""
    print("=" * 60)
    print("JOYSTICK TEST - UIU MARINER")
    print("=" * 60)

    # Initialize pygame
    pygame.init()
    pygame.joystick.init()

    # Check for joysticks
    joystick_count = pygame.joystick.get_count()
    print(f"\n✅ Found {joystick_count} joystick(s)")

    if joystick_count == 0:
        print("❌ No joystick detected!")
        print("\nTroubleshooting:")
        print("  1. Make sure your controller is connected via USB or Bluetooth")
        print("  2. Check Windows Device Manager to see if it's recognized")
        print("  3. Try pressing buttons on the controller")
        return

    # List all joysticks
    print("\n" + "=" * 60)
    print("DETECTED CONTROLLERS:")
    print("=" * 60)

    for i in range(joystick_count):
        js = pygame.joystick.Joystick(i)
        js.init()
        print(f"\nController {i}:")
        print(f"  Name: {js.get_name()}")
        print(f"  Axes: {js.get_numaxes()}")
        print(f"  Buttons: {js.get_numbuttons()}")
        print(f"  Hats: {js.get_numhats()}")

    # Use first joystick for testing
    print("\n" + "=" * 60)
    print("TESTING FIRST CONTROLLER")
    print("=" * 60)

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"\n✅ Connected to: {joystick.get_name()}")
    print("\n📋 Instructions:")
    print("  - Move the analog sticks")
    print("  - Press buttons")
    print("  - Press Ctrl+C to exit")
    print("\nReading inputs (updates every 0.5 seconds)...\n")

    try:
        while True:
            pygame.event.pump()

            # Read axes
            print("\n" + "-" * 60)
            print("AXES (Analog Sticks & Triggers):")
            for i in range(joystick.get_numaxes()):
                value = joystick.get_axis(i)
                bar = "█" * int(abs(value) * 20)
                sign = "+" if value >= 0 else "-"
                print(f"  Axis {i}: {sign}{bar:<20} ({value:+.3f})")

            # Read buttons
            pressed_buttons = []
            for i in range(joystick.get_numbuttons()):
                if joystick.get_button(i):
                    pressed_buttons.append(i)

            if pressed_buttons:
                print(f"\nBUTTONS PRESSED: {pressed_buttons}")
            else:
                print("\nBUTTONS: None pressed")

            # Read hat (D-pad)
            if joystick.get_numhats() > 0:
                hat = joystick.get_hat(0)
                if hat != (0, 0):
                    print(f"D-PAD: {hat}")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\n✅ Test completed!")
        print("=" * 60)
        print("Your controller is working correctly!")
        print("You can now use it with the Mariner ROV Control System.")
        print("=" * 60)


if __name__ == "__main__":
    test_joystick()
