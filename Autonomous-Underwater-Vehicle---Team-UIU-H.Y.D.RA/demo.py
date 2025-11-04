from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer
import cv2


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Live Bottle Detection")
        self.setGeometry(100, 100, 800, 600)
        
        # YOLO Model
        self.model = YOLO("AUV/best.pt")  # Path to your trained YOLO model
        
        # Camera Feed Label
        self.camera_label = QLabel(self)
        self.camera_label.setFixedSize(640, 480)
        
        # Button to Start Detection
        self.run_button = QPushButton("Run Detection")
        self.run_button.clicked.connect(self.start_detection)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.camera_label)
        layout.addWidget(self.run_button)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # OpenCV Camera
        self.capture = cv2.VideoCapture(0)  # 0 for default webcam
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.detection_active = False

    def start_detection(self):
        """Start or stop live detection."""
        if not self.detection_active:
            self.detection_active = True
            self.run_button.setText("Stop Detection")
            self.timer.start(30)  # Update every 30ms
        else:
            self.detection_active = False
            self.run_button.setText("Run Detection")
            self.timer.stop()

    def update_frame(self):
        """Capture frame, run detection, and update the camera label."""
        ret, frame = self.capture.read()
        if not ret:
            return
        
        if self.detection_active:
            # Run YOLO detection on the frame
            results = self.model.predict(source=frame, show=False, stream=False)
            
            # Get the first result and filter predictions by confidence > 60%
            detections = results[0].boxes  # Boxes object with detections
            filtered_boxes = []
            for box in detections:
                confidence = box.conf[0]  # Get the confidence score
                if confidence > 0.5:  # Filter out detections below 60%
                    filtered_boxes.append(box)
            
            # Draw the filtered predictions on the frame
            annotated_frame = frame.copy()
            for box in filtered_boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
                label = f"{self.model.names[int(box.cls[0])]}: {box.conf[0]:.2f}"
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rectangle
                cv2.putText(annotated_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        else:
            annotated_frame = frame  # Original frame without detection

        # Convert the frame to Qt format
        rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_frame.shape
        q_image = QImage(rgb_frame.data, width, height, channel * width, QImage.Format.Format_RGB888)
        
        # Display the frame in the label
        self.camera_label.setPixmap(QPixmap.fromImage(q_image))

    def closeEvent(self, event):
        """Release the camera when closing the application."""
        self.capture.release()
        cv2.destroyAllWindows()
        event.accept()

# Run the Application
app = QApplication([])
window = MainWindow()
window.show()
app.exec()
