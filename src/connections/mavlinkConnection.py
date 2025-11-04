from pymavlink import mavutil
import time
import sys
import os
from pathlib import Path


class PixhawkConnection:
    """
    MAVLink connection to Pixhawk running ArduSub firmware.
    Supports arming, mode changes, and direct thruster control via RC_CHANNELS_OVERRIDE.
    """

    def __init__(self, link="auto", auto_detect=True):
        """
        Initialize Pixhawk connection.

        Args:
            link: Connection string or "auto" for auto-detection
                  (e.g., "udp:192.168.0.104:14550" or "/dev/ttyUSB0:115200")
            auto_detect: If True, automatically detect Pi and start MAVProxy if needed
        """
        self.link = link
        self.auto_detect = auto_detect
        self.vehicle = None
        self.connected = False
        self.last_heartbeat_time = time.time()  # Initialize to current time, not 0
        self.last_successful_send_time = (
            time.time()
        )  # Initialize to current time, not 0
        self.heartbeat_timeout = (
            60.0  # Extended timeout - we'll rely more on successful sends
        )
        self.last_reconnect_attempt = 0
        self.reconnect_interval = 10.0  # Wait 10 seconds between reconnect attempts

    def connect(self):
        """Establish MAVLink connection and wait for heartbeat."""
        try:
            # Auto-detect Pi and MAVProxy if requested
            if self.link == "auto" and self.auto_detect:
                print("[AUTO-CONNECT] Detecting Raspberry Pi and MAVProxy...")
                detected_link = self._auto_detect_pi_mavproxy()
                if detected_link:
                    self.link = detected_link
                    print(f"[AUTO-CONNECT] ✅ Using: {self.link}")
                else:
                    print("[AUTO-CONNECT] ❌ Failed to auto-detect")
                    # Try auto-detection of serial port as fallback
                    print("[AUTO-DETECT] Attempting to find Pixhawk on serial ports...")
                    detected_link = self._auto_detect_port()
                    if detected_link:
                        self.link = detected_link
                    else:
                        print("[❌] Could not auto-detect connection")
                        self.connected = False
                        return None

            print(f"[CONNECT] Attempting to connect → {self.link}")
            self.vehicle = mavutil.mavlink_connection(self.link, autoreconnect=True)

            # Wait for heartbeat with proper timeout
            print(f"[CONNECT] Waiting for heartbeat...")
            self.vehicle.wait_heartbeat(timeout=10)
            print(f"[✅] Heartbeat received — Pixhawk Connected!")
            print(
                f"    System ID: {self.vehicle.target_system}, Component ID: {self.vehicle.target_component}"
            )
            self.connected = True
            self.last_heartbeat_time = time.time()
            return self.vehicle
        except Exception as e:
            print(f"[❌] Connection failed: {e}")

            # Try auto-detection if enabled (but only once)
            if self.auto_detect and self.link != "auto":
                print("[AUTO-DETECT] Attempting to find Pixhawk on serial ports...")
                detected_link = self._auto_detect_port()
                if detected_link:
                    self.link = detected_link
                    self.auto_detect = False  # Prevent infinite recursion
                    return self.connect()  # Retry with detected port

            self.connected = False
            return None

    def _auto_detect_pi_mavproxy(self):
        """
        Auto-detect Raspberry Pi and start MAVProxy if needed.

        Returns:
            Connection string if successful, None otherwise
        """
        try:
            # Add parent directory to path to import simple_auto_connect
            parent_dir = Path(__file__).parent.parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))

            from simple_auto_connect import get_connection_string

            connection_string = get_connection_string()
            return connection_string

        except ImportError as e:
            print(f"[AUTO-CONNECT] ⚠️ simple_auto_connect not available: {e}")
            return None
        except Exception as e:
            print(f"[AUTO-CONNECT] ❌ Error: {e}")
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
        # Check connection status before sending (but only periodically, not every time)
        if not hasattr(self, "_last_check_time"):
            self._last_check_time = 0

        # Only check connection every 0.5 seconds to avoid interfering with messages
        if time.time() - self._last_check_time > 0.5:
            self.check_connection()
            self._last_check_time = time.time()

        if not self.connected:
            # Only print error occasionally to avoid spam
            if (
                not hasattr(self, "_last_error_time")
                or time.time() - self._last_error_time > 5
            ):
                print("[❌] Not connected to Pixhawk - cannot send thruster commands")
                self._last_error_time = time.time()
            return False

        if len(channels) != 8:
            print(f"[❌] Expected 8 channels, got {len(channels)}")
            return False

        # Clamp values to 1000-2000 range
        channels = [max(1000, min(2000, int(ch))) for ch in channels]

        # Debounce unchanged values and rate-limit to reduce traffic
        if not hasattr(self, "_last_sent_channels"):
            self._last_sent_channels = None
        if not hasattr(self, "_last_send_time"):
            self._last_send_time = 0.0

        now = time.time()
        # Skip if same as last sent within 50ms (20 Hz)
        if self._last_sent_channels == channels and (now - self._last_send_time) < 0.05:
            return True

        # Debug: Log RC override messages periodically
        if not hasattr(self, "_last_rc_log_time"):
            self._last_rc_log_time = 0

        if time.time() - self._last_rc_log_time > 2.0:  # Log every 2 seconds
            print(f"[RC_OVERRIDE] Sending → Ch1-8: {channels}")
            self._last_rc_log_time = time.time()

        try:
            self.vehicle.mav.rc_channels_override_send(
                self.vehicle.target_system, self.vehicle.target_component, *channels
            )
            self._last_sent_channels = channels
            self._last_send_time = now

            # Record successful send (used for connection checking)
            self.last_successful_send_time = now

            # If send succeeds and we weren't marked connected, mark as connected now
            if not self.connected:
                self.connected = True
                print("[PIXHAWK] ✅ Connection confirmed via RC_CHANNELS_OVERRIDE!")

            return True
        except Exception as e:
            print(f"[❌] Failed to send RC override: {e}")
            self.connected = False  # Mark as disconnected on send failure
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

    def check_connection(self):
        """
        Check if connection is still alive.
        Relies on: 1) Successful RC_CHANNELS_OVERRIDE sends, 2) Heartbeat messages if available
        Updates self.connected status automatically.

        Returns:
            bool: True if connected and alive (either via sends or heartbeats)
        """
        if not self.vehicle:
            self.connected = False
            # Try to reconnect if enough time has passed
            self._try_auto_reconnect()
            return False

        try:
            # Check for heartbeat messages (non-blocking)
            msg = self.vehicle.recv_match(type="HEARTBEAT", blocking=False, timeout=0)

            if msg:
                self.last_heartbeat_time = time.time()
                if not self.connected:
                    print("[PIXHAWK] ✅ Connection restored via heartbeat!")
                self.connected = True
            else:
                # Check if we've gone too long without ANY communication
                time_since_heartbeat = time.time() - self.last_heartbeat_time
                time_since_send = time.time() - self.last_successful_send_time

                # Consider connected if either:
                # 1. Recent heartbeat received (< heartbeat_timeout), OR
                # 2. Recent successful send (< 5 seconds ago)
                recent_send = time_since_send < 5.0

                if time_since_heartbeat > self.heartbeat_timeout and not recent_send:
                    # No heartbeat AND no recent successful send = truly disconnected
                    if self.connected:
                        print(
                            f"[PIXHAWK] ❌ Connection lost! (No heartbeat for {time_since_heartbeat:.1f}s, no send for {time_since_send:.1f}s)"
                        )
                    self.connected = False
                    # Try to reconnect after connection loss
                    self._try_auto_reconnect()
                else:
                    # Keep connection alive if we're sending successfully
                    if recent_send and not self.connected:
                        self.connected = True
                        print(
                            "[PIXHAWK] ✅ Connection confirmed via RC_CHANNELS_OVERRIDE!"
                        )

            return self.connected
        except Exception as e:
            print(f"[PIXHAWK] ❌ Connection check failed: {e}")
            self.connected = False
            # Try to reconnect on error
            self._try_auto_reconnect()
            return False

    def _try_auto_reconnect(self):
        """Attempt to reconnect if enough time has passed since last attempt."""
        current_time = time.time()
        if current_time - self.last_reconnect_attempt >= self.reconnect_interval:
            self.last_reconnect_attempt = current_time
            print("[PIXHAWK] 🔄 Attempting auto-reconnect...")
            try:
                # Don't close existing connection for TCP - let autoreconnect handle it
                if self.vehicle and not self.link.startswith("tcp"):
                    try:
                        self.vehicle.close()
                    except:
                        pass
                    self.vehicle = None

                # Try to reconnect with autoreconnect enabled
                if not self.vehicle:
                    print(f"[CONNECT] Attempting to connect → {self.link}")
                    self.vehicle = mavutil.mavlink_connection(
                        self.link, autoreconnect=True
                    )

                # Check for heartbeat non-blocking
                msg = self.vehicle.recv_match(
                    type="HEARTBEAT", blocking=True, timeout=3
                )
                if msg:
                    print(f"[✅] Heartbeat received — Pixhawk Connected!")
                    print(
                        f"    System ID: {msg.get_srcSystem()}, Component ID: {msg.get_srcComponent()}"
                    )
                    self.connected = True
                    self.last_heartbeat_time = time.time()
                else:
                    print(f"[⏳] No heartbeat received, will retry later")
                    self.connected = False

            except KeyboardInterrupt:
                # Re-raise keyboard interrupt to allow clean shutdown
                raise
            except Exception as e:
                print(f"[PIXHAWK] ❌ Auto-reconnect failed: {e}")
                self.connected = False

    def get_status(self):
        """Get current vehicle status."""
        # Update connection status first
        self.check_connection()

        if not self.connected:
            return {"connected": False}

        try:
            return {
                "connected": True,
                "system_id": self.vehicle.target_system,
                "component_id": self.vehicle.target_component,
                "last_heartbeat": time.time() - self.last_heartbeat_time,
            }
        except:
            return {"connected": False}

    def close(self):
        """Close the MAVLink connection."""
        if self.vehicle:
            print("[DISCONNECT] Closing MAVLink connection")
            self.vehicle.close()
            self.connected = False
