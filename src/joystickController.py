"""
UIU MARINER - Joystick Controller
==================================
Converts gamepad input to ArduSub MANUAL_CONTROL commands.

JOYSTICK AXIS MAPPING:
  LEFT STICK:
    - Axis 0 (X): Sway (strafe left/right) → thrusters 1-4
    - Axis 1 (Y): Surge (forward/back)     → thrusters 1-4 (INVERTED)
  
  RIGHT STICK:
    - Axis 2 (X): Yaw (rotate left/right)
    - Axis 3 (Y): Heave (up/down)          → thrusters 5-8 (INVERTED)

  TRIGGERS:
    - Axis 4: Camera Zoom OUT
    - Axis 5: Camera Zoom IN

ArduSub Thruster Layout (Vectored-6DOF):
  Thrusters 1-4: Horizontal (forward, backward, strafe, yaw)
  Thrusters 5-8: Vertical (up/down)

MANUAL_CONTROL Message:
  x: Surge (forward/back) [-1000 to 1000]
  y: Sway (left/right strafe) [-1000 to 1000]  
  z: Heave (up/down) [0 to 1000], 500=neutral
  r: Yaw (rotation) [-1000 to 1000]

BUTTONS:
  Button 0: Capture Photo
  Button 1: Toggle Video Recording
  Button 2: Emergency Stop
  Button 3: Timer Toggle
  Button 6: Arm/Disarm
  Button 7: Switch Camera
"""

import pygame
import time
from typing import Dict, Optional, Callable

# ArduSub MANUAL_CONTROL Range
ARDUSUB_MIN = -1000
ARDUSUB_MAX = 1000
ARDUSUB_Z_MIN = 0
ARDUSUB_Z_CENTER = 500
ARDUSUB_Z_MAX = 1000

# RC Channel Range (PWM microseconds)
RC_MIN = 1000
RC_CENTER = 1500
RC_MAX = 2000

# Joystick Configuration - INCREASED DEADZONE to prevent vibration
DEADZONE = 0.15  # Increased from 0.05 to prevent jitter/vibration
TRIGGER_DEADZONE = 0.1
CALIBRATION_DELAY = 1.5
DEBOUNCE_TIME = 0.2

# Smoothing factor (0.0 = no smoothing, 1.0 = max smoothing)
SMOOTHING_FACTOR = 0.3

# Debug
DEBUG_ENABLED = False
DEBUG_LOG_INTERVAL = 0.5


