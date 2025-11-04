"""
Sensor Telemetry Module
Receives and processes depth, temperature, and pressure data from Raspberry Pi
"""

import socket
import time
import json
from PyQt6.QtCore import QThread, pyqtSignal


class SensorTelemetryWorker(QThread):
    """
    Worker thread to receive sensor data from Raspberry Pi via UDP/TCP socket.
    Emits signals with parsed sensor data for UI updates.
    """

    data_received = pyqtSignal(dict)  # Emits parsed sensor data
    connection_status = pyqtSignal(bool)  # Emits connection status
    error_occurred = pyqtSignal(str)  # Emits error messages

    def __init__(
        self,
        host="raspberrypi.local",
        port=5002,
        protocol="tcp",
        auto_mock_fallback=False,
        parent=None,
    ):
        super().__init__(parent)
        self.host = host
        self.port = port
        self.protocol = protocol.lower()
        self.running = False
        self.socket = None
        self.connected = False
        self.auto_mock_fallback = auto_mock_fallback
        self.mock_worker = None

        print(
            f"[SENSORS] Initialized with host={host}, port={port}, protocol={protocol}"
        )

        # Default sensor values
        self.last_data = {
            "temperature": 0.0,
            "pressure": 0.0,
            "depth": 0.0,
            "timestamp": "",
        }

    def run(self):
        """Main sensor data receiving loop."""
        self.running = True
        retry_count = 0
        max_retries = 3  # Reduced retries for faster fallback

        while self.running and retry_count < max_retries:
            try:
                if self.protocol == "tcp":
                    self._run_tcp()
                else:
                    self._run_udp()
                break  # Exit retry loop if connection successful

            except Exception as e:
                retry_count += 1
                error_msg = f"Sensor connection error (attempt {retry_count}/{max_retries}): {e}"
                print(f"[SENSORS] {error_msg}")
                self.error_occurred.emit(error_msg)
                self.connection_status.emit(False)

                if retry_count < max_retries and self.running:
                    print(f"[SENSORS] Retrying in 2 seconds...")
                    time.sleep(2)  # Reduced wait time

        if retry_count >= max_retries:
            print("[SENSORS] ❌ Max retries reached")
            self.connection_status.emit(False)

            # Auto-fallback to mock mode if enabled
            if self.auto_mock_fallback:
                print("[SENSORS] 🔄 Auto-switching to mock mode...")
                self._start_mock_mode()

    def _run_tcp(self):
        """TCP connection for sensor data."""
        print(f"[SENSORS] Connecting to {self.host}:{self.port} via TCP...")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(
            3
        )  # 3 second connection timeout (faster failure detection)

        try:
            self.socket.connect((self.host, self.port))
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            print(f"[SENSORS] Connection failed: {e}")
            raise  # Re-raise to trigger retry logic

        # Connection successful
        print("[SENSORS] ✅ TCP connection established")
        self.connected = True
        self.connection_status.emit(True)

        # Set longer timeout for receiving data
        self.socket.settimeout(5)

        buffer = ""

        while self.running:
            try:
                data = self.socket.recv(1024).decode("utf-8")

                if not data:
                    print("[SENSORS] No data received, connection closed")
                    break

                buffer += data

                # Process complete lines
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self._process_data(line.strip())

            except socket.timeout:
                # Timeout is normal, continue waiting
                continue
            except Exception as e:
                print(f"[SENSORS] TCP receive error: {e}")
                break

        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        self.connection_status.emit(False)

    def _run_udp(self):
        """UDP connection for sensor data."""
        print(f"[SENSORS] Listening on UDP port {self.port}...")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("", self.port))
        self.socket.settimeout(1.0)  # 1 second timeout for checking running flag

        print("[SENSORS] ✅ UDP socket ready")
        self.connected = True
        self.connection_status.emit(True)

        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                decoded_data = data.decode("utf-8").strip()
                self._process_data(decoded_data)

            except socket.timeout:
                continue  # Normal timeout, continue loop
            except Exception as e:
                print(f"[SENSORS] UDP receive error: {e}")
                break

        self.socket.close()
        self.connected = False
        self.connection_status.emit(False)

    def _process_data(self, data_str):
        """
        Process received sensor data string.
        Expected formats:
        - CSV: "25.5,1013.2,5.3"
        - JSON: {"temperature": 25.5, "pressure": 1013.2, "depth": 5.3}
        """
        if not data_str:
            return

        try:
            # Try JSON first
            if data_str.startswith("{"):
                data_dict = json.loads(data_str)
                sensor_data = {
                    "temperature": float(data_dict.get("temperature", 0.0)),
                    "pressure": float(data_dict.get("pressure", 0.0)),
                    "depth": float(data_dict.get("depth", 0.0)),
                    "timestamp": data_dict.get("timestamp", time.strftime("%H:%M:%S")),
                }

            # Try CSV format
            elif "," in data_str:
                parts = data_str.split(",")
                if len(parts) >= 3:
                    sensor_data = {
                        "temperature": float(parts[0]),
                        "pressure": float(parts[1]),
                        "depth": float(parts[2]),
                        "timestamp": time.strftime("%H:%M:%S"),
                    }
                else:
                    return

            else:
                return

            # Update last known good data
            self.last_data = sensor_data

            # Emit to UI
            self.data_received.emit(sensor_data)

        except (ValueError, json.JSONDecodeError) as e:
            print(f"[SENSORS] Data parse error: {e} - Data: {data_str}")

    def get_last_data(self):
        """Get last received sensor data."""
        return self.last_data.copy()

    def _start_mock_mode(self):
        """Switch to mock mode on connection failure."""
        import random

        print("[SENSORS] ✅ Mock mode activated")
        self.connection_status.emit(True)  # Report as "connected" (to mock)

        depth = 0.0
        direction = 1

        while self.running:
            try:
                # Simulate depth changing
                depth += 0.1 * direction
                if depth > 10.0:
                    direction = -1
                elif depth < 0.0:
                    direction = 1

                # Generate mock data
                sensor_data = {
                    "temperature": 20.0 + random.uniform(-2, 2),
                    "pressure": 1013.0 + random.uniform(-5, 5),
                    "depth": abs(depth) + random.uniform(-0.2, 0.2),
                    "timestamp": time.strftime("%H:%M:%S"),
                }

                self.last_data = sensor_data
                self.data_received.emit(sensor_data)
                time.sleep(0.5)  # Update every 500ms

            except Exception as e:
                print(f"[SENSORS] Mock mode error: {e}")
                break

    def stop(self):
        """Stop the sensor thread."""
        print("[SENSORS] Stopping sensor telemetry...")
        self.running = False

        # Close socket if open
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

        self.wait()


class MockSensorWorker(QThread):
    """
    Mock sensor worker for testing without hardware.
    Generates simulated sensor data.
    """

    data_received = pyqtSignal(dict)
    connection_status = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        self.depth = 0.0
        self.direction = 1  # 1 for increasing, -1 for decreasing

    def run(self):
        """Generate mock sensor data."""
        import random

        self.running = True
        self.connection_status.emit(True)
        print("[SENSORS] Mock sensor data enabled (testing mode)")

        while self.running:
            # Simulate depth changing
            self.depth += 0.1 * self.direction
            if self.depth > 10.0:
                self.direction = -1
            elif self.depth < 0.0:
                self.direction = 1

            # Generate mock data
            sensor_data = {
                "temperature": 20.0 + random.uniform(-2, 2),
                "pressure": 1013.0 + random.uniform(-5, 5),
                "depth": abs(self.depth) + random.uniform(-0.2, 0.2),
                "timestamp": time.strftime("%H:%M:%S"),
            }

            self.data_received.emit(sensor_data)
            time.sleep(0.5)  # Update every 500ms

        self.connection_status.emit(False)

    def stop(self):
        """Stop mock sensor."""
        self.running = False
        self.wait()
