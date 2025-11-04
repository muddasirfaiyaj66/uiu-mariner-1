# import pygame
# import socket
# import time

# # ========== CONFIG ==========
# SERVER_IP = "10.42.0.185"  # Change this to your Pixhawk server IP
# SERVER_PORT = 7000
# DEADZONE = 0.1
# COMMAND_DELAY = 0.05  # seconds
# # ============================

# def clamp_pwm(value):
#     return max(1000, min(2000, int(value)))

# def main():
#     pygame.init()
#     pygame.joystick.init()

#     if pygame.joystick.get_count() == 0:
#         print("No joystick found.")
#         return

#     joystick = pygame.joystick.Joystick(0)
#     joystick.init()
#     print(f"Joystick detected: {joystick.get_name()}")

#     # Connect to Pixhawk server
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     try:
#         sock.connect((SERVER_IP, SERVER_PORT))
#         print("Connected to MAVProxy server.")
#     except Exception as e:
#         print(f"Connection failed: {e}")
#         return

#     last_command_time = time.time()
#     last_rc = {i: 1500 for i in range(1, 9)}

#     try:
#         while True:
#             pygame.event.pump()

#             axis_0 = joystick.get_axis(0)  # Left/Right
#             axis_1 = joystick.get_axis(1)  # Forward/Backward
#             axis_3 = joystick.get_axis(3)  # Up/Down

#             rc = last_rc.copy()

#             # Forward/Backward (RC 1 & 8)
#             if axis_1 > DEADZONE:
#                 pwm = int(axis_1 * 450)
#                 rc[1] = 1500 - pwm
#                 rc[8] = 1500 + pwm
#             elif axis_1 < -DEADZONE:
#                 pwm = int(abs(axis_1) * 450)
#                 rc[1] = 1500 + pwm
#                 rc[8] = 1500 - pwm
#             else:
#                 rc[1], rc[8] = 1500, 1500

#             # Left/Right (RC 2 & 5)
#             if axis_0 > DEADZONE:
#                 pwm = int(axis_0 * 450)
#                 rc[2] = 1500 + pwm
#                 rc[5] = 1500 - pwm
#             elif axis_0 < -DEADZONE:
#                 pwm = int(abs(axis_0) * 450)
#                 rc[2] = 1500 - pwm
#                 rc[5] = 1500 + pwm
#             else:
#                 rc[2], rc[5] = 1500, 1500

#             # Up/Down (RC 3, 4, 6, 7)
#             if axis_3 > DEADZONE:
#                 pwm = int(axis_3 * 450)
#                 rc[3] = rc[4] = 1500 + pwm
#                 rc[6] = rc[7] = 1500 - pwm
#             elif axis_3 < -DEADZONE:
#                 pwm = int(abs(axis_3) * 450)
#                 rc[3] = rc[4] = 1500 - pwm
#                 rc[6] = rc[7] = 1500 + pwm
#             else:
#                 rc[3], rc[4], rc[6], rc[7] = 1500, 1500, 1500, 1500

#             # Clamp and send only changed values
#             now = time.time()
#             if now - last_command_time > COMMAND_DELAY:
#                 for ch in rc:
#                     rc[ch] = clamp_pwm(rc[ch])
#                     if rc[ch] != last_rc[ch]:
#                         cmd = f"rc {ch} {rc[ch]}"
#                         try:
#                             sock.sendall((cmd + "\n").encode())
#                             print(f"Sent: {cmd}")
#                         except Exception as e:
#                             print(f"Send error: {e}")
#                         last_rc[ch] = rc[ch]
#                 last_command_time = now

#             time.sleep(0.01)

#     except KeyboardInterrupt:
#         print("Exiting and resetting all RC to 1500...")
#         for ch in last_rc:
#             sock.sendall(f"rc {ch} 1500\n".encode())
#         sock.close()

