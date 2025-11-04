import time
import numpy as np
import psutil
import socket
import serial
import cv2
import pygame
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QProgressBar,
    QSpacerItem,
    QSizePolicy,
    QSlider,
    QFrame,
    QGraphicsOpacityEffect
)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QBrush, QColor, QPainterPath, QKeyEvent, QPixmap
from PyQt6.QtCore import Qt, QRectF, QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QThread
import cv2


# class ArmThread(QThread):
#     def __init__(self, parent = None):
#         super().__init__(parent)
#         self.worker = ArmController()

#     def run(self):
#         try:
#             self.worker.run()
#         except Exception as e:
#             print(f"Arm Controller Error: {e}")
            
#     def stop(self):
#         self.worker.stop()
#         self.quit()
#         self.wait()

class CameraWorker(QThread):
    frame_ready = pyqtSignal(object)  # Signal to send frame to GUI

    def __init__(self, pipeline, parent=None):
        super().__init__(parent)
        self.pipeline = pipeline
        self.running = True
        # self.joystick_name = self.joystick_init()

    def run(self):
        cap = cv2.VideoCapture(self.pipeline, cv2.CAP_GSTREAMER)

        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                self.frame_ready.emit(frame)
        cap.release()

    def stop(self):
        self.running = False
        self.wait()



