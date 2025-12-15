"""
UIU MARINER - Joystick Controller
==================================
EXACT MAPPING FOR YOUR JOYSTICK:
  LEFT STICK:
    - Axis 0 (X): Sway (strafe left/right)
    - Axis 1 (Y): Surge (forward/backward)
  
  RIGHT STICK:
    - Axis 2 (X): Yaw (rotate left/right)
    - Axis 3 (Y): Heave (up/down)
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

# Joystick Configuration
DEADZONE = 0.15
TRIGGER_DEADZONE = 0.1
CALIBRATION_DELAY = 1.5
DEBOUNCE_TIME = 0.2
SMOOTHING_FACTOR = 0.3

# Debug Configuration
DEBUG_ENABLED = True
DEBUG_LOG_INTERVAL = 0.2


class JoystickController:
    """ArduSub joystick controller with exact mapping."""

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

        # Smoothing
        self._prev_surge = 0
        self._prev_sway = 0
        self._prev_heave = ARDUSUB_Z_CENTER
        self._prev_yaw = 0

        # Button debounce
        self._button_last_press = {}
        self._button_prev_state = {}

        # Callbacks
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
        print(f"[JOYSTICK] Axes: {self.joystick.get_numaxes()}, Buttons: {self.joystick.get_numbuttons()}")

    def set_callback(self, event_name: str, callback: Callable):
        """Register callback for joystick events."""
        if event_name in self._callbacks:
            self._callbacks[event_name] = callback

    def _trigger_callback(self, event_name: str):
        """Trigger registered callback."""
        cb = self._callbacks.get(event_name)
        if cb:
            try:
                cb()
            except Exception as e:
                print(f"[JOYSTICK] Callback error for {event_name}: {e}")

    def is_connected(self) -> bool:
        return self.joystick is not None

    def is_ready(self) -> bool:
        return self.is_connected() and time.time() >= self.ready_time

    def _get_axis(self, index: int) -> float:
        """Get axis value with deadzone."""
        if not self.joystick:
            return 0.0
        try:
            val = self.joystick.get_axis(index)
            if abs(val) < DEADZONE:
                return 0.0
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

    def _to_ardusub(self, val: float) -> int:
        """Convert axis to ArduSub range [-1000, 1000]."""
        if abs(val) < 0.01:
            return 0
        return max(ARDUSUB_MIN, min(ARDUSUB_MAX, int(val * ARDUSUB_MAX)))

    def _to_ardusub_z(self, val: float) -> int:
        """Convert axis to ArduSub Z range [0, 1000], 500=neutral."""
        if abs(val) < 0.01:
            return ARDUSUB_Z_CENTER
        # Map -1 (full up) to 0, 0 to 500, +1 (full down) to 1000
        return int(ARDUSUB_Z_CENTER + val * 500)

    def _smooth(self, new_val: int, prev_val: int) -> int:
        """Apply smoothing."""
        if new_val == 0 or new_val == ARDUSUB_Z_CENTER:
            return new_val
        return int(prev_val + (new_val - prev_val) * (1.0 - SMOOTHING_FACTOR))

    def read_joystick(self) -> Dict:
        """Read all joystick inputs."""
        if not self.is_ready():
            return self._empty_state()

        pygame.event.pump()
        
        # YOUR EXACT AXIS MAPPING:
        # Axis 0: Left stick X (left/right) → SWAY
        # Axis 1: Left stick Y (forward/backward) → SURGE
        # Axis 2: Right stick X (left/right) → YAW
        # Axis 3: Right stick Y (up/down) → HEAVE
        
        left_x = self._get_axis(0)   # Axis 0: Sway (strafe left/right)
        left_y = self._get_axis(1)   # Axis 1: Surge (forward/backward)
        right_x = self._get_axis(2)  # Axis 2: Yaw (rotate left/right)
        right_y = self._get_axis(3)  # Axis 3: Heave (up/down)
        
        # Triggers (if available)
        try:
            zoom_out = self._get_axis(4) if self.joystick.get_numaxes() > 4 else 0.0  # LT
            zoom_in = self._get_axis(5) if self.joystick.get_numaxes() > 5 else 0.0   # RT
        except:
            zoom_out = 0.0
            zoom_in = 0.0

        return {
            "axes": {
                "left_x": left_x,    # SWAY (strafe)
                "left_y": left_y,    # SURGE (forward/back)
                "right_x": right_x,  # YAW (rotation)
                "right_y": right_y,  # HEAVE (up/down)
                "zoom_out": zoom_out,
                "zoom_in": zoom_in,
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
        
        YOUR EXACT MAPPING:
        -------------------
        x (surge):    Axis 1 (left_y) = forward/backward
                      -1.0 = full forward, +1.0 = full backward
        
        y (sway):     Axis 0 (left_x) = strafe left/right
                      -1.0 = full left, +1.0 = full right
        
        z (heave):    Axis 3 (right_y) = up/down
                      -1.0 = full up, +1.0 = full down
                      Map to: 0=full up, 500=neutral, 1000=full down
        
        r (yaw):      Axis 2 (right_x) = rotate left/right
                      -1.0 = rotate left, +1.0 = rotate right
        """
        axes = state["axes"]
        buttons = state["buttons"]

        # Emergency Stop (Button 2)
        if self._button_pressed("btn2", buttons.get("btn2", False)):
            self.emergency_stop_active = True
            self._prev_surge = 0
            self._prev_sway = 0
            self._prev_heave = ARDUSUB_Z_CENTER
            self._prev_yaw = 0
            print("[🚨 EMERGENCY STOP]")
            self._trigger_callback("on_emergency_stop")
            return {
                "x": 0, 
                "y": 0, 
                "z": ARDUSUB_Z_CENTER, 
                "r": 0, 
                "buttons": 0, 
                "emergency_stop": True
            }

        if not buttons.get("btn2", False):
            self.emergency_stop_active = False

        # Get raw axis values
        left_y_raw = axes.get("left_y", 0)   # SURGE (forward/back)
        left_x_raw = axes.get("left_x", 0)   # SWAY (strafe)
        right_x_raw = axes.get("right_x", 0) # YAW (rotate)
        right_y_raw = axes.get("right_y", 0) # HEAVE (up/down)

        # ===========================================
        # DIRECT MAPPING - EXACTLY AS YOU SPECIFIED
        # ===========================================
        
        # IMPORTANT: Check if your joystick needs inversion
        # Test these options one by one:
        
        # OPTION 1: No inversion (standard)
        # raw_surge = self._to_ardusub(left_y_raw)     # Forward: negative, Backward: positive
        # raw_sway = self._to_ardusub(left_x_raw)      # Left: negative, Right: positive
        # raw_yaw = self._to_ardusub(right_x_raw)      # Rotate left: negative, Rotate right: positive
        # raw_heave = self._to_ardusub_z(right_y_raw)  # Up: negative maps to <500, Down: positive maps to >500
        
        # OPTION 2: Invert surge and heave (most common)
        raw_surge = self._to_ardusub(-left_y_raw)     # Inverted: Forward: positive, Backward: negative
        raw_sway = self._to_ardusub(left_x_raw)       # No change
        raw_yaw = self._to_ardusub(right_x_raw)       # No change
        raw_heave = self._to_ardusub_z(-right_y_raw)  # Inverted: Up: positive maps to <500, Down: negative maps to >500
        
        # OPTION 3: All inverted
        # raw_surge = self._to_ardusub(-left_y_raw)
        # raw_sway = self._to_ardusub(-left_x_raw)
        # raw_yaw = self._to_ardusub(-right_x_raw)
        # raw_heave = self._to_ardusub_z(-right_y_raw)

        # Apply smoothing
        surge = self._smooth(raw_surge, self._prev_surge)
        sway = self._smooth(raw_sway, self._prev_sway)
        heave = self._smooth(raw_heave, self._prev_heave)
        yaw = self._smooth(raw_yaw, self._prev_yaw)

        # Update previous values
        self._prev_surge = surge
        self._prev_sway = sway
        self._prev_heave = heave
        self._prev_yaw = yaw

        # Camera Zoom
        zoom_out_raw = axes.get("zoom_out", 0)
        zoom_in_raw = axes.get("zoom_in", 0)
        
        # Normalize trigger values
        zoom_in = (zoom_in_raw + 1) / 2 if zoom_in_raw < 0 else zoom_in_raw
        zoom_out = (zoom_out_raw + 1) / 2 if zoom_out_raw < 0 else zoom_out_raw
        
        if zoom_in > TRIGGER_DEADZONE and not self.camera_zoom_in:
            self.camera_zoom_in = True
            self._trigger_callback("on_camera_zoom_in")
        elif zoom_in <= TRIGGER_DEADZONE:
            self.camera_zoom_in = False

        if zoom_out > TRIGGER_DEADZONE and not self.camera_zoom_out:
            self.camera_zoom_out = True
            self._trigger_callback("on_camera_zoom_out")
        elif zoom_out <= TRIGGER_DEADZONE:
            self.camera_zoom_out = False

        # Button actions
        self._process_buttons(buttons)

        # Button bitmask
        bitmask = 0
        if buttons.get("btn0", False): bitmask |= 1 << 0  # Photo
        if buttons.get("btn1", False): bitmask |= 1 << 1  # Recording
        if buttons.get("btn2", False): bitmask |= 1 << 2  # Emergency Stop
        if buttons.get("btn3", False): bitmask |= 1 << 3  # Timer
        if buttons.get("btn6", False): bitmask |= 1 << 4  # Arm/Disarm
        if buttons.get("btn7", False): bitmask |= 1 << 5  # Camera Switch

        # DEBUG OUTPUT - Clear and informative
        current_time = time.time()
        if DEBUG_ENABLED and current_time - self._last_log_time > DEBUG_LOG_INTERVAL:
            print(f"[JOYSTICK INPUT]")
            print(f"  Left Stick:  X(sway):{left_x_raw:+.3f} Y(surge):{left_y_raw:+.3f}")
            print(f"  Right Stick: X(yaw):{right_x_raw:+.3f} Y(heave):{right_y_raw:+.3f}")
            
            print(f"[ARDUSUB OUTPUT]")
            print(f"  x(surge):   {surge:+5d} {'(FWD)' if surge < 0 else '(BWD)' if surge > 0 else ''}")
            print(f"  y(sway):    {sway:+5d} {'(LEFT)' if sway < 0 else '(RIGHT)' if sway > 0 else ''}")
            print(f"  z(heave):   {heave:4d} {'(UP)' if heave < 500 else '(DOWN)' if heave > 500 else ''}")
            print(f"  r(yaw):     {yaw:+5d} {'(ROT-L)' if yaw < 0 else '(ROT-R)' if yaw > 0 else ''}")
            
            # Movement summary
            movements = []
            if abs(surge) > 50:
                movements.append(f"Surge: {'Forward' if surge < 0 else 'Backward'}")
            if abs(sway) > 50:
                movements.append(f"Sway: {'Left' if sway < 0 else 'Right'}")
            if abs(heave - ARDUSUB_Z_CENTER) > 50:
                movements.append(f"Heave: {'Up' if heave < 500 else 'Down'}")
            if abs(yaw) > 50:
                movements.append(f"Yaw: {'Left' if yaw < 0 else 'Right'}")
            
            if movements:
                print(f"[MOVEMENT] {' | '.join(movements)}")
            else:
                print(f"[MOVEMENT] Stationary")
            
            print("-" * 50)
            self._last_log_time = current_time

        return {
            "x": surge,
            "y": sway, 
            "z": heave,
            "r": yaw,
            "buttons": bitmask,
            "emergency_stop": False
        }

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
        return {
            "x": 0, 
            "y": 0, 
            "z": ARDUSUB_Z_CENTER, 
            "r": 0, 
            "buttons": 0, 
            "emergency_stop": True
        }

    def close(self):
        """Close joystick."""
        if self.joystick:
            self.joystick.quit()
            self.joystick = None
        pygame.quit()
        print("[JOYSTICK] Disconnected")


# ===========================================
# TEST CODE
# ===========================================
if __name__ == "__main__":
    print("=" * 60)
    print("JOYSTICK TEST - YOUR EXACT MAPPING")
    print("=" * 60)
    print("Move joysticks and check the mapping:")
    print("1. Left Stick FORWARD/BACK → Should show 'x(surge)'")
    print("2. Left Stick LEFT/RIGHT → Should show 'y(sway)'")
    print("3. Right Stick LEFT/RIGHT → Should show 'r(yaw)'")
    print("4. Right Stick UP/DOWN → Should show 'z(heave)'")
    print("=" * 60)
    print("NOTE: If directions are reversed, change the inversion")
    print("in the compute_manual_control() method")
    print("=" * 60)
    
    controller = JoystickController()
    
    try:
        while True:
            if controller.is_ready():
                state = controller.read_joystick()
                control = controller.compute_manual_control(state)
                
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    finally:
        controller.close()