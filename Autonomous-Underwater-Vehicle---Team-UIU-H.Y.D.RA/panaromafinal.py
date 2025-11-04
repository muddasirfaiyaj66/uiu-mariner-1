import sys
import os
import cv2
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, Qt

# ==== CONFIG ====
FRAME_DIM = (640, 480)  # Set to a lower resolution for preview
DOWNLOADS_PATH = os.path.join(os.path.expanduser("~"), "Downloads")
VIDEO_PATH = os.path.join(DOWNLOADS_PATH, "recorded_video.avi")
FPS = 20.0

GSTREAMER_PIPELINE = (
    "udpsrc port=5001 caps=\"application/x-rtp, media=video, encoding-name=H264, payload=96\" ! "
    "rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! appsink"
)
# =================


class VideoRecorder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Recorder with Preview")
        self.setGeometry(300, 200, 700, 550)

        # Layout
        self.layout = QVBoxLayout()
        self.preview_label = QLabel("Live Preview")
        self.preview_label.setFixedSize(*FRAME_DIM)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.preview_label)

        self.record_button = QPushButton("Start Recording")
        self.record_button.clicked.connect(self.toggle_recording)
        self.layout.addWidget(self.record_button)

        self.setLayout(self.layout)

        # Video Capture
        self.cap = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            self.preview_label.setText("❌ Unable to open video stream.")
            self.record_button.setEnabled(False)
            return

        # Timer to show preview
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(30)  # 30ms = ~33 FPS

        self.is_recording = False
        self.out = None

    def update_preview(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame_resized = cv2.resize(frame, FRAME_DIM)
        rgb_image = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        qt_image = QImage(
            rgb_image.data,
            rgb_image.shape[1],
            rgb_image.shape[0],
            rgb_image.strides[0],
            QImage.Format.Format_RGB888
        )
        self.preview_label.setPixmap(QPixmap.fromImage(qt_image))

        if self.is_recording and self.out:
            self.out.write(frame_resized)

    def toggle_recording(self):
        if not self.is_recording:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.out = cv2.VideoWriter(VIDEO_PATH, fourcc, FPS, FRAME_DIM)
            self.is_recording = True
            self.record_button.setText("Stop Recording")
            print("⏺ Started recording.")
        else:
            self.is_recording = False
            if self.out:
                self.out.release()
                self.out = None
            self.record_button.setText("Start Recording")
            print(f"💾 Video saved to: {VIDEO_PATH}")

    def closeEvent(self, event):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        if self.out:
            self.out.release()
        cv2.destroyAllWindows()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoRecorder()
    window.show()
    sys.exit(app.exec())