class ControlPage(QWidget):
    def __init__(self, parent=None):
        
        super().__init__(parent)
        self.init_ui()
        self.active_commands = []  # Store active commands
        self.joystick_init()  # Initialize joystick
        self.timer = QTimer(self)  
        self.timer.timeout.connect(self.read_joystick)  
        self.timer.start(100)  # Read joystick every 50ms
        self.last_command_time = 0
        self.command_delay = 0.1 
        self.joystick_ready_time = time.time() + 1.5



        self.mav_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.mav_socket.connect(("10.42.0.185", 7000))
            print("✅ Connected to MAVProxy server")
        except Exception as e:
            print(f"❌ Could not connect to MAVProxy server: {e}")



    def init_ui(self):
        main_layout = QVBoxLayout(self) 

        main_row = QHBoxLayout()

        frame_buttonLayout = QVBoxLayout()
        
        self.small_frame = QLabel()
        self.small_frame.setStyleSheet(" border: 1px solid #005767; border-radius: 20px; margin-bottom: 10px;")
        self.small_frame.setFixedSize(384, 216)

        camerabtn_label = QLabel("SWITCH CAMERAS")
        camerabtn_label.setStyleSheet("""color: white; font-size: 12px; font-weight: bold; margin-top: 20px;""")
        opacity_effect = QGraphicsOpacityEffect()
        camerabtn_label.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0.6)  # Set opacity for the label

        camera01_btn = QPushButton("Camera 01")
        camera01_btn.setFixedSize(150, 50)
        camera01_btn.setStyleSheet("""
            background-color: transparent;
            color: white;
            font-size: 10px;
            padding: 5px;
            border: 1px solid #FF8800;
            border-radius: 5px;
            margin-top: 10px;
            
        """)

        camera02_btn = QPushButton("CAMERA ON")
        camera02_btn.setFixedSize(150, 50)
        camera02_btn.setStyleSheet("""
            background-color: transparent;
            color: white;
            font-size: 10px;
            padding: 5px;
            border: 1px solid #FF8800;
            border-radius: 5px;
            margin-top: 10px;
            
        """)

        frame_buttonLayout.addWidget(self.small_frame)
        frame_buttonLayout.addWidget(camerabtn_label)
        frame_buttonLayout.addWidget(camera01_btn)
        frame_buttonLayout.addWidget(camera02_btn)
        frame_buttonLayout.addStretch()


        # Main camera display
        self.main_camera = QLabel()
        self.main_camera.setFixedSize(960, 540)
        self.main_camera.setStyleSheet(" border: 1px solid #005767; border-radius: 20px;")


        # Thrusters and Status
        thrusterstatus_layout = QVBoxLayout()


        status_container = QWidget()
        status_container.setStyleSheet("""
            background-color: #181818;
            border: 1px solid #0D363E;
            border-radius: 10px;
            padding: 10px;
        """)
        container_layout = QVBoxLayout()

        # Create and style the label inside
        status_label = QLabel("Communication Status")
        status_label.setStyleSheet("""
            color: white;
            font-size: 8px;
            border: none;
        """)
        conn_label = QLabel("CONNECTED")
        conn_label.setStyleSheet("""
            color: #FF8800;
            font-size: 20px;
            height: 30px;
            border: none;
        """)
        ip_label = QLabel("IP ADDRESS: 192.168.2.3")
        ip_label.setStyleSheet("""
            color: white;
            font-size: 8px;
            border: none;
        """)
        container_layout.addWidget(status_label)
        container_layout.addWidget(conn_label)
        container_layout.addWidget(ip_label)
        status_container.setLayout(container_layout)
        status_container.setFixedSize(400, 130)


        # Create thruster buttons
        control_status = QWidget()
        control_status.setStyleSheet("""
            background-color:
            #181818;
            border: 1px solid #0D363E;
            border-radius: 10px;
            padding: 10px;
        """)

        control_layout = QVBoxLayout()

        main_label = QLabel("DIRECTION")
        main_label.setStyleSheet("""
            color: white;
            font-size: 8px;
            border: none;
        """)

        dir_status = QLabel("NEUTRAL")
        dir_status.setStyleSheet("""
            color: #FF8800;
            font-size: 20px;
            border: none;
        """)

        
        up_label = QLabel("UP/DOWN")
        up_label.setStyleSheet("""
            color: white;
            font-size: 8px;
            border: none;
        """)

        thruster2_Layout = QHBoxLayout()
        thruster2_label = QLabel("THRUSTER 2")
        thruster2_label.setStyleSheet("""
            color: white;
            border: none;
        """)
        thruster2 = QLabel("0")
        thruster2.setStyleSheet("""
            color: #FF8800;
        """)
        thruster2_Layout.addWidget(thruster2_label)
        thruster2_Layout.addWidget(thruster2)

        thruster3_layout = QHBoxLayout()
        thruster3_label = QLabel("THRUSTER 3")
        thruster3_label.setStyleSheet("""
            color: white;
            border: none;
        """)
        thruster3_value = QLabel("0")
        thruster3_value.setStyleSheet("""
            color: #FF8800;

        """)
        thruster3_layout.addWidget(thruster3_label)
        thruster3_layout.addWidget(thruster3_value)

        thruster6_layout = QHBoxLayout()
        thruster6_label = QLabel("THRUSTER 6")
        thruster6_label.setStyleSheet("""
            color: white;
            border: none;
        """)
        thruster6_value = QLabel("0")
        thruster6_value.setStyleSheet("""
            color: #FF8800;
        """)
        thruster6_layout.addWidget(thruster6_label)
        thruster6_layout.addWidget(thruster6_value)

        thruster7_layout = QHBoxLayout()
        thruster7_label = QLabel("THRUSTER 7")
        thruster7_label.setStyleSheet("""
            border: none;
        """)
        thruster7_value = QLabel("0")
        thruster7_value.setStyleSheet("""
            color: #FF8800;

        """)
        thruster7_layout.addWidget(thruster7_label)
        thruster7_layout.addWidget(thruster7_value)

        fwd_label = QLabel("FORWARD/BACKWARD")
        fwd_label.setStyleSheet("""
            font-size: 8px;
            border: none;
        """)

        # Thruster 1
        thruster1_layout = QHBoxLayout()
        thruster1_label = QLabel("THRUSTER 1")
        thruster1_label.setStyleSheet("""
            color: white;
            border: none;
        """)
        thruster1_value = QLabel("0")
        thruster1_value.setStyleSheet("""
            color: #FF8800;
        """)
        thruster1_layout.addWidget(thruster1_label)
        thruster1_layout.addWidget(thruster1_value)

        # Thruster 4
        thruster4_layout = QHBoxLayout()
        thruster4_label = QLabel("THRUSTER 4")
        thruster4_label.setStyleSheet("""
            color: white;
            border: none;
        """)
        thruster4_value = QLabel("0")
        thruster4_value.setStyleSheet("""
            color: #FF8800;
        """)
        thruster4_layout.addWidget(thruster4_label)
        thruster4_layout.addWidget(thruster4_value)

        # Thruster 5
        thruster5_layout = QHBoxLayout()
        thruster5_label = QLabel("THRUSTER 5")
        thruster5_label.setStyleSheet("""
            color: white;
            border: none;
        """)
        thruster5_value = QLabel("0")
        thruster5_value.setStyleSheet("""
            color: #FF8800;
        """)
        thruster5_layout.addWidget(thruster5_label)
        thruster5_layout.addWidget(thruster5_value)

        # Thruster 8
        thruster8_layout = QHBoxLayout()
        thruster8_label = QLabel("THRUSTER 8")
        thruster8_label.setStyleSheet("""
            color: white;
            border: none;
        """)
        thruster8_value = QLabel("0")
        thruster8_value.setStyleSheet("""
            color: #FF8800;
        """)
        thruster8_layout.addWidget(thruster8_label)
        thruster8_layout.addWidget(thruster8_value)


        control_layout.addWidget(main_label)
        control_layout.addWidget(dir_status)
        control_layout.addWidget(up_label)

        control_layout.addLayout(thruster2_Layout)
        control_layout.addLayout(thruster3_layout)
        control_layout.addLayout(thruster6_layout)
        control_layout.addLayout(thruster7_layout)

        control_layout.addWidget(fwd_label)
        control_layout.addLayout(thruster1_layout)
        control_layout.addLayout(thruster4_layout)
        control_layout.addLayout(thruster5_layout)
        control_layout.addLayout(thruster8_layout)
        


        control_status.setLayout(control_layout)

        thrusterstatus_layout.addWidget(status_container)
        thrusterstatus_layout.addWidget(control_status)
        thrusterstatus_layout.addStretch()


        main_row.addLayout(frame_buttonLayout)
        main_row.addWidget(self.main_camera, alignment=Qt.AlignmentFlag.AlignTop)
        main_row.addLayout(thrusterstatus_layout)
        

        main_row.addStretch()

        second_row = QHBoxLayout()

        sensor_layout = QVBoxLayout()
        
        sensor_label = QLabel("SENSORS")
        sensor_label.setStyleSheet("""font-size: 12px; font-weight: bold; color: white; margin-bottom: 40px;""")
        
        depth_layout = QHBoxLayout()
        depth_label = QLabel("DEPTH")
        depth_value = QLabel("0 m")
        depth_value.setStyleSheet("border: 1px solid #0D363E; border-radius: 5px; padding: 10px; color: #FF8800;")
        depth_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        depth_label.setStyleSheet("color: white; font-size: 8px;")
        depth_layout.addWidget(depth_label)
        depth_layout.addWidget(depth_value)

        temp_layout = QHBoxLayout()
        temp_label = QLabel("TEMPERATURE")
        temp_value = QLabel("0 °C")
        temp_value.setStyleSheet("border: 1px solid #0D363E; border-radius: 5px; padding: 10px; color: #FF8800;")
        temp_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(temp_value)

        pressure_layout = QHBoxLayout()
        pressure_label = QLabel("PRESSURE")
        pressure_value = QLabel("0 Pa")
        pressure_value.setStyleSheet("border: 1px solid #0D363E; border-radius: 5px; padding: 10px; color: #FF8800;")
        pressure_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pressure_layout.addWidget(pressure_label)
        pressure_layout.addWidget(pressure_value)

        sensor_layout.addWidget(sensor_label)
        sensor_layout.addLayout(depth_layout)
        sensor_layout.addLayout(temp_layout)
        sensor_layout.addLayout(pressure_layout)
        sensor_layout.addStretch()

        #leak and Emergency Alarm

        alarm_layout = QVBoxLayout()

        leak_label = QLabel("LEAK ALARM")
        leak_label.setStyleSheet("color: 4F4F4F; background: #4F4F4F; font-size: 10px;border-radius: 50px; padding: 10px; color: white;")
        leak_label.setFixedSize(100, 100)
        leak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        emergency_label = QPushButton("EMERGENCY")
        emergency_label.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 10px; color: red; font-size: 10px; background-color: transparent;")


        alarm_layout.addWidget(leak_label)
        alarm_layout.addWidget(emergency_label) 
        alarm_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        joystick_layout = QVBoxLayout()
        image1_label = QLabel()
        pixmap1 = QPixmap("Autonomous-Underwater-Vehicle---Team-UIU-H.Y.D.RA/assets/joystick.png")  
        image1_label.setPixmap(pixmap1)

        joystick_layout2 = QVBoxLayout()
        image2_label = QLabel()
        pixmap2 = QPixmap("Autonomous-Underwater-Vehicle---Team-UIU-H.Y.D.RA/assets/joystick.png")  
        image2_label.setPixmap(pixmap1)

        label1 = QLabel("ARM JOYSTICK")
        label1.setStyleSheet("font-size: 10px;")
        conn_joystick1 = QLabel("XBox 360 Controller")
        conn_joystick1.setStyleSheet("font-size: 20px; color: #FF8800")

        label2 = QLabel("ARM JOYSTICK")
        label2.setStyleSheet("font-size: 10px;")
        conn_joystick2 = QLabel("XBox 360 Controller")
        conn_joystick2.setStyleSheet("font-size: 20px; color: #FF8800")

        joystick_layout.addWidget(image1_label)
        joystick_layout.addWidget(label1)
        joystick_layout.addWidget(conn_joystick1)

        joystick_layout2.addWidget(image2_label)
        joystick_layout2.addWidget(label2)
        joystick_layout2.addWidget(conn_joystick2)

        taske_layout = QVBoxLayout()
        

        
        second_row.addLayout(sensor_layout)
        second_row.addLayout(alarm_layout)
        second_row.addLayout(joystick_layout)
        second_row.addLayout(joystick_layout2)
        
        # Add rows to main layout
        main_layout.addLayout(main_row)
        main_layout.addLayout(second_row)
        main_layout.addStretch()


    def start_video_threads(self):
        pipeline0 = (
            "udpsrc port=5000 ! application/x-rtp, encoding-name=H264, payload=96 ! "
            "rtph264depay ! avdec_h264 ! videoconvert ! appsink"
        )

        pipeline1 = (
            "udpsrc port=5001 ! application/x-rtp, encoding-name=H264, payload=97 ! "
            "rtph264depay ! avdec_h264 ! videoconvert ! appsink"
        )

        self.cam0_worker = CameraWorker(pipeline0)
        self.cam1_worker = CameraWorker(pipeline1)

        self.cam0_worker.frame_ready.connect(lambda f: self.display_frame(f, self.small_frame))
        self.cam1_worker.frame_ready.connect(lambda f: self.display_frame(f, self.main_camera))

        self.cam0_worker.start()
        self.cam1_worker.start()



    def display_frame(self, frame, label):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(qt_image))

    


    def setup_camera_connections(self):
        self.camera01_btn.clicked.connect(self.switch_cameras)
        self.camera02_btn.clicked.connect(self.switch_cameras)







    def send_command(self, command):
        try:
            self.mav_socket.sendall((command + "\n").encode())
            print(f"Sent: {command}")
        except Exception as e:
            print(f"❌ Failed to send command: {e}")


    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input"""
        key_map = {
            Qt.Key.Key_W: ["rc 3 1000", "rc 4 1000"],  # Forward
            Qt.Key.Key_S: ["rc 3 2000", "rc 4 2000"],  # Backward
            Qt.Key.Key_A: ["rc 1 2000", "rc 2 2000"],  # Left
            Qt.Key.Key_D: ["rc 1 1000", "rc 2 1000"],  # Right
            Qt.Key.Key_Up: ["rc 5 1000", "rc 6 1000"],  # Up Tilt
            Qt.Key.Key_Down: ["rc 5 2000", "rc 6 2000"],  # Down Tilt
            Qt.Key.Key_U: ["rc 5 1000", "rc 8 2000"],  # Up Normal
        }

        if event.key() in key_map:
            commands = key_map[event.key()]
            for command in commands:
                if command not in self.active_commands:
                    self.active_commands.append(command)
                self.send_command(command)
                self.last_command_time = time.time()

        elif event.key() == Qt.Key.Key_Q:  # Reset command
            self.reset_commands()

            
    # def joystick_init(self):
    #     """Initialize only the Zikway HID gamepad"""
    #     pygame.init()
    #     pygame.joystick.init()
        
    #     found = False
    #     for i in range(pygame.joystick.get_count()):
    #         joystick = pygame.joystick.Joystick(i)
    #         joystick.init()
    #         name = joystick.get_name()
    #         print(f"Detected joystick: {name}")
            
    #         if "Zikway" in name:
    #             self.joystick = joystick
    #             found = True
    #             print("✅ Zikway Gamepad Connected!")
    #             break
    #         else:
    #             joystick.quit()  # optional: release non-Zikway joystick

    #     if not found:
    #         self.joystick = None
    #         print("❌ Zikway Gamepad Not Found!")



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

        if time.time() < self.joystick_ready_time:
            return

        pygame.event.pump()

        # Axis values
        axis_0 = self.joystick.get_axis(0)  # Left/Right
        axis_1 = self.joystick.get_axis(1)  # Forward/Backward
        axis_5 = self.joystick.get_axis(3)  # Up/Down
        axis_4 = self.joystick.get_axis(4)  # Forward Tilt

        # Button states
        reset_button = self.joystick.get_button(0)  # Reset Hover
        stop_button = self.joystick.get_button(9)  # Stop everything
        send_arm = self.joystick.get_button(0)  # Arm/Disarm
        close_arm = self.joystick.get_button(1)  # Close Arm

        commands = []

        # Forward/Backward (Axis 1): Forward = axis_1 < -0.03, Backward = axis_1 > 0.03
        if axis_1 > 0.03:  # BACKWARD
            axis_1_abs = abs(axis_1)
            value = int(1500 + (axis_1_abs * 450))  # Goes up to 2000
            reverse_value = int(1500 - (axis_1_abs * 450))  # Goes down to 1000

            commands.append(f"rc 1 {reverse_value}")   # ACW -> backward (1 < 1500)
            commands.append(f"rc 8 {value}")           # CW -> backward (8 > 1500)

        elif axis_1 < -0.03:  # FORWARD
            axis_1_abs = abs(axis_1)
            value = int(1500 + (axis_1_abs * 450))  # Goes up to 2000
            reverse_value = int(1500 - (axis_1_abs * 450))  # Goes down to 1000

            commands.append(f"rc 1 {value}")           # ACW -> forward (1 > 1500)
            commands.append(f"rc 8 {reverse_value}")   # CW -> forward (8 < 1500)

        else:
            commands.append(f"rc 1 1500")
            commands.append(f"rc 8 1500")

        # Left/Right (Axis 0): Right = axis_0 > 0.03, Left = axis_0 < -0.03
        if axis_0 > 0.03:  # RIGHT
            axis_0_abs = abs(axis_0)
            value = int(1500 + (axis_0_abs * 450))  # Both rotate CW ( > 1500 )
            value2 = int(1500 - (axis_0_abs * 450))

            commands.append(f"rc 2 {value}")        # CW
            commands.append(f"rc 5 {value2}")        # CW

        elif axis_0 < -0.03:  # LEFT
            axis_0_abs = abs(axis_0)
            value = int(1500 + (axis_0_abs * 450))  # Both rotate CW ( > 1500 )
            value2 = int(1500 - (axis_0_abs * 450))

            commands.append(f"rc 2 {value2}")        # CW
            commands.append(f"rc 5 {value}")        # CW

        else:
            commands.append(f"rc 2 1500")
            commands.append(f"rc 5 1500")

        # Up/Down (Axis 5): Down = axis_5 > 0.03, Up = axis_5 < -0.03
        if axis_5 > 0.03:  # DOWN
            axis_5_abs = abs(axis_5)
            value = int(1500 + (axis_5_abs * 450))  # > 1500
            value2 = int(1500 - (axis_5_abs * 450))  # < 1500

            commands.append(f"rc 3 {value}")      # ACW
            commands.append(f"rc 4 {value}")        # ACW
            commands.append(f"rc 6 {value2}")        # CW
            commands.append(f"rc 7 {value2}")        # CW

        elif axis_5 < -0.03:  # UP
            axis_5_abs = abs(axis_5)
            value = int(1500 + (axis_5_abs * 450))  # > 1500
            value2 = int(1500 - (axis_5_abs * 450))  # < 1500

            commands.append(f"rc 3 {value2}")        # ACW
            commands.append(f"rc 4 {value2}")        # ACW
            commands.append(f"rc 6 {value}")        # CW
            commands.append(f"rc 7 {value}")        # CW

        else:
            commands.append(f"rc 3 1500")
            commands.append(f"rc 4 1500")
            commands.append(f"rc 6 1500")
            commands.append(f"rc 7 1500")

















        # Reset Hover
        if reset_button:
            commands.append("rc 5 1500")
            commands.append("rc 6 1500")
            commands.append("rc 7 1500")
            commands.append("rc 8 1500")

        # Arm Commands
        if send_arm:
            commands.append("open")
        elif close_arm:
            commands.append("close")

        # Stop Everything
        if stop_button:
            commands.extend([
                "rc 3 1500", "rc 4 1500", "rc 1 1500", "rc 2 1500",
                "rc 5 1500", "rc 6 1500", "rc 8 1500"
            ])

        # Throttle sending commands based on time delay
        current_time = time.time()
        if current_time - self.last_command_time > self.command_delay:
            for command in commands:
                if command not in self.active_commands:
                    self.active_commands.append(command)
                self.send_command(command)
            self.last_command_time = current_time

    def reset_commands(self):
        """Reset all RC commands"""
        reset_commands = ["rc 1 1500", "rc 2 1500", "rc 3 1500", "rc 4 1500",
                          "rc 5 1500", "rc 6 1500", "rc 8 1500"]
        for command in reset_commands:
            self.send_command(command)
        self.active_commands.clear()

    def closeEvent(self, event):
        self.arm_thread.stop()
        event.accept()