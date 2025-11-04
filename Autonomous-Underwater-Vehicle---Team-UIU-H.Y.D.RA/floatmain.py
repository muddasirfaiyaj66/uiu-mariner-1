
import sys
import re
import serial
from serial import SerialException
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QFrame, QTabWidget
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
import pyqtgraph as pg
import csv
import os


class FloatDashboard(QWidget):
    def __init__(self, port='/dev/ttyACM0', baudrate=9600):
        super().__init__()
        self.setWindowTitle("MATE FLOAT DASHBOARD")
        self.setGeometry(100, 100, 1920, 1080)
        self.setStyleSheet(self.load_stylesheet())

        self.port_name = port
        self.baudrate = baudrate
        self.serial_port = None
        self.serial_connected = False

        self.dive_index = -1
        self.dive_data = []
        self.graph_tabs = QTabWidget()
        self.line_counter = 0

        self.initUI()
        self.initData()

        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.checkSerialConnection)
        self.connection_timer.start(1000)

    def initUI(self):
        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        title = QLabel("MATE FLOAT DASHBOARD")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #ff9900")

        self.telemetry_button = QPushButton("START TELEMETRY")
        self.telemetry_button.clicked.connect(self.toggleTelemetry)
        self.telemetry_button.setObjectName("telemetryButton")

        self.emergency_button = QPushButton("EMERGENCY STOP")
        self.emergency_button.clicked.connect(self.emergencyStop)
        self.emergency_button.setObjectName("emergencyButton")

        comm_status = QFrame()
        comm_status.setObjectName("statusFrame")
        comm_status_layout = QVBoxLayout(comm_status)
        stat_title = QLabel("FLOAT COMM STATUS")
        stat_title.setStyleSheet("color: gray; font-size: 10px;")
        self.stat_label = QLabel("DISCONNECTED")
        self.stat_label.setStyleSheet("color: red; font-size: 16px;")
        self.ip_label = QLabel("NO SERIAL PORT")
        self.ip_label.setStyleSheet("color: gray; font-size: 10px;")
        comm_status_layout.addWidget(stat_title)
        comm_status_layout.addWidget(self.stat_label)
        comm_status_layout.addWidget(self.ip_label)

        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(self.telemetry_button)
        top_layout.addWidget(self.emergency_button)
        top_layout.addWidget(comm_status)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.graph_tabs)

        sensor_layout = QHBoxLayout()
        self.temp_label = QLabel("Temperature: -- °C")
        self.pressure_label = QLabel("Pressure: -- mbar")
        self.altitude_label = QLabel("Altitude: -- m")

        for label in [self.temp_label, self.pressure_label, self.altitude_label]:
            label.setStyleSheet("color: white; font-size: 14px;")
            sensor_layout.addWidget(label)

        table_title = QLabel("Live Data From Sensors")
        table_title.setStyleSheet("color: gray; font-size: 12px;")
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Team ID", "Time", "Temp (°C)", "Altitude (m)", "Pressure (Pa)"])
        self.table.setStyleSheet("background-color: #121212; color: white; border: 1px solid #2e2e2e;")

        main_layout.addLayout(sensor_layout)
        main_layout.addWidget(table_title)
        main_layout.addWidget(self.table)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTelemetry)

    def initData(self):
        self.team_id = "PN06"
        self.line_counter = 0
        self.current_dive = {"x": [], "p": [], "a": []}

    def toggleTelemetry(self):
        if self.timer.isActive():
            self.timer.stop()
            self.telemetry_button.setText("START TELEMETRY")
        else:
            self.timer.start(1000)
            self.telemetry_button.setText("STOP TELEMETRY")

    def emergencyStop(self):
        self.timer.stop()
        self.telemetry_button.setText("START TELEMETRY")
        print("!!! EMERGENCY STOP !!!")

    def updateTelemetry(self):
        self.read_serial()

    def read_serial(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                while self.serial_port.in_waiting:
                    line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    print("Received:", line)

                    match = re.search(
                        r"Time:\s*(\d+)\s*s\s*\|\s*Temp:\s*([-+]?[0-9]*\.?[0-9]+)\s*°C\s*\|\s*Pressure:\s*([-+]?[0-9]*\.?[0-9]+)\s*mbar\s*\|\s*Alt:\s*([-+]?[0-9]*\.?[0-9]+)",
                        line
                    )

                    if match:
                        _, temp_str, pressure_str, altitude_str = match.groups()
                        temp = float(temp_str)
                        pressure = float(pressure_str)
                        altitude = float(altitude_str)

                        self.temp_label.setText(f"Temperature: {temp:.2f} °C")
                        self.pressure_label.setText(f"Pressure: {pressure:.2f} mbar")
                        self.altitude_label.setText(f"Altitude: {altitude:.2f} m")

                        self.line_counter += 1
                        self.current_dive["x"].append(self.line_counter)
                        self.current_dive["p"].append(pressure)
                        self.current_dive["a"].append(altitude)

                        timestamp = datetime.now().strftime("%H:%M:%S")
                        row = self.table.rowCount()
                        self.table.insertRow(row)
                        self.table.setItem(row, 0, QTableWidgetItem(self.team_id))
                        self.table.setItem(row, 1, QTableWidgetItem(timestamp))
                        self.table.setItem(row, 2, QTableWidgetItem(f"{temp:.2f}"))
                        self.table.setItem(row, 3, QTableWidgetItem(f"{altitude:.2f}"))
                        self.table.setItem(row, 4, QTableWidgetItem(f"{pressure:.2f}"))
                        self.table.scrollToBottom()

                        if self.line_counter == 45:
                            self.saveDiveToCSV()
                            self.addGraphTab()
                            self.resetDiveData()

            except Exception as e:
                print("Error parsing serial data:", e)

    def saveDiveToCSV(self):
        filename = f"dive_{self.dive_index + 2}.csv"
        try:
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Time Index", "Pressure (mbar)", "Altitude (m)"])
                for i in range(len(self.current_dive["x"])):
                    writer.writerow([self.current_dive["x"][i], self.current_dive["p"][i], self.current_dive["a"][i]])
            print(f"Saved: {filename}")
        except Exception as e:
            print("CSV save error:", e)

    def addGraphTab(self):
        self.dive_index += 1
        plot_widget = pg.PlotWidget(title=f"Dive {self.dive_index + 1}")
        plot_widget.setBackground("#202020")
        plot_widget.plot(self.current_dive["x"], self.current_dive["p"], pen=pg.mkPen('#ff9900', width=2), name="Pressure")
        plot_widget.plot(self.current_dive["x"], self.current_dive["a"], pen=pg.mkPen('#00aaff', width=2), name="Altitude")
        self.graph_tabs.addTab(plot_widget, f"Dive {self.dive_index + 1}")

    def resetDiveData(self):
        self.line_counter = 0
        self.current_dive = {"x": [], "p": [], "a": []}
        self.table.setRowCount(0)

    def checkSerialConnection(self):
        if self.serial_port is None or not self.serial_port.is_open:
            try:
                self.serial_port = serial.Serial(self.port_name, self.baudrate, timeout=1)
                print("Serial connected.")
            except SerialException:
                self.serial_port = None

        if self.serial_port and self.serial_port.is_open:
            self.stat_label.setText("CONNECTED")
            self.stat_label.setStyleSheet("color: #ff9900; font-size: 16px;")
            self.ip_label.setText(f"CONNECTED TO: {self.serial_port.port}")
        else:
            self.stat_label.setText("DISCONNECTED")
            self.stat_label.setStyleSheet("color: red; font-size: 16px;")
            self.ip_label.setText("NO SERIAL PORT")

    def load_stylesheet(self):
        return """
        QWidget {
            background-color: #121212;
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
        }
        QPushButton#telemetryButton {
            background-color: #292929;
            color: white;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 6px 12px;
        }
        QPushButton#telemetryButton:hover {
            background-color: #ff9900;
            color: black;
        }
        QPushButton#emergencyButton {
            background-color: red;
            color: white;
            font-weight: bold;
            border-radius: 6px;
            padding: 6px 12px;
        }
        QTableWidget {
            gridline-color: #2e2e2e;
            border-radius: 8px;
        }
        QHeaderView::section {
            background-color: #1e1e1e;
            color: #aaa;
            padding: 4px;
            border: none;
        }
        QFrame#statusFrame {
            border: 1px solid #2e2e2e;
            border-radius: 12px;
            padding: 10px;
            background-color: #1a1a1a;
        }
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FloatDashboard()
    window.show()
    sys.exit(app.exec())