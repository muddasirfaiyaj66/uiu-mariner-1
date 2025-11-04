from pymavlink import mavutil
import time


class PixhawkConnection:
    """
    MAVLink connection to Pixhawk running ArduSub firmware.
    Supports arming, mode changes, and direct thruster control via RC_CHANNELS_OVERRIDE.
    """

    def __init__(self, link="udp:192.168.0.104:14550", auto_detect=False):
        """
        Initialize Pixhawk connection.

        Args:
            link: Connection string (e.g., "udp:192.168.0.104:14550" or "/dev/ttyUSB0:115200")
            auto_detect: If True and connection fails, try to auto-detect serial port
        """
        self.link = link
        self.auto_detect = auto_detect
        self.vehicle = None
        self.connected = False

    def connect(self):
        """Establish MAVLink connection and wait for heartbeat."""
        try:
            print(f"[CONNECT] Attempting to connect → {self.link}")
            self.vehicle = mavutil.mavlink_connection(self.link)
            self.vehicle.wait_heartbeat(timeout=10)
            print(f"[✅] Heartbeat received — Pixhawk Connected!")
            print(
                f"    System ID: {self.vehicle.target_system}, Component ID: {self.vehicle.target_component}"
            )
            self.connected = True
            return self.vehicle
        except Exception as e:
            print(f"[❌] Connection failed: {e}")

            # Try auto-detection if enabled
            if self.auto_detect:
                print("[AUTO-DETECT] Attempting to find Pixhawk on serial ports...")
                detected_link = self._auto_detect_port()
                if detected_link:
                    self.link = detected_link
                    return self.connect()  # Retry with detected port

            self.connected = False
            return None

    def _auto_detect_port(self):
        """
        Auto-detect Pixhawk on serial ports.

        Returns:
            Connection string if found, None otherwise
        """
        try:
            from .portScanner import quick_scan

            return quick_scan(verbose=True)
        except ImportError:
            print("[AUTO-DETECT] ⚠️ portScanner not available")
            return None
        except Exception as e:
            print(f"[AUTO-DETECT] ❌ Error: {e}")
            return None

    def set_mode(self, mode="MANUAL"):
        """
        Set ArduSub flight mode.
        Common modes: MANUAL, STABILIZE, ALT_HOLD, DEPTH_HOLD, POSHOLD
        """
        if not self.connected:
            print("[❌] Not connected to Pixhawk")
            return False

        try:
            self.vehicle.set_mode_apm(mode)
            print(f"[MODE] → {mode}")
            return True
        except Exception as e:
            print(f"[❌] Failed to set mode: {e}")
            return False

    def arm(self):
        """Arm the vehicle (enable thrusters)."""
        if not self.connected:
            print("[❌] Not connected to Pixhawk")
            return False

        try:
            self.vehicle.mav.command_long_send(
                self.vehicle.target_system,
                self.vehicle.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
            )
            print("[✅] Thrusters armed!")
            return True
        except Exception as e:
            print(f"[❌] Arming failed: {e}")
            return False

    def disarm(self):
        """Disarm the vehicle (disable thrusters)."""
        if not self.connected:
            print("[❌] Not connected to Pixhawk")
            return False

        try:
            self.vehicle.mav.command_long_send(
                self.vehicle.target_system,
                self.vehicle.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            )
            print("[⚠️] Thrusters disarmed")
            return True
        except Exception as e:
            print(f"[❌] Disarming failed: {e}")
            return False

    def send_rc_channels_override(self, channels):
        """
        Send RC_CHANNELS_OVERRIDE message to directly control thrusters.

        Args:
            channels (list): List of 8 PWM values (1000-2000), 1500 is neutral.
                            [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8]

        ArduSub Standard Frame Configuration (BlueROV2):
            Channel 1: Forward/Backward (Left Thruster)
            Channel 2: Left/Right (Right Lateral Thruster)
            Channel 3: Up/Down (Front Vertical Thruster)
            Channel 4: Up/Down (Rear Vertical Thruster)
            Channel 5: Forward/Backward (Right Thruster)
            Channel 6: Yaw (Left Lateral Thruster)
            Channel 7: Roll/Pitch
            Channel 8: Roll/Pitch
        """
        if not self.connected:
            print("[❌] Not connected to Pixhawk")
            return False

        if len(channels) != 8:
            print(f"[❌] Expected 8 channels, got {len(channels)}")
            return False

        # Clamp values to 1000-2000 range
        channels = [max(1000, min(2000, int(ch))) for ch in channels]

        try:
            self.vehicle.mav.rc_channels_override_send(
                self.vehicle.target_system, self.vehicle.target_component, *channels
            )
            return True
        except Exception as e:
            print(f"[❌] Failed to send RC override: {e}")
            return False

    def send_manual_control(self, x=0, y=0, z=500, r=0):
        """
        Send MANUAL_CONTROL message (alternative to RC_CHANNELS_OVERRIDE).

        Args:
            x: Forward/backward (-1000 to 1000)
            y: Left/right (-1000 to 1000)
            z: Throttle (0 to 1000, 500 is neutral for ArduSub)
            r: Yaw rotation (-1000 to 1000)
        """
        if not self.connected:
            print("[❌] Not connected to Pixhawk")
            return False

        try:
            self.vehicle.mav.manual_control_send(
                self.vehicle.target_system, x, y, z, r, 0  # buttons (16-bit bitmask)
            )
            return True
        except Exception as e:
            print(f"[❌] Failed to send manual control: {e}")
            return False

    def get_status(self):
        """Get current vehicle status."""
        if not self.connected:
            return {"connected": False}

        try:
            # Request heartbeat to check connection
            msg = self.vehicle.recv_match(type="HEARTBEAT", blocking=False, timeout=0.1)
            return {
                "connected": True,
                "system_id": self.vehicle.target_system,
                "component_id": self.vehicle.target_component,
                "heartbeat": msg is not None,
            }
        except:
            return {"connected": False}

    def close(self):
        """Close the MAVLink connection."""
        if self.vehicle:
            print("[DISCONNECT] Closing MAVLink connection")
            self.vehicle.close()
            self.connected = False