class JoystickController:
    """ArduSub joystick controller using MANUAL_CONTROL (Mode A)."""

    def __init__(self, joystick_index=0, target_name=None):
        pygame.init()
        pygame.joystick.init()

        self.joystick = None
        self.joystick_name = "Not Connected"
        self.ready_time = time.time() + CALIBRATION_DELAY
        self._last_log_time = 0.0

        # State tracking
        self.is_armed = False
        self.is_recording_video = False
        self.timer_active = False
        self.current_camera_index = 0
        self.emergency_stop_active = False
        self.camera_zoom_in = False
        self.camera_zoom_out = False

        # Smoothing - store previous values to prevent rapid oscillation
        self._prev_x = 0
        self._prev_y = 0
        self._prev_z = ARDUSUB_Z_CENTER
        self._prev_r = 0

        # Button debounce
        self._button_last_press = {}
        self._button_prev_state = {}

        # Callbacks for UI integration
        self._callbacks: Dict[str, Optional[Callable]] = {
            "on_arm": None,
            "on_disarm": None,
            "on_capture_photo": None,
            "on_video_start": None,
            "on_video_stop": None,
            "on_emergency_stop": None,
            "on_timer_toggle": None,
            "on_camera_switch": None,
            "on_camera_zoom_in": None,
            "on_camera_zoom_out": None,
        }

        self._connect_joystick(joystick_index, target_name)

    def _connect_joystick(self, joystick_index, target_name):
        """Connect to available joystick."""
        if pygame.joystick.get_count() == 0:
            print("[JOYSTICK] No joystick detected")
            return

        if target_name:
            for i in range(pygame.joystick.get_count()):
                js = pygame.joystick.Joystick(i)
                js.init()
                if target_name.lower() in js.get_name().lower():
                    self.joystick = js
                    self.joystick_name = js.get_name()
                    print(f"[JOYSTICK] Connected: {self.joystick_name}")
                    return
                js.quit()

        # Default to first joystick
        self.joystick = pygame.joystick.Joystick(joystick_index)
        self.joystick.init()
        self.joystick_name = self.joystick.get_name()
        print(f"[JOYSTICK] Connected: {self.joystick_name}")

    def set_callback(self, event_name: str, callback: Callable):
        """Register callback for joystick events."""
        if event_name in self._callbacks:
            self._callbacks[event_name] = callback

    def _trigger_callback(self, event_name: str):
        """Trigger registered callback."""
        cb = self._callbacks.get(event_name)
        if cb:
            try:
                print(f"[CALLBACK] Triggering: {event_name}")
                cb()
            except Exception as e:
                print(f"[JOYSTICK] Callback error for {event_name}: {e}")
        else:
            print(f"[CALLBACK] No handler registered for: {event_name}")

    def is_connected(self) -> bool:
        return self.joystick is not None

    def is_ready(self) -> bool:
        return self.is_connected() and time.time() >= self.ready_time

    def _get_axis(self, index: int) -> float:
        """Get axis value with proper deadzone to prevent jitter."""
        if not self.joystick:
            return 0.0
        try:
            val = self.joystick.get_axis(index)
            # Apply deadzone - return 0 if within deadzone
            if abs(val) < DEADZONE:
                return 0.0
            # Scale the remaining range so movement starts smoothly after deadzone
            # This prevents sudden jumps when exiting deadzone
            sign = 1 if val > 0 else -1
            scaled = (abs(val) - DEADZONE) / (1.0 - DEADZONE)
            return sign * scaled
        except:
            return 0.0

    def _get_button(self, index: int) -> bool:
        """Get button state."""
        if not self.joystick:
            return False
        try:
            return self.joystick.get_button(index)
        except:
            return False

    def _button_pressed(self, name: str, state: bool) -> bool:
        """Check for button press with debounce."""
        prev = self._button_prev_state.get(name, False)
        self._button_prev_state[name] = state

        if state and not prev:
            last = self._button_last_press.get(name, 0)
            if time.time() - last >= DEBOUNCE_TIME:
                self._button_last_press[name] = time.time()
                return True
        return False

    def _to_ardusub(self, val: float, invert: bool = False) -> int:
        """Convert axis to ArduSub range [-1000, 1000] with clean zero."""
        if invert:
            val = -val
        # If value is essentially zero, return exactly 0
        if abs(val) < 0.01:
            return 0
        return max(ARDUSUB_MIN, min(ARDUSUB_MAX, int(val * ARDUSUB_MAX)))

    def _to_ardusub_z(self, val: float, invert: bool = True) -> int:
        """Convert axis to ArduSub Z range [0, 1000], 500=neutral."""
        if invert:
            val = -val
        # If value is essentially zero, return exactly center (500)
        if abs(val) < 0.05:
            return ARDUSUB_Z_CENTER
        return max(ARDUSUB_Z_MIN, min(ARDUSUB_Z_MAX, int(ARDUSUB_Z_CENTER + val * 500)))

    def _smooth(self, new_val: int, prev_val: int) -> int:
        """Apply smoothing to prevent rapid oscillation/vibration."""
        # If new value is neutral (0 or 500 for z), snap to it immediately
        if new_val == 0 or new_val == ARDUSUB_Z_CENTER:
            return new_val
        # Otherwise apply smoothing
        return int(prev_val + (new_val - prev_val) * (1.0 - SMOOTHING_FACTOR))

    def read_joystick(self) -> Dict:
        """Read all joystick inputs."""
        if not self.is_ready():
            return self._empty_state()

        pygame.event.pump()

        return {
            "axes": {
                "left_x": self._get_axis(0),   # Sway
                "left_y": self._get_axis(1),   # Surge
                "right_x": self._get_axis(2),  # Yaw
                "right_y": self._get_axis(3),  # Heave
                "zoom_out": self._get_axis(4), # Camera Zoom OUT
                "zoom_in": self._get_axis(5),  # Camera Zoom IN
            },
            "buttons": {
                "btn0": self._get_button(0),  # Photo
                "btn1": self._get_button(1),  # Recording
                "btn2": self._get_button(2),  # Emergency Stop
                "btn3": self._get_button(3),  # Timer
                "btn6": self._get_button(6),  # Arm/Disarm
                "btn7": self._get_button(7),  # Camera Switch
            },
        }

    def _empty_state(self) -> Dict:
        return {
            "axes": {k: 0.0 for k in ["left_x", "left_y", "right_x", "right_y", "zoom_out", "zoom_in"]},
            "buttons": {k: False for k in ["btn0", "btn1", "btn2", "btn3", "btn6", "btn7"]},
        }

    def compute_manual_control(self, state: Dict) -> Dict:
        """
        Convert joystick to ArduSub MANUAL_CONTROL values.
        
        Axis Mapping:
          LEFT STICK:
            - Axis 0 (X): Sway (y) - strafe left/right → thrusters 1-4
            - Axis 1 (Y): Surge (x) - forward/back    → thrusters 1-4 (INVERTED)
          
          RIGHT STICK:
            - Axis 2 (X): Yaw (r) - rotate left/right
            - Axis 3 (Y): Heave (z) - up/down         → thrusters 5-8 (INVERTED)
        
        ArduSub handles all thruster mixing internally based on frame type.
        """
        axes = state["axes"]
        buttons = state["buttons"]

        # Emergency Stop (Button 2) - highest priority
        if self._button_pressed("btn2", buttons.get("btn2", False)):
            self.emergency_stop_active = True
            self._prev_x = 0
            self._prev_y = 0
            self._prev_z = ARDUSUB_Z_CENTER
            self._prev_r = 0
            print("[🚨 EMERGENCY STOP]")
            self._trigger_callback("on_emergency_stop")
            return {"x": 0, "y": 0, "z": ARDUSUB_Z_CENTER, "r": 0, "buttons": 0, "emergency_stop": True}

        if not buttons.get("btn2", False):
            self.emergency_stop_active = False

        # Axis mapping per user's controller:
        # Left Y (axis 1) → Surge (forward/back) - INVERTED
        # Left X (axis 0) → Sway (strafe)
        # Right X (axis 2) → Yaw (rotate)
        # Right Y (axis 3) → Heave (up/down) - INVERTED
        raw_surge = self._to_ardusub(axes.get("left_y", 0), invert=True)   # Left Y → Forward/Back
        raw_sway = self._to_ardusub(axes.get("left_x", 0))                  # Left X → Strafe
        raw_heave = self._to_ardusub_z(axes.get("right_y", 0), invert=True) # Right Y → Up/Down (thrusters 5-8)
        raw_yaw = self._to_ardusub(axes.get("right_x", 0))                  # Right X → Yaw

        # Apply smoothing to prevent vibration/oscillation
        surge = self._smooth(raw_surge, self._prev_x)
        sway = self._smooth(raw_sway, self._prev_y)
        heave = self._smooth(raw_heave, self._prev_z)
        yaw = self._smooth(raw_yaw, self._prev_r)

        # Update previous values for next smoothing cycle
        self._prev_x = surge
        self._prev_y = sway
        self._prev_z = heave
        self._prev_r = yaw

        # Camera Zoom (Axis 4 = OUT, Axis 5 = IN)
        # Note: Triggers typically range from -1 (not pressed) to +1 (fully pressed)
        # or 0 (not pressed) to 1 (fully pressed) depending on controller
        zoom_out_raw = axes.get("zoom_out", 0)
        zoom_in_raw = axes.get("zoom_in", 0)
        
        # Normalize trigger values: convert -1 to 1 range to 0 to 1 range
        # If trigger is at -1, it's not pressed; if at 1, it's fully pressed
        zoom_in = (zoom_in_raw + 1) / 2 if zoom_in_raw < 0 else zoom_in_raw
        zoom_out = (zoom_out_raw + 1) / 2 if zoom_out_raw < 0 else zoom_out_raw
        
        if zoom_in > TRIGGER_DEADZONE:
            if not self.camera_zoom_in:
                self.camera_zoom_in = True
                print(f"[ZOOM] IN pressed (value: {zoom_in:.2f})")
                self._trigger_callback("on_camera_zoom_in")
        else:
            self.camera_zoom_in = False

        if zoom_out > TRIGGER_DEADZONE:
            if not self.camera_zoom_out:
                self.camera_zoom_out = True
                print(f"[ZOOM] OUT pressed (value: {zoom_out:.2f})")
                self._trigger_callback("on_camera_zoom_out")
        else:
            self.camera_zoom_out = False

        # Button actions
        self._process_buttons(buttons)

        # Button bitmask
        bitmask = sum((1 << i) for i, k in enumerate(["btn0", "btn1", "btn2", "btn3", "btn6", "btn7"]) if buttons.get(k))

        if DEBUG_ENABLED and time.time() - self._last_log_time > DEBUG_LOG_INTERVAL:
            if surge or sway or heave != ARDUSUB_Z_CENTER or yaw:
                print(f"[CTRL] x:{surge:+5d} y:{sway:+5d} z:{heave:4d} r:{yaw:+5d}")
                self._last_log_time = time.time()

        return {"x": surge, "y": sway, "z": heave, "r": yaw, "buttons": bitmask, "emergency_stop": False}

    def _process_buttons(self, buttons: Dict):
        """Process button presses."""
        # Button 0 - Photo
        if self._button_pressed("btn0", buttons.get("btn0", False)):
            print("[📷] Photo")
            self._trigger_callback("on_capture_photo")

        # Button 1 - Video toggle
        if self._button_pressed("btn1", buttons.get("btn1", False)):
            self.is_recording_video = not self.is_recording_video
            print(f"[🎥] Video: {'START' if self.is_recording_video else 'STOP'}")
            self._trigger_callback("on_video_start" if self.is_recording_video else "on_video_stop")

        # Button 3 - Timer
        if self._button_pressed("btn3", buttons.get("btn3", False)):
            self.timer_active = not self.timer_active
            print(f"[⏱️] Timer: {'ON' if self.timer_active else 'OFF'}")
            self._trigger_callback("on_timer_toggle")

        # Button 6 - Arm/Disarm
        if self._button_pressed("btn6", buttons.get("btn6", False)):
            self.is_armed = not self.is_armed
            print(f"[{'🔓 ARM' if self.is_armed else '🔒 DISARM'}]")
            self._trigger_callback("on_arm" if self.is_armed else "on_disarm")

        # Button 7 - Camera switch
        if self._button_pressed("btn7", buttons.get("btn7", False)):
            self.current_camera_index = (self.current_camera_index + 1) % 2
            print(f"[📹] Camera {self.current_camera_index}")
            self._trigger_callback("on_camera_switch")

    def get_emergency_stop_command(self) -> Dict:
        """Get emergency stop command."""
        return {"x": 0, "y": 0, "z": ARDUSUB_Z_CENTER, "r": 0, "buttons": 0, "emergency_stop": True}

    def compute_thruster_channels(self, state: Dict) -> list:
        """
        Convert joystick to 8 RC channel values (1000-2000 PWM).
        This is used by mainWindow for RC_CHANNELS_OVERRIDE.
        
        Returns list of 8 channel values.
        """
        axes = state["axes"]
        buttons = state["buttons"]

        # Process button callbacks
        self._process_buttons(buttons)

        # Camera zoom (Axis 4 = OUT, Axis 5 = IN)
        # Note: Triggers typically range from -1 (not pressed) to +1 (fully pressed)
        zoom_out_raw = axes.get("zoom_out", 0)
        zoom_in_raw = axes.get("zoom_in", 0)
        
        # Normalize trigger values
        zoom_in = (zoom_in_raw + 1) / 2 if zoom_in_raw < 0 else zoom_in_raw
        zoom_out = (zoom_out_raw + 1) / 2 if zoom_out_raw < 0 else zoom_out_raw
        
        if zoom_in > TRIGGER_DEADZONE:
            if not self.camera_zoom_in:
                self.camera_zoom_in = True
                self._trigger_callback("on_camera_zoom_in")
        else:
            self.camera_zoom_in = False

        if zoom_out > TRIGGER_DEADZONE:
            if not self.camera_zoom_out:
                self.camera_zoom_out = True
                self._trigger_callback("on_camera_zoom_out")
        else:
            self.camera_zoom_out = False

        # Emergency stop check (Button 2)
        if self._button_pressed("btn2", buttons.get("btn2", False)):
            self.emergency_stop_active = True
            print("[🚨 EMERGENCY STOP]")
            self._trigger_callback("on_emergency_stop")
            return [RC_CENTER] * 8

        if not buttons.get("btn2", False):
            self.emergency_stop_active = False

        # Convert axes to RC channel values
        def axis_to_rc(val: float, invert: bool = False) -> int:
            if invert:
                val = -val
            if abs(val) < DEADZONE:
                return RC_CENTER
            return int(RC_CENTER + val * 400)  # Scale to 1100-1900 range

        # Axis mapping to RC channels (per user's joystick layout):
        # Left Y (axis 1) → Surge (forward/back) - INVERTED
        # Left X (axis 0) → Sway (strafe)
        # Right X (axis 2) → Yaw (rotate)
        # Right Y (axis 3) → Heave (up/down) - INVERTED
        surge = axis_to_rc(axes.get("left_y", 0), invert=True)
        sway = axis_to_rc(axes.get("left_x", 0))
        heave = axis_to_rc(axes.get("right_y", 0), invert=True)
        yaw = axis_to_rc(axes.get("right_x", 0))

        # Return 8 channels: surge, sway, heave, yaw, then neutral for 5-8
        return [surge, sway, heave, yaw, RC_CENTER, RC_CENTER, RC_CENTER, RC_CENTER]

    def close(self):
        """Close joystick."""
        if self.joystick:
            self.joystick.quit()
            self.joystick = None
        pygame.quit()
        print("[JOYSTICK] Disconnected")
