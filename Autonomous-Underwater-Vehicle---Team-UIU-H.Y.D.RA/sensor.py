import sys
import socket
import time
from dbconnect import connection
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QThread, pyqtSignal

class SensorDataReceiverThread(QThread):
    """Thread to receive sensor data from Raspberry Pi via socket and store it in MongoDB."""
    data_received = pyqtSignal(dict)  # Signal to update UI with new data

    def __init__(self, collection_name, host="raspberrypi.local", port=5000):
        super().__init__()
        self.collection = connection(collection_name)  # Connect to MongoDB
        self.host = "192.168.21.126"  # Raspberry Pi IP or hostname
        self.port = 5000  # Port to connect
        self.running = True  # Control flag

    def run(self):
        """Connect to Raspberry Pi and continuously receive sensor data."""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.host, self.port))
            print(f"Connected to Raspberry Pi at {self.host}:{self.port}")

            while self.running:
                data = client.recv(1024).decode()
                if not data:
                    break  # Stop if no data received

                # Parse received data
                temp, pressure, depth = data.split(",")

                sensor_data = {
                    "temperature": float(temp),
                    "pressure": float(pressure),
                    "depth": float(depth),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }

                # Insert data into MongoDB
                self.collection.insert_one(sensor_data)
                self.data_received.emit(sensor_data)  # Send data to UI
                print(f"Stored in DB: {sensor_data}")

            client.close()

        except Exception as e:
            print(f"Connection Error: {e}")

    def stop(self):
        """Stop the thread gracefully."""
        self.running = False

class SensorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

        # Start receiving sensor data in a separate thread
        self.data_thread = SensorDataReceiverThread("sensors")
        self.data_thread.data_received.connect(self.update_ui)
        self.data_thread.start()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        first_row = QVBoxLayout()

        # Temperature
        self.temp_label = QLabel("Temperature: 0°C")
        first_row.addWidget(self.temp_label)

        # Pressure
        self.pressure_label = QLabel("Pressure: 0 hPa")
        first_row.addWidget(self.pressure_label)

        # Depth
        self.depth_label = QLabel("Depth: 0 m")
        first_row.addWidget(self.depth_label)

        main_layout.addLayout(first_row)
        self.setLayout(main_layout)

    def update_ui(self, data):
        """Update labels with real-time sensor data."""
        self.temp_label.setText(f"Temperature: {data['temperature']}°C")
        self.pressure_label.setText(f"Pressure: {data['pressure']} hPa")
        self.depth_label.setText(f"Depth: {data['depth']} m")

    def closeEvent(self, event):
        """Stop the data thread when closing the window."""
        self.data_thread.stop()
        self.data_thread.wait()
        super().closeEvent(event)

