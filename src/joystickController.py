"""
UIU MARINER - Joystick / Gamepad Controller
=============================================
Reads Xbox 360, Xbox One, and Nintendo Switch Pro controller input.
Converts analog stick and button inputs to 8-channel thruster PWM commands.

Features:
  - Multi-controller support with auto-detection
  - Xbox 360 and Nintendo Switch Pro controller mappings
  - Deadzone filtering for analog sticks
  - Rate-limited debug logging
  - Emergency stop button support
  - Thruster channel computation with customizable mappings

Author: UIU MARINER Development Team
"""

import pygame
import time
from typing import List, Dict, Optional


# Joystick Configuration Constants
DEADZONE = 0.03  # Ignore analog stick movements below this threshold
PWM_MIN = 1000  # Minimum PWM value (full reverse)
PWM_NEUTRAL = 1500  # Neutral PWM value (no thrust)
PWM_MAX = 2000  # Maximum PWM value (full forward)

# Calibration timing
CALIBRATION_DELAY = 1.5  # Time to wait before joystick is ready (seconds)

# Channel mapping (indices 0..7 correspond to RC channels 1..8)
# Update these values to remap which RC channel each logical thruster uses.
CHANNEL_MAP = {
    "forward_a": 0,  # Channel 1 (index 0)
    "yaw_a": 1,      # Channel 2 (index 1)
    "vert_a": 2,     # Channel 3 (index 2)
    "vert_b": 3,     # Channel 4 (index 3)
    "yaw_b": 4,      # Channel 5 (index 4)
    "vert_c": 5,     # Channel 6 (index 5)
    "vert_d": 6,     # Channel 7 (index 6)
    "forward_b": 7,  # Channel 8 (index 7)
}


