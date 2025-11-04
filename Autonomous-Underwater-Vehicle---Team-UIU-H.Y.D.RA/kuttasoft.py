import sys
import socket
import pygame
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer

class MAVProxyClient(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.active_commands = []
        self.joystick_init()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_joystick)
        self.timer.start(50)

    def initUI(self):
        self.setWindowTitle("ROV Joystick Controller")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()
        self.label = QLabel("Use joystick to send RC commands.\n"
                            "Axis 0: Left/Right (Yaw)\n"
                            "Axis 1: Forward/Backward (Surge)\n"
                            "Axis 3: Up/Down (Heave)\n"
                            "Button 0: Reset\n"
                            "Button 1: Close Arm\n"
                            "Button 9: Stop Everything")
        layout.addWidget(self.label)
        self.setLayout(layout)

    def send_command(self, command):
        HOST = "10.42.0.186"  # Update this if needed
        PORT = 7000

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((HOST, PORT))
                client_socket.sendall(command.encode())
                print(f"Sent: {command}")
        except Exception as e:
            print(f"Error: {e}")
            if "No route to host" in str(e):
                print("No route to host! Sending failsafe RC 1500 to all channels (locally)")
                # Locally print or handle failsafe actions
                for i in range(1, 9):
                    print(f"Failsafe (not sent): rc {i} 1500")

            

    def joystick_init(self):
        """Initialize joystick"""
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print("Joystick Connected!")
        else:
            self.joystick = None
            print("No Joystick Found!")
    def read_joystick(self):
        if not self.joystick:
            return

    def read_joystick(self):
        if not self.joystick:
            return

        pygame.event.pump()

        DEADZONE = 0.3

        axis_0 = self.joystick.get_axis(0)  # Left/Right (Yaw)
        axis_1 = self.joystick.get_axis(1)  # Forward/Backward (Surge)
        axis_5 = self.joystick.get_axis(3)  # Up/Down (Heave)

        stop_button = self.joystick.get_button(7)

        commands = []

        # Surge (Forward/Backward)
        if axis_1 > DEADZONE:
            thrust = int(1500 + (abs(axis_1) * 450))
            anti_thrust = int(1500 - (abs(axis_1) * 450))
            commands.append(f"rc 1 {thrust}")
            commands.append(f"rc 8 {anti_thrust}")
        elif axis_1 < -DEADZONE:
            thrust = int(1500 + (abs(axis_1) * 450))
            anti_thrust = int(1500 - (abs(axis_1) * 450))
            commands.append(f"rc 1 {anti_thrust}")
            commands.append(f"rc 8 {thrust}")
            
        else:
            commands.append("rc 1 1500")
            commands.append("rc 8 1500")

        # Yaw (Left/Right)
        if axis_0 > DEADZONE:
            power = int(1500 + (abs(axis_0) * 500))
            reverse_power = int(1500 - (abs(axis_0) * 500))
            commands.append(f"rc 2 {power}")
            commands.append(f"rc 5 {reverse_power}")
        elif axis_0 < -DEADZONE:
            power = int(1500 + (abs(axis_0) * 500))
            reverse_power = int(1500 - (abs(axis_0) * 500))
            commands.append(f"rc 2 {reverse_power}")
            commands.append(f"rc 5 {power}")
        else:
            commands.append("rc 2 1500")
            commands.append("rc 5 1500")

        # Heave (Up/Down)
        if axis_5 > DEADZONE:
            thrust = int(1500 - (abs(axis_5) * 450))
            thrust2 = int(1500 + (abs(axis_5) * 450))


            commands.extend([
                f"rc 3 {thrust}",
                f"rc 4 {thrust2}",
                f"rc 6 {thrust}",
                f"rc 7 {thrust}"
            ])
        elif axis_5 < -DEADZONE:
            thrust = int(1500 + (abs(axis_5) * 450))
            thrust2 = int(1500 - (abs(axis_5) * 450))
            commands.extend([
                f"rc 3 {thrust}",
                f"rc 4 {thrust2}",
                f"rc 6 {thrust}",
                f"rc 7 {thrust}"
            ])
        else:
            commands.extend([
                "rc 4 1500",
                "rc 3 1500",
                "rc 6 1500",
                "rc 7 1500"
            ])

        # Stop Everything
        if stop_button:
            self.stop_all()
            return

        # Send commands
        for command in commands:
            self.send_command(command)

    def stop_all(self):
        stop_commands = [
            "rc 1 1500", "rc 2 1500", "rc 3 1500", "rc 4 1500",
            "rc 5 1500", "rc 6 1500", "rc 7 1500", "rc 8 1500"
        ]
        for command in stop_commands:
            self.send_command(command)
        print("All thrusters stopped.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MAVProxyClient()
    window.show()
    sys.exit(app.exec())