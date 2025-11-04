"""
Joystick Controller for ROV
Reads Xbox 360 / compatible gamepad input and converts to thruster PWM values.
"""

import pygame
import time
from typing import List, Dict, Optional


class JoystickController:
    """
    Handles joystick input and converts axes/buttons to 8-channel thruster commands.
    """

    # Dead zone for analog sticks (ignore small movements)
    DEADZONE = 0.03

    # PWM range
    PWM_MIN = 1000
    PWM_NEUTRAL = 1500
    PWM_MAX = 2000

    def __init__(self, joystick_index=0, target_name=None):
        """
        Initialize joystick controller.

        Args:
            joystick_index: Index of joystick to use (default 0)
            target_name: Optional filter for joystick name (e.g., "Xbox")
        """
        pygame.init()
        pygame.joystick.init()

        self.joystick = None
        self.joystick_name = "Not Connected"
        self.last_read_time = time.time()
        self.ready_time = time.time() + 1.5  # Calibration delay

        self._connect_joystick(joystick_index, target_name)

    def _connect_joystick(self, joystick_index, target_name):
        """Find and connect to joystick."""
        joystick_count = pygame.joystick.get_count()

        if joystick_count == 0:
            print("❌ No joystick detected")
            return False

        # List all detected joysticks
        print(f"[JOYSTICK] Found {joystick_count} joystick(s)")

        # If target name is specified, search for matching joystick
        if target_name:
            found = False
            for i in range(joystick_count):
                js = pygame.joystick.Joystick(i)
                js.init()
                name = js.get_name()
                print(f"[JOYSTICK] {i}: {name}")

                if not found and target_name.lower() in name.lower():
                    self.joystick = js
                    self.joystick_name = name
                    print(f"[JOYSTICK] ✅ Matched target '{target_name}' → {name}")
                    found = True
                else:
                    js.quit()

            if not found:
                print(
                    f"[JOYSTICK] ⚠️ Target '{target_name}' not found, using first available"
                )
                # Fall back to first joystick
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.joystick_name = self.joystick.get_name()
                print(f"[JOYSTICK] ✅ Connected to: {self.joystick_name}")
                return True
            return True
        else:
            # Use first available joystick
            self.joystick = pygame.joystick.Joystick(joystick_index)
            self.joystick.init()
            self.joystick_name = self.joystick.get_name()
            print(f"[JOYSTICK] ✅ Connected to: {self.joystick_name}")
            return True

    def is_connected(self) -> bool:
        """Check if joystick is connected."""
        return self.joystick is not None

    def is_ready(self) -> bool:
        """Check if joystick has passed calibration delay."""
        return self.is_connected() and time.time() >= self.ready_time

    def get_axis_value(self, axis_index: int, invert=False) -> float:
        """
        Get axis value with deadzone applied.

        Args:
            axis_index: Axis number (0-5 typically)
            invert: If True, multiply by -1

        Returns:
            Value from -1.0 to 1.0, or 0.0 if in deadzone
        """
        if not self.joystick:
            return 0.0

        try:
            value = self.joystick.get_axis(axis_index)
            if invert:
                value = -value

            # Apply deadzone
            if abs(value) < self.DEADZONE:
                return 0.0
            return value
        except:
            return 0.0

    def get_button(self, button_index: int) -> bool:
        """Get button state (True if pressed)."""
        if not self.joystick:
            return False

        try:
            return self.joystick.get_button(button_index)
        except:
            return False

    def get_hat(self, hat_index: int = 0) -> tuple:
        """
        Get D-pad (hat) state.
        Returns: (x, y) where:
            x: -1 (left), 0 (center), 1 (right)
            y: -1 (down), 0 (center), 1 (up)
        """
        if not self.joystick:
            return (0, 0)

        try:
            return self.joystick.get_hat(hat_index)
        except:
            return (0, 0)

    def axis_to_pwm(self, axis_value: float, reverse=False) -> int:
        """
        Convert axis value (-1.0 to 1.0) to PWM (1000-2000).

        Args:
            axis_value: Input from -1.0 to 1.0
            reverse: If True, invert the mapping

        Returns:
            PWM value (1000-2000), 1500 is neutral
        """
        if reverse:
            axis_value = -axis_value

        # Map -1.0...1.0 → 1000...2000
        pwm = self.PWM_NEUTRAL + int(axis_value * 500)
        return max(self.PWM_MIN, min(self.PWM_MAX, pwm))

    def read_joystick(self) -> Dict[str, any]:
        """
        Read all joystick inputs and return structured data.

        Returns:
            Dictionary with:
                - axes: Dict of axis names → values (-1.0 to 1.0)
                - buttons: Dict of button names → bool
                - hat: Tuple (x, y)
                - timestamp: Time of reading
        """
        if not self.is_ready():
            return self._get_empty_state()

        # Update pygame event queue
        pygame.event.pump()

        # Read axes - Auto-detect controller type
        # Nintendo Switch Pro Controller uses different axis mapping
        controller_name = self.joystick_name.lower()

        if "switch" in controller_name:
            # Nintendo Switch Pro Controller mapping
            axes = {
                "left_x": self.get_axis_value(0),  # Left stick horizontal
                "left_y": self.get_axis_value(1),  # Left stick vertical
                "right_x": self.get_axis_value(2),  # Right stick horizontal
                "right_y": self.get_axis_value(3),  # Right stick vertical
                "left_trigger": self.get_axis_value(4),  # ZL
                "right_trigger": self.get_axis_value(5),  # ZR
            }
        else:
            # Xbox 360 / Standard gamepad layout
            axes = {
                "left_x": self.get_axis_value(0),  # Left stick horizontal
                "left_y": self.get_axis_value(1),  # Left stick vertical
                "right_x": self.get_axis_value(3),  # Right stick horizontal
                "right_y": self.get_axis_value(4),  # Right stick vertical
                "left_trigger": self.get_axis_value(2),  # LT
                "right_trigger": self.get_axis_value(5),  # RT
            }

        # Read buttons (Xbox 360 standard layout)
        buttons = {
            "a": self.get_button(0),
            "b": self.get_button(1),
            "x": self.get_button(2),
            "y": self.get_button(3),
            "lb": self.get_button(4),
            "rb": self.get_button(5),
            "back": self.get_button(6),
            "start": self.get_button(7),
            "left_stick": self.get_button(8),
            "right_stick": self.get_button(9),
        }

        # Read D-pad
        hat = self.get_hat(0)

        self.last_read_time = time.time()

        return {
            "axes": axes,
            "buttons": buttons,
            "hat": hat,
            "timestamp": self.last_read_time,
        }

    def _get_empty_state(self) -> Dict[str, any]:
        """Return empty state when joystick not ready."""
        return {
            "axes": {
                k: 0.0
                for k in [
                    "left_x",
                    "left_y",
                    "right_x",
                    "right_y",
                    "left_trigger",
                    "right_trigger",
                ]
            },
            "buttons": {
                k: False
                for k in [
                    "a",
                    "b",
                    "x",
                    "y",
                    "lb",
                    "rb",
                    "back",
                    "start",
                    "left_stick",
                    "right_stick",
                ]
            },
            "hat": (0, 0),
            "timestamp": time.time(),
        }

    def compute_thruster_channels(self, joystick_state: Dict) -> List[int]:
        """
        Convert joystick state to 8-channel thruster PWM values.

        Based on the control.py logic from the reference repo:
            - Left stick Y: Forward/Backward (channels 1, 8)
            - Left stick X: Left/Right rotation (channels 2, 5)
            - Right stick Y: Up/Down (channels 3, 4, 6, 7)

        Args:
            joystick_state: Output from read_joystick()

        Returns:
            List of 8 PWM values [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8]
        """
        axes = joystick_state["axes"]
        buttons = joystick_state["buttons"]

        # Initialize all channels to neutral
        channels = [self.PWM_NEUTRAL] * 8

        # DEBUG (rate-limited): Raw axis values (avoid spamming console which can block)
        if not hasattr(self, "_last_axes_log_time"):
            self._last_axes_log_time = 0.0
        if time.time() - self._last_axes_log_time > 1.0:  # log at most once per second
            try:
                num_axes = self.joystick.get_numaxes()
                raw_axes = [self.joystick.get_axis(i) for i in range(num_axes)]
                if any(abs(val) > 0.1 for val in raw_axes):  # only log meaningful movement
                    axes_str = ", ".join(
                        [f"Axis{i}={raw_axes[i]:.2f}" for i in range(num_axes)]
                    )
                    print(f"[DEBUG] RAW AXES: {axes_str}")
            except Exception:
                pass
            self._last_axes_log_time = time.time()

        # Extract axis values
        forward_back = -axes["left_y"]  # Invert Y axis (forward is negative)
        left_right = axes["left_x"]
        up_down = -axes["right_y"]  # Invert Y axis

        # Forward/Backward (Channels 1 and 8)
        # From reference: axis_1 < 0 → forward, axis_1 > 0 → backward
        if abs(forward_back) > self.DEADZONE:
            value = self.axis_to_pwm(forward_back)
            reverse_value = self.axis_to_pwm(-forward_back)
            channels[0] = value  # Ch1: ACW for forward
            channels[7] = reverse_value  # Ch8: CW for forward
            # Reduce verbose printing to avoid console-induced stalls
            if not hasattr(self, "_last_thruster_log_time"):
                self._last_thruster_log_time = 0.0
            if time.time() - self._last_thruster_log_time > 0.5:
                print(
                    f"[THRUSTER] FB {forward_back:.2f} → Ch1={value}, Ch8={reverse_value}"
                )
                self._last_thruster_log_time = time.time()

        # Left/Right rotation (Channels 2 and 5)
        # From reference: axis_0 > 0 → right, axis_0 < 0 → left
        if abs(left_right) > self.DEADZONE:
            value = self.axis_to_pwm(left_right)
            value2 = self.axis_to_pwm(-left_right)
            channels[1] = value  # Ch2
            channels[4] = value2  # Ch5
            if time.time() - getattr(self, "_last_thruster_log_time", 0.0) > 0.5:
                print(f"[THRUSTER] LR {left_right:.2f} → Ch2={value}, Ch5={value2}")
                self._last_thruster_log_time = time.time()

        # Up/Down (Channels 3, 4, 6, 7)
        # From reference: axis_5 < 0 → up, axis_5 > 0 → down
        # Only apply vertical thrust if the value is outside deadzone
        if abs(up_down) > self.DEADZONE:
            value = self.axis_to_pwm(up_down)
            value2 = self.axis_to_pwm(-up_down)
            channels[2] = value2  # Ch3: ACW
            channels[3] = value2  # Ch4: ACW
            channels[5] = value  # Ch6: CW
            channels[6] = value  # Ch7: CW
            if time.time() - getattr(self, "_last_thruster_log_time", 0.0) > 0.5:
                print(
                    f"[THRUSTER] UD {up_down:.2f} → Ch3={value2}, Ch4={value2}, Ch6={value}, Ch7={value}"
                )
                self._last_thruster_log_time = time.time()

        # Emergency stop (Start button)
        if buttons["start"]:
            channels = [self.PWM_NEUTRAL] * 8
            print("[THRUSTER] ⚠️ EMERGENCY STOP - All channels set to neutral (1500μs)")

        return channels

    def close(self):
        """Close joystick connection."""
        if self.joystick:
            self.joystick.quit()
            self.joystick = None
        pygame.quit()
        print("[JOYSTICK] Disconnected")