# if __name__ == "__main__":
#     main()




































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
        self.setWindowTitle("Chungi pungi")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()
        self.label = QLabel("Use joystick to send RC commands.\n"
                            "Axis 0: Left/Right\n"
                            "Axis 1: Forward/Backward\n"
                            "Axis 3: Up/Down\n"
                            "Button 0: Reset\n"
                            "Button 1: Close Arm\n"
                            "Button 9: Stop Everything")
        layout.addWidget(self.label)
        self.setLayout(layout)

    def send_command(self, command):
        HOST = "10.42.0.185"  # Update this if needed
        PORT = 7000

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((HOST, PORT))
                client_socket.sendall(command.encode())
                print(f"Sent: {command}")
        except Exception as e:
            print(f"Error: {e}")

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
        """Read joystick input and send appropriate RC commands"""
        if not self.joystick:
            return
  
        pygame.event.pump()

        # Axis values
        axis_0 = self.joystick.get_axis(0)  # Left/Right
        axis_1 = self.joystick.get_axis(1)  # Forward/Backward
        axis_5 = self.joystick.get_axis(3)  # Up/Down
        # axis_3 = self.joystick.get_axis(3)  # Assuming Axis 3 is for backward tilt
        axis_4 = self.joystick.get_axis(4)  # Assuming Axis 4 is for forward tilt

        # Button states

        reset_button = self.joystick.get_button(0)  # Reset Hover
        stop_button = self.joystick.get_button(9)  # Stop everything
        send_arm = self.joystick.get_button(0)  # Arm/Disarm
        close_arm = self.joystick.get_button(1)  # Close Arm

        commands = []


        if axis_1 > 0.03:  # BACKWARD (was originally FORWARD)
            axis_1_abs = abs(axis_1)
            thrust = int(1500 - (axis_1_abs * 450))  # Goes down to 1000
            anti_thrust = int(1500 + (axis_1_abs * 450))  # Goes up to 2000
            commands.append(f"rc 1 {thrust}")        # CW
            commands.append(f"rc 8 {anti_thrust}")   # Inverted again

        elif axis_1 < -0.03:  # FORWARD (was originally BACKWARD)
            axis_1_abs = abs(axis_1)
            thrust = int(1500 + (axis_1_abs * 450))  # Goes up to 2000
            anti_thrust = int(1500 - (axis_1_abs * 450))  # Goes down to 1000
            commands.append(f"rc 1 {thrust}")        # This spins ACW as expected
            commands.append(f"rc 8 {anti_thrust}")   # Inverted because it's mounted opposite

        else:
            # Neutral when joystick is centered
            commands.append(f"rc 1 1500")
            commands.append(f"rc 8 1500")






        # Left/Right (Axis 0): Right = axis_0 > 0.03, Left = axis_0 < -0.03
        if axis_0 > 0.03:  # RIGHT TURN
            axis_0_abs = abs(axis_0)
            power = int(1500 + (axis_0_abs * 500))  # Max 2000
            reverse_power = int(1500 - (axis_0_abs * 500))  # Min 1000
            commands.append(f"rc 2 {reverse_power}")  # Clockwise
            commands.append(f"rc 5 {reverse_power}")          # Anti-clockwise

        elif axis_0 < -0.03:  # LEFT TURN
            axis_0_abs = abs(axis_0)
            power = int(1500 + (axis_0_abs * 500))  # Max 2000
            reverse_power = int(1500 - (axis_0_abs * 500))  # Min 1000
            commands.append(f"rc 2 {power}")         # Anti-clockwise
            commands.append(f"rc 5 {power}") # Clockwise

        else:
            commands.append(f"rc 2 1500")
            commands.append(f"rc 5 1500")

            


        MOTOR_NEUTRAL = 1500
        MOTOR_MAX = 2000
        MOTOR_MIN = 1000



        if axis_5 > 0.03:  # DOWN
            axis_5_abs = abs(axis_5)
            thrust = int(1500 - (axis_5_abs * 450))  # CCW
            thrust2 = int(1500 + (axis_5_abs * 450)) # CW

            commands.append(f"rc 3 {thrust2}")     # CCW
            commands.append(f"rc 4 {thrust2}")    # CW
            commands.append(f"rc 6 {thrust}")     # CCW
            commands.append(f"rc 7 {thrust}")     # CCW

        elif axis_5 < -0.03:  # UP
            axis_5_abs = abs(axis_5)
            thrust = int(1500 + (axis_5_abs * 450))  # CW
            thrust2 = int(1500 - (axis_5_abs * 450)) # CCW

            commands.append(f"rc 3 {thrust2}")     # CW
            commands.append(f"rc 4 {thrust2}")    # CCW
            commands.append(f"rc 6 {thrust}")     # CW
            commands.append(f"rc 7 {thrust}")     # CW

        else:
            commands.append(f"rc 3 {MOTOR_NEUTRAL}")
            commands.append(f"rc 4 {MOTOR_NEUTRAL}")
            commands.append(f"rc 6 {MOTOR_NEUTRAL}")
            commands.append(f"rc 7 {MOTOR_NEUTRAL}")




    
        # Stop Everything
        if stop_button:
            self.stop_all()
            return  # Stop here to avoid sending more joystick commands


        # Send commands
        for command in commands:
            if command not in self.active_commands:
                self.active_commands.append(command)
            self.send_command(command)

    def stop_all(self):
        """Force stop all thrusters and clear active command buffer"""
        stop_commands = [
            "rc 1 1500", "rc 2 1500", "rc 3 1500", "rc 4 1500",
            "rc 5 1500", "rc 6 1500", "rc 7 1500", "rc 8 1500"
        ]
        for command in stop_commands:
            self.send_command(command)
        self.active_commands.clear()
        print("All thrusters stopped and buffer cleared.")


    def reset_commands(self):
        """Reset all RC commands"""
        reset_commands = ["rc 1 1500", "rc 2 1500", "rc 3 1500", "rc 4 1500",
                          "rc 5 1500", "rc 6 1500", "rc 8 1500"]
        for command in reset_commands:
            self.send_command(command)
        self.active_commands.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MAVProxyClient()
    window.show()
    sys.exit(app.exec())