class JoystickController:
    """
    Manages joystick/gamepad input and converts to ROV thruster commands.

    Supports multiple controller types with automatic detection:
    - Xbox 360 / Xbox One / Compatible gamepads
    - Nintendo Switch Pro Controller

    Handles analog stick input processing with deadzone filtering and
    converts joystick axes to 8-channel PWM thruster values suitable
    for ArduSub/BlueROV2 ROVs.

    Example:
        controller = JoystickController()
        if controller.is_ready():
            state = controller.read_joystick()
            channels = controller.compute_thruster_channels(state)
            # Send channels to thruster controller
    """

    def __init__(self, joystick_index=0, target_name=None):
        """
        Initialize joystick controller with pygame.

        Args:
            joystick_index (int): Index of joystick to use (default: first joystick)
            target_name (str, optional): Filter for specific controller name
                                       (e.g., "Xbox" to select Xbox controller)
                                       If not found, falls back to first available
        """
        pygame.init()
        pygame.joystick.init()

        # Joystick instance
        self.joystick = None
        self.joystick_name = "Not Connected"
        self.last_read_time = time.time()

        # Calibration delay - joystick not ready until after delay period
        self.ready_time = time.time() + CALIBRATION_DELAY

        # Logging throttling
        self._last_axes_log_time = 0.0
        self._last_thruster_log_time = 0.0

        self._connect_joystick(joystick_index, target_name)

    def _connect_joystick(self, joystick_index, target_name):
        """
        Scan for and connect to an available joystick.

        If target_name is specified, searches for a joystick with matching name.
        If match not found, falls back to first available joystick.

        Args:
            joystick_index (int): Index of first joystick to try
            target_name (str, optional): Partial name to search for
        """
        joystick_count = pygame.joystick.get_count()

        if joystick_count == 0:
            print("❌ No joystick detected")
            return False

        print(f"[JOYSTICK] Found {joystick_count} joystick(s)")

        # Try to find target controller if name specified
        if target_name:
            self._connect_by_target_name(joystick_count, target_name)
        else:
            # Use first available joystick
            self._connect_by_index(joystick_index)

        return bool(self.joystick)

    def _connect_by_target_name(self, joystick_count: int, target_name: str):
        """
        Search for joystick with name containing target_name.

        Args:
            joystick_count (int): Total number of joysticks available
            target_name (str): Partial name to match (case-insensitive)
        """
        found = False

        # List all joysticks and search for match
        for i in range(joystick_count):
            js = pygame.joystick.Joystick(i)
            js.init()
            name = js.get_name()
            print(f"[JOYSTICK] {i}: {name}")

            # Check if this is our target
            if not found and target_name.lower() in name.lower():
                self.joystick = js
                self.joystick_name = name
                print(f"[JOYSTICK] ✅ Matched target '{target_name}' → {name}")
                found = True
            else:
                js.quit()

        # Fallback if target not found
        if not found:
            print(
                f"[JOYSTICK] ⚠️ Target '{target_name}' not found, "
                f"using first available"
            )
            self._connect_by_index(0)

    def _connect_by_index(self, joystick_index: int):
        """
        Connect to joystick by index.

        Args:
            joystick_index (int): Index of joystick to connect to
        """
        try:
            self.joystick = pygame.joystick.Joystick(joystick_index)
            self.joystick.init()
            self.joystick_name = self.joystick.get_name()
            print(f"[JOYSTICK] ✅ Connected to: {self.joystick_name}")
        except Exception as e:
            print(f"[JOYSTICK] ❌ Failed to connect: {e}")
            self.joystick = None

    def get_axis_value(self, axis_index: int, invert=False) -> float:
        """
        Read a joystick analog axis with deadzone filtering.

        Applies deadzone threshold to ignore small stick movements caused
        by calibration drift or sensor noise.

        Args:
            axis_index (int): Axis index (0-5):
                - 0: Left stick horizontal
                - 1: Left stick vertical
                - 2: Left trigger (LT / ZL)
                - 3: Right stick horizontal
                - 4: Right stick vertical
                - 5: Right trigger (RT / ZR)
            invert (bool): If True, multiply result by -1

        Returns:
            float: Axis value from -1.0 to 1.0, or 0.0 if in deadzone
        """
        if not self.joystick:
            return 0.0

        try:
            value = self.joystick.get_axis(axis_index)
            if invert:
                value = -value
        except Exception:
            return 0.0
        # Apply deadzone - ignore small movements
        return 0.0 if abs(value) < DEADZONE else value

    def get_button(self, button_index: int) -> bool:
        """
        Read a joystick button state.

        Args:
            button_index (int): Button index (typically 0-9):
                - 0: A button
                - 1: B button
                - 2: X button
                - 3: Y button
                - 4: LB (Left Bumper)
                - 5: RB (Right Bumper)
                - 6: Back button
                - 7: Start button
                - 8: Left stick press
                - 9: Right stick press

        Returns:
            bool: True if button pressed, False otherwise
        """
        if not self.joystick:
            return False

        try:
            return self.joystick.get_button(button_index)
        except Exception:
            return False

    def get_hat(self, hat_index: int = 0) -> tuple:
        """
        Read D-pad (hat switch) state.

        Args:
            hat_index (int): Hat index (usually 0)

        Returns:
            tuple: (x, y) where:
                - x: -1 (left), 0 (center), 1 (right)
                - y: -1 (down), 0 (center), 1 (up)
        """
        if not self.joystick:
            return (0, 0)

        try:
            return self.joystick.get_hat(hat_index)
        except Exception:
            return (0, 0)

    def is_connected(self) -> bool:
        """Check if joystick is connected and initialized."""
        return self.joystick is not None

    def is_ready(self) -> bool:
        """
        Check if joystick has passed calibration delay and is ready for use.

        Returns False for the first CALIBRATION_DELAY seconds after connection
        to allow the joystick to stabilize.

        Returns:
            bool: True if joystick is connected and calibration complete
        """
        return self.is_connected() and time.time() >= self.ready_time

    def axis_to_pwm(self, axis_value: float, reverse=False) -> int:
        """
        Convert analog axis value to PWM command value.

        Maps normalized joystick value (-1.0 to 1.0) to PWM range (1000-2000)
        suitable for thruster control where:
        - 1000 = full reverse (counter-clockwise)
        - 1500 = neutral / stop
        - 2000 = full forward (clockwise)

        Args:
            axis_value (float): Normalized input from -1.0 to 1.0
            reverse (bool): If True, invert the mapping

        Returns:
            int: PWM value clamped to [1000, 2000]
        """
        if reverse:
            axis_value = -axis_value

        # Map -1.0...1.0 → 1000...2000
        pwm = PWM_NEUTRAL + int(axis_value * 500)
        return max(PWM_MIN, min(PWM_MAX, pwm))

    def read_joystick(self) -> Dict[str, any]:
        """
        Read all joystick inputs and return structured state dictionary.

        Reads analog sticks, buttons, and D-pad, and returns in organized format.
        Automatically detects controller type and applies correct axis mapping.

        Returns:
            Dictionary with keys:
            - axes: Dict mapping axis names to values (-1.0 to 1.0)
                  Keys: "left_x", "left_y", "right_x", "right_y",
                        "left_trigger", "right_trigger"
            - buttons: Dict mapping button names to bool states
                     Keys: "a", "b", "x", "y", "lb", "rb", "back", "start",
                           "left_stick", "right_stick"
            - hat: Tuple of (x, y) D-pad state
            - timestamp: Time of this reading (seconds)
        """
        if not self.is_ready():
            return self._get_empty_state()

        # Update pygame event queue
        pygame.event.pump()

        # Read axes using controller-specific mapping
        axes = self._read_controller_axes()

        # Read buttons (standard Xbox layout)
        buttons = self._read_controller_buttons()

        # Read D-pad
        hat = self.get_hat(0)

        self.last_read_time = time.time()

        return {
            "axes": axes,
            "buttons": buttons,
            "hat": hat,
            "timestamp": self.last_read_time,
        }

    def _read_controller_axes(self) -> Dict[str, float]:
        """
        Read analog stick and trigger axes with controller-specific mapping.

        Different controller types use different axis indices.
        This method auto-detects the controller and applies correct mapping.

        Returns:
            Dictionary mapping axis names to normalized values (-1.0 to 1.0)
        """
        # Auto-detect controller type from name
        controller_name = self.joystick_name.lower()

        if "switch" in controller_name:
            # Nintendo Switch Pro Controller axis mapping
            return {
                "left_x": self.get_axis_value(0),  # Left stick horizontal
                "left_y": self.get_axis_value(1),  # Left stick vertical
                "right_x": self.get_axis_value(2),  # Right stick horizontal
                "right_y": self.get_axis_value(3),  # Right stick vertical
                "left_trigger": self.get_axis_value(4),  # ZL trigger
                "right_trigger": self.get_axis_value(5),  # ZR trigger
            }
        else:
            # Xbox 360 / Standard gamepad axis mapping (default)
            return {
                "left_x": self.get_axis_value(0),  # Left stick horizontal
                "left_y": self.get_axis_value(1),  # Left stick vertical
                "right_x": self.get_axis_value(2),  # Right stick horizontal
                "right_y": self.get_axis_value(3),  # Right stick vertical
                "left_trigger": self.get_axis_value(4),  # LT trigger
                "right_trigger": self.get_axis_value(5),  # RT trigger
            }

    def _read_controller_buttons(self) -> Dict[str, bool]:
        """
        Read all button states using Xbox 360 standard layout.

        Returns:
            Dictionary mapping button names to pressed states (True/False)
        """
        return {
            "a": self.get_button(0),  # A button
            "b": self.get_button(1),  # B button
            "x": self.get_button(2),  # X button
            "y": self.get_button(3),  # Y button
            "lb": self.get_button(4),  # LB bumper
            "rb": self.get_button(5),  # RB bumper
            "back": self.get_button(6),  # Back button
            "start": self.get_button(7),  # Start button
            "left_stick": self.get_button(8),  # Left stick click
            "right_stick": self.get_button(9),  # Right stick click
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
        UIU Mariner 6-DOF Thruster Configuration:
        - 45° angle thrusters: 1,2,3,4 (indices 0,1,2,3) - horizontal movement + yaw
        - 0° angle thrusters: 5,6,7,8 (indices 4,5,6,7) - vertical movement (up/down)
        
        Thrusters:
        - T1-4: 45-degree vectored thrusters for forward/backward, left/right, yaw
        - T5-8: 0-degree vertical thrusters for up/down
        
        Rotation Convention:
        - CW = full forward (PWM 2000)
        - CCW = full reverse (PWM 1000)
        - Neutral = stopped (PWM 1500)
        
        Movement Mappings:
        - Forward (Axis 1 neg): T1-4 CW
        - Backward (Axis 1 pos): T1-4 CCW
        - Left (Axis 0 neg): T1,3 CCW + T2,4 CW
        - Right (Axis 0 pos): T1,3 CW + T2,4 CCW
        - Up (Axis 3 neg): T5-8 CW
        - Down (Axis 3 pos): T5-8 CCW
        - Yaw Right (Axis 2 pos): T1,4 CW + T2,3 CCW
        - Yaw Left (Axis 2 neg): T2,3 CW + T1,4 CCW
        """
        axes = joystick_state["axes"]
        buttons = joystick_state["buttons"]
        hat = joystick_state["hat"]

        # Initialize all channels to neutral (1500)
        channels = [PWM_NEUTRAL] * 8
        
        # Store button states for external use
        self.button_states = buttons
        self.hat_state = hat

        # Read normalized axis values (-1.0 to +1.0)
        axis_0 = axes.get("left_x", 0)    # Left/Right strafe
        axis_1 = axes.get("left_y", 0)    # Forward/Backward
        axis_2 = axes.get("right_x", 0)   # Yaw
        axis_3 = axes.get("right_y", 0)   # Up/Down
        axis_4 = axes.get("left_trigger", 0)   # LT - Camera zoom out
        axis_5 = axes.get("right_trigger", 0)  # RT - Camera zoom in

        # Process hat (D-pad) for digital input
        hat_x = hat[0]  # -1=left, 0=center, +1=right
        hat_y = hat[1]  # -1=down, 0=center, +1=up

        # Combine analog and digital inputs (analog takes priority)
        if abs(axis_0) > DEADZONE:
            strafe = axis_0
        elif hat_x != 0:
            strafe = float(hat_x)
        else:
            strafe = 0.0

        if abs(axis_1) > DEADZONE:
            forward_back = axis_1
        elif hat_y != 0:
            forward_back = float(hat_y)
        else:
            forward_back = 0.0

        if abs(axis_2) > DEADZONE:
            yaw = axis_2
        else:
            yaw = 0.0

        if abs(axis_3) > DEADZONE:
            vertical = axis_3
        else:
            vertical = 0.0

        # --- 6-DOF THRUSTER MIXING ---
        # Apply all 4 DOF movements with proper mixing
        # This allows simultaneous control of multiple directions
        
        # 1. FORWARD/BACKWARD (Axis 1): All 4 horizontal thrusters
        if abs(forward_back) > DEADZONE:
            pwm = self.axis_to_pwm(forward_back)
            channels[0] = pwm  # T1
            channels[1] = pwm  # T2
            channels[2] = pwm  # T3
            channels[3] = pwm  # T4
        
        # 2. LEFT/RIGHT STRAFE (Axis 0): Differential horizontal thrusters
        if abs(strafe) > DEADZONE:
            pwm_cw = self.axis_to_pwm(strafe)      # CW direction
            pwm_ccw = self.axis_to_pwm(-strafe)    # CCW direction
            
            # Add to existing values (for mixing with forward/backward)
            channels[0] = self._mix_pwm(channels[0], pwm_ccw)   # T1 CCW for right
            channels[1] = self._mix_pwm(channels[1], pwm_cw)    # T2 CW for right
            channels[2] = self._mix_pwm(channels[2], pwm_ccw)   # T3 CCW for right
            channels[3] = self._mix_pwm(channels[3], pwm_cw)    # T4 CW for right
        
        # 3. YAW (Axis 2): Opposite rotation pairs
        if abs(yaw) > DEADZONE:
            pwm_cw = self.axis_to_pwm(yaw)         # CW direction
            pwm_ccw = self.axis_to_pwm(-yaw)       # CCW direction
            
            # Add to existing values (for mixing with other movements)
            channels[0] = self._mix_pwm(channels[0], pwm_cw)    # T1 CW for right yaw
            channels[1] = self._mix_pwm(channels[1], pwm_ccw)   # T2 CCW for right yaw
            channels[2] = self._mix_pwm(channels[2], pwm_ccw)   # T3 CCW for right yaw
            channels[3] = self._mix_pwm(channels[3], pwm_cw)    # T4 CW for right yaw
        
        # 4. VERTICAL UP/DOWN (Axis 3): All 4 vertical thrusters
        if abs(vertical) > DEADZONE:
            pwm = self.axis_to_pwm(vertical)
            channels[4] = pwm  # T5
            channels[5] = pwm  # T6
            channels[6] = pwm  # T7
            channels[7] = pwm  # T8

        # --- CAMERA ZOOM ---
        self.camera_zoom_in = axis_5 > 0.1   # RT
        self.camera_zoom_out = axis_4 > 0.1  # LT

        # --- EMERGENCY STOP ---
        # Button 2 (X button): Emergency stop all thrusters
        if buttons.get("x", False):
            self._emergency_stop(channels)
            print("[JOYSTICK] ⚠️ EMERGENCY STOP ACTIVATED!")

        return channels

    def _mix_pwm(self, current_pwm: int, additional_pwm: int) -> int:
        """
        Mix two PWM values together for blended thruster control.
        
        Allows multiple simultaneous movements (e.g., forward + left).
        Uses simple averaging to blend commands.
        
        Args:
            current_pwm: Current PWM value (1000-2000)
            additional_pwm: Additional PWM value to mix in (1000-2000)
            
        Returns:
            Mixed PWM value (1000-2000)
        """
        if current_pwm == PWM_NEUTRAL and additional_pwm == PWM_NEUTRAL:
            return PWM_NEUTRAL
        
        # Average the two values for smooth blending
        mixed = int((current_pwm + additional_pwm) / 2)
        
        # Clamp to valid range
        return max(PWM_MIN, min(PWM_MAX, mixed))

    def _log_raw_axes_periodically(self):
        """
        Log raw axis values periodically for debugging.

        Prevents console spam by only logging every 1 second
        and only when axes are actively being used (value > 0.1).
        """
        import contextlib
        now = time.time()
        if now - self._last_axes_log_time > 1.0:  # Log at most once per second
            with contextlib.suppress(Exception):
                num_axes = self.joystick.get_numaxes()
                raw_axes = [self.joystick.get_axis(i) for i in range(num_axes)]
                # Only log if meaningful movement detected
                if any(abs(val) > 0.1 for val in raw_axes):
                    axes_str = ", ".join(
                        [f"Axis{i}={raw_axes[i]:.2f}" for i in range(num_axes)]
                    )
                    print(f"[DEBUG] RAW AXES: {axes_str}")
            self._last_axes_log_time = now

    def _apply_forward_backward_control(self, channels: list, forward_back: float):
        """
        Apply forward/backward thruster control.

        Channels 1 & 8 handle forward/backward motion:
        - Ch1: ACW (counter-clockwise) for forward
        - Ch8: CW (clockwise) for forward (opposite rotation)

        Args:
            channels (list): Channel array to modify
            forward_back (float): Normalized input -1.0 (forward) to 1.0 (backward)
        """
        if abs(forward_back) > DEADZONE:
            value = self.axis_to_pwm(forward_back)
            reverse_value = self.axis_to_pwm(-forward_back)
            # Use CHANNEL_MAP to determine which indices correspond to forward thrusters
            channels[CHANNEL_MAP["forward_a"]] = value
            channels[CHANNEL_MAP["forward_b"]] = reverse_value

            # Log with rate limiting to avoid console spam
            if time.time() - self._last_thruster_log_time > 0.5:
                direction = "Forward" if forward_back < 0 else "Backward"
                print(
                    f"[THRUSTER] {direction} {forward_back:.2f} "
                    f"→ Ch1={value}, Ch8={reverse_value}"
                )
                self._last_thruster_log_time = time.time()

    def _apply_left_right_control(self, channels: list, left_right: float):
        """
        Apply left/right rotation control (yaw).

        Channels 2 & 5 handle yaw rotation:
        - Ch2 & Ch5: Differential thrust for rotation

        Args:
            channels (list): Channel array to modify
            left_right (float): Normalized input -1.0 (left) to 1.0 (right)
        """
        if abs(left_right) > DEADZONE:
            value = self.axis_to_pwm(left_right)
            value2 = self.axis_to_pwm(-left_right)
            # Map yaw/rotation channels via CHANNEL_MAP
            channels[CHANNEL_MAP["yaw_a"]] = value
            channels[CHANNEL_MAP["yaw_b"]] = value2

            # Log with rate limiting
            if time.time() - self._last_thruster_log_time > 0.5:
                direction = "Left" if left_right < 0 else "Right"
                print(
                    f"[THRUSTER] {direction} {left_right:.2f} "
                    f"→ Ch2={value}, Ch5={value2}"
                )
                self._last_thruster_log_time = time.time()

    def _apply_vertical_control(self, channels: list, up_down: float):
        """
        Apply vertical thruster control (depth control).

        Channels 3, 4, 6, 7 handle vertical movement:
        - Ch3 & Ch4: ACW (counter-clockwise) thrusters
        - Ch6 & Ch7: CW (clockwise) thrusters

        Args:
            channels (list): Channel array to modify
            up_down (float): Normalized input -1.0 (up) to 1.0 (down)
        """
        if abs(up_down) > DEADZONE:
            value = self.axis_to_pwm(up_down)
            value2 = self.axis_to_pwm(-up_down)
            # Map vertical thrusters via CHANNEL_MAP
            channels[CHANNEL_MAP["vert_a"]] = value2
            channels[CHANNEL_MAP["vert_b"]] = value2
            channels[CHANNEL_MAP["vert_c"]] = value
            channels[CHANNEL_MAP["vert_d"]] = value

            # Log with rate limiting
            if time.time() - self._last_thruster_log_time > 0.5:
                direction = "Up" if up_down < 0 else "Down"
                print(
                    f"[THRUSTER] {direction} {up_down:.2f} "
                    f"→ Ch3={value2}, Ch4={value2}, Ch6={value}, Ch7={value}"
                )
                self._last_thruster_log_time = time.time()

    def _emergency_stop(self, channels: list):
        """
        Emergency stop - set all channels to neutral.

        Called when Start button pressed. Immediately stops all thrusters
        by setting all channels to neutral (1500 μs).

        Args:
            channels (list): Channel array to zero out
        """
        for i in range(len(channels)):
            channels[i] = PWM_NEUTRAL
        print("[THRUSTER] ⚠️ EMERGENCY STOP - All channels → neutral (1500μs)")

    def close(self):
        """Close joystick connection."""
        if self.joystick:
            self.joystick.quit()
            self.joystick = None
        pygame.quit()
        print("[JOYSTICK] Disconnected")
