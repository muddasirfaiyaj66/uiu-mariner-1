import sys
import socket
import struct
import pickle
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QThread, pyqtSignal, Qt

class VideoReceiver(QThread):
    frame_received = pyqtSignal(np.ndarray)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.running = True

    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))
        data = b""
        payload_size = struct.calcsize(">L")

        while self.running:
            while len(data) < payload_size:
                packet = client_socket.recv(4096)
                if not packet: return
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = pickle.loads(frame_data)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            self.frame_received.emit(frame)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

class DualCameraApp(QWidget):
    def __init__(self, host='raspberrypi.local'):
        super().__init__()
        self.setWindowTitle("Dual Camera Stream")
        self.label1 = QLabel()
        self.label2 = QLabel()

        self.label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        self.setLayout(layout)

        self.cam1 = VideoReceiver(host, 8000)
        self.cam1.frame_received.connect(self.update_label1)
        self.cam1.start()

        self.cam2 = VideoReceiver(host, 8001)
        self.cam2.frame_received.connect(self.update_label2)
        self.cam2.start()

    def update_label1(self, frame):
        self.label1.setPixmap(self.convert_frame_to_pixmap(frame))

    def update_label2(self, frame):
        self.label2.setPixmap(self.convert_frame_to_pixmap(frame))

    def convert_frame_to_pixmap(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(qimg).scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)

    def closeEvent(self, event):
        self.cam1.stop()
        self.cam2.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = DualCameraApp(host='192.168.125.218')  # Replace with your Raspberry Pi's IP address
    win.resize(700, 1000)
    win.show()
    sys.exit(app.exec())
