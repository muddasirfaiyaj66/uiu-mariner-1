#!/usr/bin/env python3
"""
Quick Thruster Check - Verify joystick → PWM → Pixhawk flow
Simple visual test to confirm your thruster control is working
"""

import pygame
import sys
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

print("=" * 70)
print("🎮 QUICK THRUSTER CHECK - UIU MARINER")
print("=" * 70)
print()

# Step 1: Check joystick
print("📌 Step 1: Checking Joystick...")
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("❌ No joystick detected!")
    print("   - Connect your controller via USB")
    print("   - Check Windows Device Manager")
    sys.exit(1)

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"✅ Found: {joystick.get_name()}")
print(f"   Axes: {joystick.get_numaxes()}, Buttons: {joystick.get_numbuttons()}")
print()

# Step 2: Test axis reading
print("📌 Step 2: Testing Axis Reading...")
print("   Move LEFT STICK forward/backward...")
print("   Move RIGHT STICK up/down...")
print()

# Deadzone
DEADZONE = 0.03


def axis_to_pwm(value):
    """Convert -1.0...1.0 to PWM 1000-2000"""
    if abs(value) < DEADZONE:
        return 1500
    pwm = 1500 + int(value * 500)
    return max(1000, min(2000, pwm))


print("Press SPACE to start test, ESC to quit")
running = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                running = True
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit(0)

    if running:
        break
    time.sleep(0.1)

print()
print("🚀 LIVE THRUSTER VALUES (Press ESC to stop)")
print("=" * 70)
print()
print("┌" + "─" * 68 + "┐")
print("│ Joystick Input             PWM Values (μs)                         │")
print("├" + "─" * 68 + "┤")
print("│ Stick    │ Value  │ Ch1  │ Ch2  │ Ch3  │ Ch4  │ Ch5  │ Ch6  │ Ch7  │ Ch8  │")
print("├" + "─" * 68 + "┤")

running = True
last_update = time.time()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.QUIT:
            running = False

    # Update pygame
    pygame.event.pump()

    # Read axes
    left_y = joystick.get_axis(1)  # Forward/backward
    left_x = joystick.get_axis(0)  # Left/right
    right_y = joystick.get_axis(4)  # Up/down
    right_x = joystick.get_axis(3)  # Not used

    # Convert to thruster channels
    channels = [1500] * 8

    # Forward/Backward (Ch1, Ch8)
    if abs(left_y) > DEADZONE:
        forward_back = -left_y  # Invert
        channels[0] = axis_to_pwm(forward_back)
        channels[7] = axis_to_pwm(-forward_back)

    # Left/Right (Ch2, Ch5)
    if abs(left_x) > DEADZONE:
        channels[1] = axis_to_pwm(left_x)
        channels[4] = axis_to_pwm(-left_x)

    # Up/Down (Ch3, Ch4, Ch6, Ch7)
    if abs(right_y) > DEADZONE:
        up_down = -right_y  # Invert
        channels[2] = axis_to_pwm(-up_down)
        channels[3] = axis_to_pwm(-up_down)
        channels[5] = axis_to_pwm(up_down)
        channels[6] = axis_to_pwm(up_down)

    # Display every 0.2s
    if time.time() - last_update > 0.2:
        # Left stick line
        print(
            f"│ Left  Y  │ {left_y:+.2f}  │ {channels[0]:4d} │ {channels[1]:4d} │ .... │ .... │ {channels[4]:4d} │ .... │ .... │ {channels[7]:4d} │"
        )

        # Right stick line
        print(
            f"│ Right Y  │ {right_y:+.2f}  │ .... │ .... │ {channels[2]:4d} │ {channels[3]:4d} │ .... │ {channels[5]:4d} │ {channels[6]:4d} │ .... │"
        )

        # Separator
        print("│" + " " * 68 + "│")

        last_update = time.time()

    time.sleep(0.05)

print("└" + "─" * 68 + "┘")
print()
print("=" * 70)
print("✅ Joystick Test Complete")
print()
print("📌 What You Should See:")
print("   ✓ When you move sticks, PWM values change (1000-2000)")
print("   ✓ Neutral position = 1500μs")
print("   ✓ Full forward/up = 2000μs")
print("   ✓ Full backward/down = 1000μs")
print()
print("📌 Next Steps:")
print("   1. If values change → Joystick is working! ✅")
print("   2. Run: python test_thruster_dataflow.py")
print("      (This will test sending to Pixhawk)")
print("   3. Run: python launch_mariner.py")
print("      (Launch full application)")
print()
print("=" * 70)

pygame.quit()
