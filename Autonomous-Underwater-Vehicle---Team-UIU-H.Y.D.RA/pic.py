import sys
import cv2
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer


class CameraViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dual Camera Feed")

        # Labels for each camera
        self.cam0_label = QLabel()
        self.cam1_label = QLabel()
        self.cam0_label.setText("Waiting for Camera 0...")
        self.cam1_label.setText("Waiting for Camera 1...")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.cam0_label)
        layout.addWidget(self.cam1_label)
        self.setLayout(layout)

        # GStreamer pipelines
        pipeline0 = (
            "udpsrc port=5000 ! application/x-rtp, encoding-name=H264, payload=96 ! "
            "rtph264depay ! avdec_h264 ! videoconvert ! appsink"
        )

        pipeline1 = (
            "udpsrc port=5001 ! application/x-rtp, encoding-name=H264, payload=97 ! "
            "rtph264depay ! avdec_h264 ! videoconvert ! appsink"
        )

        self.cap0 = cv2.VideoCapture(pipeline0, cv2.CAP_GSTREAMER)
        self.cap1 = cv2.VideoCapture(pipeline1, cv2.CAP_GSTREAMER)

        

        # Timers to update feeds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(30)

    def update_frames(self):
        self.show_frame(self.cap0, self.cam0_label)
        self.show_frame(self.cap1, self.cam1_label)

    def show_frame(self, cap, label):
        ret, frame = cap.read()
        if ret:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            label.setPixmap(QPixmap.fromImage(qt_image))
        else:
            label.setText("No feed")


app = QApplication(sys.argv)
viewer = CameraViewer()
viewer.show()
sys.exit(app.exec())
