#!/usr/bin/env python3
"""
Test Controller - Display Joystick Values in Real-Time
Shows all axes and button states for your Nintendo Switch Pro Controller
"""

import pygame
import sys
import time


def main():
    # Initialize pygame
    pygame.init()
    pygame.joystick.init()

    print("=" * 60)
    print("🎮 CONTROLLER TEST - Real-Time Values")
    print("=" * 60)
    print()

    # Check for joysticks
    joystick_count = pygame.joystick.get_count()

    if joystick_count == 0:
        print("❌ No controllers detected!")
        print("   Please connect your controller and try again.")
        pygame.quit()
        sys.exit(1)

    # List all detected joysticks
    print(f"✅ Found {joystick_count} controller(s):")
    for i in range(joystick_count):
        joy = pygame.joystick.Joystick(i)
        print(f"   [{i}] {joy.get_name()}")
    print()

    # Connect to first joystick
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"🎮 Connected to: {joystick.get_name()}")
    print(f"   Axes: {joystick.get_numaxes()}")
    print(f"   Buttons: {joystick.get_numbuttons()}")
    print(f"   Hats: {joystick.get_numhats()}")
    print()
    print("=" * 60)
    print("📊 LIVE VALUES (Press Ctrl+C to exit)")
    print("=" * 60)
    print()

    try:
        while True:
            # Process events
            pygame.event.pump()

            # Clear screen (move cursor to top)
            print("\033[2J\033[H", end="")

            print("=" * 60)
            print(f"🎮 {joystick.get_name()}")
            print("=" * 60)
            print()

            # Display axes
            print("📊 AXES (Joysticks):")
            print("-" * 60)
            axis_names = [
                "Left Stick X  (horizontal)",
                "Left Stick Y  (vertical)",
                "Right Stick X (horizontal)",
                "Right Stick Y (vertical)",
                "Left Trigger  (L2/ZL)",
                "Right Trigger (R2/ZR)",
            ]

            for i in range(min(joystick.get_numaxes(), len(axis_names))):
                value = joystick.get_axis(i)
                bar_length = int(abs(value) * 20)
                bar = "█" * bar_length
                direction = "→" if value > 0 else "←" if value < 0 else "•"

                print(
                    f"  Axis {i} ({axis_names[i] if i < len(axis_names) else 'Axis ' + str(i)})"
                )
                print(f"    Value: {value:+.3f}  {direction} {bar}")

            print()

            # Display buttons
            print("🔘 BUTTONS:")
            print("-" * 60)
            button_names = [
                "B (East)",
                "A (South)",
                "Y (West)",
                "X (North)",
                "L (L1)",
                "R (R1)",
                "ZL (L2)",
                "ZR (R2)",
                "Minus (-)",
                "Plus (+)",
                "Left Stick",
                "Right Stick",
                "Home",
                "Capture",
                "?",
                "?",
            ]

            pressed_buttons = []
            for i in range(joystick.get_numbuttons()):
                if joystick.get_button(i):
                    btn_name = (
                        button_names[i] if i < len(button_names) else f"Button {i}"
                    )
                    pressed_buttons.append(f"[{i}] {btn_name}")

            if pressed_buttons:
                print("  PRESSED: " + ", ".join(pressed_buttons))
            else:
                print("  (No buttons pressed)")

            print()

            # Display D-Pad (Hat)
            if joystick.get_numhats() > 0:
                print("🎯 D-PAD:")
                print("-" * 60)
                hat = joystick.get_hat(0)
                dpad_state = []
                if hat[1] == 1:
                    dpad_state.append("UP")
                elif hat[1] == -1:
                    dpad_state.append("DOWN")
                if hat[0] == 1:
                    dpad_state.append("RIGHT")
                elif hat[0] == -1:
                    dpad_state.append("LEFT")

                if dpad_state:
                    print(f"  {' + '.join(dpad_state)}")
                else:
                    print("  (Centered)")
                print()

            print("=" * 60)
            print("💡 TIP: Move joysticks and press buttons to see values")
            print("   Press Ctrl+C to exit")
            print("=" * 60)

            # Delay for comfortable reading speed
            time.sleep(0.5)  # 2 Hz update rate (slower for better readability)

    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("✅ Controller test stopped")
        print("=" * 60)
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
