import sys
import socket
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal, QObject

# Signal class to update UI from thread
class SensorDataSignal(QObject):
    data_received = pyqtSignal(str, str, str)

# PyQt6 GUI class
class SensorDisplay(QWidget):
    def __init__(self):
        super().__init__()

        # Set up UI
        self.setWindowTitle("Sensor Data Display")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout()
        
        self.temp_label = QLabel("Temperature: -- °C")
        self.press_label = QLabel("Pressure: -- Pa")
        self.alt_label = QLabel("Altitude: -- m")

        self.layout.addWidget(self.temp_label)
        self.layout.addWidget(self.press_label)
        self.layout.addWidget(self.alt_label)

        self.setLayout(self.layout)

        # Create signal instance
        self.signal = SensorDataSignal()
        self.signal.data_received.connect(self.update_labels)

        # Start socket thread
        self.start_client_thread()

    def start_client_thread(self):
        self.thread = threading.Thread(target=self.socket_client, daemon=True)
        self.thread.start()

    def socket_client(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raspberry_pi_ip = "192.168.21.173"  # Change this to your Raspberry Pi's IP
        client.connect((raspberry_pi_ip, 5000))

        while True:
            data = client.recv(1024).decode().strip()
            if data:
                try:
                    temp, press, alt = data.split(",")
                    self.signal.data_received.emit(temp, press, alt)
                except ValueError:
                    continue  # Skip if data is incorrect

    def update_labels(self, temp, press, alt):
        self.temp_label.setText(f"Temperature: {temp} °C")
        self.press_label.setText(f"Pressure: {press} Pa")
        self.alt_label.setText(f"Altitude: {alt} m")

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SensorDisplay()
    window.show()
    sys.exit(app.exec())
