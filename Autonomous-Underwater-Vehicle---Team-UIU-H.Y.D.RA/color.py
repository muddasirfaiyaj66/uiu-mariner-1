import sys
import cv2
import numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

class ColorDetectionApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Color Detection")
        self.setGeometry(100, 100, 1280, 600)

        # Create main layout
        self.layout = QVBoxLayout(self)

        # QLabel for displaying webcam footage
        self.main_cam = QLabel(self)
        self.main_cam.setFixedSize(1260, 440)
        self.layout.addWidget(self.main_cam)

        # Color Detect button
        self.detect_button = QPushButton("Color Detect", self)
        self.layout.addWidget(self.detect_button)

        # Initialize camera
        self.cap = self.initialize_raspberry_pi_camera()
        self.is_detecting = False

        # Define color ranges (HSV)
        self.color_ranges = {
            'Brick': ((0, 100, 100), (10, 255, 255)),
            'Wheat': ((20, 100, 100), (40, 255, 255)),
            'Coal': ((0, 0, 0), (180, 255, 50)),
            'Furnase Sand': ((0, 0, 200), (180, 20, 255)),
        }

        # Setup timer if camera is available
        if self.cap and self.cap.isOpened():
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)  # Refresh every 30 ms
        else:
            print("Error: Could not open video stream.")

        # Connect button
        self.detect_button.clicked.connect(self.toggle_detection)

    def initialize_raspberry_pi_camera(self):
        """Initialize Raspberry Pi Camera using GStreamer."""
        pipeline = (
            "udpsrc port=5000 caps=application/x-rtp,media=video,encoding-name=H264,payload=96 "
            "! rtph264depay ! avdec_h264 ! videoconvert ! appsink"
        )
        cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        return cap if cap.isOpened() else None

    def update_frame(self):
        if not self.cap:
            return
        
        ret, frame = self.cap.read()
        if ret:
            if self.is_detecting:
                frame = self.detect_colors(frame)

            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, c = rgb_frame.shape
            q_img = QImage(rgb_frame.data, w, h, c * w, QImage.Format.Format_RGB888)
            self.main_cam.setPixmap(QPixmap.fromImage(q_img))

    def detect_colors(self, frame):
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        for color, (lower, upper) in self.color_ranges.items():
            mask = cv2.inRange(hsv_frame, np.array(lower), np.array(upper))
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                if cv2.contourArea(contour) > 500:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, color, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        return frame

    def toggle_detection(self):
        self.is_detecting = not self.is_detecting
        self.detect_button.setText("Stop Detection" if self.is_detecting else "Color Detect")

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ColorDetectionApp()
    window.show()
    sys.exit(app.exec())