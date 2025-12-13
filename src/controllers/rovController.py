"""
ROV Controller
Main orchestration layer that coordinates between views, models, and services.
Implements the business logic for ROV control.
"""

import logging
from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from src.models import MAVLinkState, ConnectionState, RCChannels
from src.services import PixhawkConnection
from src.joystickController import JoystickController

logger = logging.getLogger(__name__)


class ROVController(QObject):
    """
    Main application controller for the ROV system.
    Coordinates between UI views, data models, and communication services.
    """

    # Signals for UI updates
    connection_status_changed = pyqtSignal(str)  # "connected" | "disconnected"
    telemetry_updated = pyqtSignal(dict)  # Telemetry data dict
    vehicle_armed_changed = pyqtSignal(bool)  # Armed status
    mode_changed = pyqtSignal(str)  # Mode string
    error_occurred = pyqtSignal(str)  # Error message

    def __init__(self):
        """Initialize the ROV controller"""
        super().__init__()

        # Models
        self.state = MAVLinkState()

        # Services
        self.pixhawk_connection: Optional[PixhawkConnection] = None
        self.joystick: Optional[JoystickController] = None

        # Configuration
        self.connection_string = "tcp:raspberrypi.local:7000"

        # Control timers
        self.control_loop_timer = QTimer()
        self.control_loop_timer.timeout.connect(self._control_loop)
        self.control_loop_interval = 50  # ms (20 Hz control rate)

        # RC channels for control
        self.rc_channels = RCChannels()

    def connect_to_pixhawk(self, connection_string: Optional[str] = None) -> bool:
        """
        Establish connection to Pixhawk via network or serial.

        Args:
            connection_string: MAVLink connection string (tcp/udp/serial)
                             e.g., "tcp:192.168.1.104:7000" or "tcp:raspberrypi.local:7000"

        Returns:
            True if connection successful, False otherwise
        """
        try:
            if connection_string:
                self.connection_string = connection_string

            logger.info(f"[ROV] Connecting to {self.connection_string}")
            self.state.connection_state = ConnectionState.CONNECTING

            # Create connection
            if not self.pixhawk_connection:
                self.pixhawk_connection = PixhawkConnection(
                    self.connection_string, timeout=5.0
                )

            # Attempt connection
            if self.pixhawk_connection.connect():
                self.state.connection_state = ConnectionState.CONNECTED
                self.state.update_heartbeat()
                self.connection_status_changed.emit("connected")
                logger.info("[✅] Connected to Pixhawk")

                # Start control loop
                self.control_loop_timer.start(self.control_loop_interval)
                return True
            else:
                self.state.connection_state = ConnectionState.ERROR
                self.connection_status_changed.emit("disconnected")
                logger.error("[❌] Failed to connect to Pixhawk")
                return False

        except Exception as e:
            logger.error(f"[❌] Connection error: {e}")
            self.state.connection_state = ConnectionState.ERROR
            self.connection_status_changed.emit("error")
            self.error_occurred.emit(str(e))
            return False

    def disconnect(self):
        """Disconnect from Pixhawk"""
        try:
            self.control_loop_timer.stop()
            if self.pixhawk_connection:
                self.pixhawk_connection.close()
            self.state.reset()
            self.state.connection_state = ConnectionState.DISCONNECTED
            self.connection_status_changed.emit("disconnected")
            logger.info("[✅] Disconnected from Pixhawk")
        except Exception as e:
            logger.error(f"[❌] Disconnect error: {e}")

    def arm_vehicle(self, force=True) -> bool:
        """
        Arm the vehicle for operation
        
        Args:
            force (bool): If True, force arm bypassing pre-arm checks (default: True for ROV testing)
        """
        if not self.state.is_connected() or not self.pixhawk_connection:
            logger.warning("[⚠️] Cannot arm: not connected")
            return False

        try:
            logger.info("[ROV] Arming vehicle...")
            success = self.pixhawk_connection.arm(force=force)
            if success:
                self.state.telemetry.system_armed = True
                self.vehicle_armed_changed.emit(True)
                return True
            else:
                logger.warning("[⚠️] Arming rejected - trying force arm...")
                success = self.pixhawk_connection.arm(force=True)
                if success:
                    self.state.telemetry.system_armed = True
                    self.vehicle_armed_changed.emit(True)
                return success
        except Exception as e:
            logger.error(f"[❌] Arm failed: {e}")
            self.error_occurred.emit(f"Arm failed: {e}")
            return False

    def disarm_vehicle(self) -> bool:
        """Disarm the vehicle"""
        if not self.state.is_connected() or not self.pixhawk_connection:
            logger.warning("[⚠️] Cannot disarm: not connected")
            return False

        try:
            logger.info("[ROV] Disarming vehicle...")
            self.pixhawk_connection.disarm()
            self.state.telemetry.system_armed = False
            self.vehicle_armed_changed.emit(False)
            return True
        except Exception as e:
            logger.error(f"[❌] Disarm failed: {e}")
            self.error_occurred.emit(f"Disarm failed: {e}")
            return False

    def set_mode(self, mode: str) -> bool:
        """
        Set vehicle mode.

        Args:
            mode: Mode string (e.g., "MANUAL", "ACRO", "STABILIZE")

        Returns:
            True if successful
        """
        if not self.state.is_connected() or not self.pixhawk_connection:
            logger.warning("[⚠️] Cannot set mode: not connected")
            return False

        try:
            logger.info(f"[ROV] Setting mode to {mode}")
            self.pixhawk_connection.set_mode(mode)
            self.state.vehicle_mode = mode
            self.mode_changed.emit(mode)
            return True
        except Exception as e:
            logger.error(f"[❌] Mode change failed: {e}")
            self.error_occurred.emit(f"Mode change failed: {e}")
            return False

    def set_rc_channels(self, channels: list):
        """
        Set RC channel values for thruster control.

        Args:
            channels: List of 8 channel values (1000-2000 microseconds)
        """
        if not self.state.is_connected() or not self.pixhawk_connection:
            return

        try:
            self.rc_channels.channels = channels
            self.pixhawk_connection.send_rc_channels_override(channels)
        except Exception as e:
            logger.error(f"[❌] RC send failed: {e}")

    def initialize_joystick(self) -> bool:
        """Initialize Xbox joystick controller with ArduSub mappings"""
        try:
            self.joystick = JoystickController()
            
            # Register callback functions for button actions
            self.joystick.set_callback("on_arm", self._on_joystick_arm)
            self.joystick.set_callback("on_disarm", self._on_joystick_disarm)
            self.joystick.set_callback("on_capture_photo", self._on_capture_photo)
            self.joystick.set_callback("on_video_start", self._on_video_start)
            self.joystick.set_callback("on_video_stop", self._on_video_stop)
            self.joystick.set_callback("on_emergency_stop", self._on_emergency_stop)
            self.joystick.set_callback("on_timer_toggle", self._on_timer_toggle)
            self.joystick.set_callback("on_camera_switch", self._on_camera_switch)
            self.joystick.set_callback("on_camera_zoom_in", self._on_camera_zoom_in)
            self.joystick.set_callback("on_camera_zoom_out", self._on_camera_zoom_out)
            
            logger.info("[✅] Joystick initialized with ArduSub mappings")
            return True
        except Exception as e:
            logger.warning(f"[⚠️] Joystick initialization failed: {e}")
            return False

    # =========================================================================
    # JOYSTICK CALLBACK HANDLERS
    # =========================================================================

    def _on_joystick_arm(self):
        """Callback when arm button (Back) pressed"""
        self.arm_vehicle(force=True)

    def _on_joystick_disarm(self):
        """Callback when disarm button (Back) pressed again"""
        self.disarm_vehicle()

    def _on_capture_photo(self):
        """Callback when photo capture button (A) pressed - handled by UI"""
        logger.info("[📷] Photo capture requested (UI handles)")
        # Camera is on Pi, capture handled by UI - no MAVLink needed

    def _on_video_start(self):
        """Callback when video recording started (B toggle) - handled by UI"""
        logger.info("[🎥] Video recording START requested (UI handles)")
        # Camera is on Pi, recording handled by UI - no MAVLink needed

    def _on_video_stop(self):
        """Callback when video recording stopped (B toggle) - handled by UI"""
        logger.info("[⏹️] Video recording STOP requested (UI handles)")
        # Camera is on Pi, recording handled by UI - no MAVLink needed

    def _on_emergency_stop(self):
        """Callback when emergency stop button (X) pressed"""
        logger.warning("[🚨 EMERGENCY STOP] Triggered by joystick!")
        if self.pixhawk_connection:
            # Send zero-throttle command
            self.pixhawk_connection.send_emergency_stop()
            # Disarm the vehicle
            self.disarm_vehicle()

    def _on_timer_toggle(self):
        """Callback when timer toggle button (Y) pressed"""
        # Emit signal for UI to handle timer
        logger.info("[⏱️] Timer toggle requested")

    def _on_camera_switch(self):
        """Callback when camera switch button (Start) pressed"""
        logger.info("[📹] Camera switch requested")
        # This would typically emit a signal for the UI to handle

    def _on_camera_zoom_in(self):
        """Callback when zoom in trigger (RT) pressed - handled by UI/OpenCV"""
        logger.debug("[🔍+] Zoom in requested (UI handles via OpenCV)")
        # UI handles zoom via OpenCV - no MAVLink needed

    def _on_camera_zoom_out(self):
        """Callback when zoom out trigger (LT) pressed - handled by UI/OpenCV"""
        logger.debug("[🔍-] Zoom out requested (UI handles via OpenCV)")
        # UI handles zoom via OpenCV - no MAVLink needed

    def _control_loop(self):
        """Main control loop executed at regular intervals"""
        if not self.state.is_connected():
            return

        try:
            # Check connection health
            if not self.pixhawk_connection.is_connected():
                logger.warning("[⚠️] Pixhawk connection lost")
                self.state.connection_state = ConnectionState.DISCONNECTED
                self.connection_status_changed.emit("disconnected")
                self.control_loop_timer.stop()
                return

            # If joystick available, read input and send MANUAL_CONTROL
            if self.joystick and self.joystick.is_connected():
                joystick_state = self.joystick.read_joystick()
                
                # Compute ArduSub MANUAL_CONTROL values
                manual_ctrl = self.joystick.compute_manual_control(joystick_state)
                
                # Send MANUAL_CONTROL message (Method-1 for ArduSub)
                self.pixhawk_connection.send_manual_control(
                    x=manual_ctrl["x"],
                    y=manual_ctrl["y"],
                    z=manual_ctrl["z"],
                    r=manual_ctrl["r"],
                    buttons=manual_ctrl["buttons"]
                )

            # Update telemetry from Pixhawk
            self._update_telemetry()

        except Exception as e:
            logger.error(f"[❌] Control loop error: {e}")

    def _update_telemetry(self):
        """Update telemetry from Pixhawk"""
        if not self.pixhawk_connection:
            return

        try:
            # Get latest telemetry messages
            while True:
                msg = self.pixhawk_connection.recv_match(blocking=False, timeout=0)
                if not msg:
                    break

                msg_type = msg.get_type()

                if msg_type == "HEARTBEAT":
                    self.state.update_heartbeat()
                    self.state.system_id = msg.get_srcSystem()
                    self.state.component_id = msg.get_srcComponent()
                    self.state.vehicle_mode = self.pixhawk_connection.mode_string()

                elif msg_type == "GLOBAL_POSITION_INT":
                    self.state.telemetry.latitude = msg.lat / 1e7
                    self.state.telemetry.longitude = msg.lon / 1e7
                    self.state.telemetry.altitude = msg.alt / 1000.0

                elif msg_type == "ATTITUDE":
                    self.state.telemetry.pitch = msg.pitch
                    self.state.telemetry.roll = msg.roll
                    self.state.telemetry.heading = msg.yaw

                elif msg_type == "SYS_STATUS":
                    self.state.telemetry.battery_voltage = msg.voltage_battery / 1000.0
                    self.state.telemetry.battery_current = msg.current_battery / 100.0
                    self.state.telemetry.battery_remaining = msg.battery_remaining

                elif msg_type == "VFR_HUD":
                    self.state.telemetry.groundspeed = msg.groundspeed

            # Emit telemetry signal
            self.telemetry_updated.emit(
                {
                    "latitude": self.state.telemetry.latitude,
                    "longitude": self.state.telemetry.longitude,
                    "altitude": self.state.telemetry.altitude,
                    "heading": self.state.telemetry.heading,
                    "pitch": self.state.telemetry.pitch,
                    "roll": self.state.telemetry.roll,
                    "battery_voltage": self.state.telemetry.battery_voltage,
                    "battery_remaining": self.state.telemetry.battery_remaining,
                }
            )

        except Exception as e:
            logger.debug(f"Telemetry update error: {e}")

    def is_connected(self) -> bool:
        """Check if connected to Pixhawk"""
        return self.state.is_connected()

    def is_armed(self) -> bool:
        """Check if vehicle is armed"""
        return self.state.telemetry.system_armed
