import sys
import serial
import re
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer

class SensorReceiver(QWidget):
    def __init__(self, port='/dev/ttyACM0', baudrate=9600):
        super().__init__()

        # Serial Setup
        self.serial_port = serial.Serial(port, baudrate, timeout=1)

        # UI Setup
        self.setWindowTitle("Sensor Data Monitor")
        layout = QVBoxLayout()

        self.temp_label = QLabel("Temperature: -- °C")
        self.pressure_label = QLabel("Pressure: -- mbar")
        self.altitude_label = QLabel("Altitude: -- m")

        layout.addWidget(self.temp_label)
        layout.addWidget(self.pressure_label)
        layout.addWidget(self.altitude_label)

        self.setLayout(layout)

        # Timer to update data every 500ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)
        self.timer.start(500)

    def read_serial(self):
        if self.serial_port.in_waiting:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                print("Received:", line)

                # Parse only the sensor data line
                match = re.search(r"T:\s*([\d.]+)\s*C\s*\|\s*P:\s*([\d.]+)\s*mbar\s*\|\s*Alt:\s*([\d.]+)", line)
                if match:
                    temp = match.group(1)
                    pressure = match.group(2)
                    altitude = match.group(3)

                    self.temp_label.setText(f"Temperature: {temp} °C")
                    self.pressure_label.setText(f"Pressure: {pressure} mbar")
                    self.altitude_label.setText(f"Altitude: {altitude} m")
            except Exception as e:
                print("Error parsing serial data:", e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SensorReceiver(port='/dev/ttyACM0')  # Replace with your serial port
    window.show()
    sys.exit(app.exec())
