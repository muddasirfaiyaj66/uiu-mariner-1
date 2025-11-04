"""
Camera Worker Module with OpenCV Object Detection
Handles dual camera feeds from Raspberry Pi with GStreamer and real-time object detection
"""

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap


class CameraWorker(QThread):
    """
    Worker thread for camera streaming with object detection.
    Receives H.264 video stream via GStreamer UDP and applies OpenCV detection.
    """

    frame_ready = pyqtSignal(QPixmap)  # Emits processed frame as QPixmap
    fps_update = pyqtSignal(float)  # Emits current FPS
    error_occurred = pyqtSignal(str)  # Emits error messages

    def __init__(self, pipeline, detection_enabled=True, camera_id=0, parent=None):
        super().__init__(parent)
        self.pipeline = pipeline
        self.running = False
        self.detection_enabled = detection_enabled
        self.camera_id = camera_id
        self.cap = None

        # Object detection setup
        self.detector = None
        self.detection_type = "none"  # "haar", "yolo", "none"

        # FPS calculation
        self.fps_counter = 0
        self.fps_start_time = 0

        # Initialize detector if enabled
        if detection_enabled:
            self._init_detector()

    def _init_detector(self):
        """Initialize object detection model."""
        try:
            # Try Haar Cascade first (lightweight, good for underwater)
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self.detector = cv2.CascadeClassifier(cascade_path)

            if self.detector.empty():
                print(
                    f"[CAM{self.camera_id}] Haar Cascade not loaded, detection disabled"
                )
                self.detection_enabled = False
            else:
                self.detection_type = "haar"
                print(f"[CAM{self.camera_id}] Haar Cascade detector initialized")
        except Exception as e:
            print(f"[CAM{self.camera_id}] Detection init error: {e}")
            self.detection_enabled = False

    def run(self):
        """Main camera capture loop."""
        import time

        self.running = True
        self.fps_start_time = time.time()
        retry_count = 0
        max_retries = 2  # Quick failure for faster startup

        try:
            while self.running and retry_count < max_retries:
                # Open camera with GStreamer pipeline
                print(
                    f"[CAM{self.camera_id}] Attempting to open stream (attempt {retry_count + 1}/{max_retries})..."
                )
                self.cap = cv2.VideoCapture(self.pipeline, cv2.CAP_GSTREAMER)

                if not self.cap.isOpened():
                    retry_count += 1
                    error_msg = f"Camera {self.camera_id}: Failed to open stream"
                    self.error_occurred.emit(error_msg)
                    print(f"[CAM{self.camera_id}] ❌ Failed to open: {self.pipeline}")

                    if retry_count < max_retries:
                        print(f"[CAM{self.camera_id}] Retrying in 1 second...")
                        time.sleep(1)
                    else:
                        print(
                            f"[CAM{self.camera_id}] Max retries reached, showing placeholder"
                        )
                        self._show_placeholder()
                        return
                    continue

                # Successfully opened
                print(f"[CAM{self.camera_id}] ✅ Stream opened successfully")
                break

            # Main capture loop
            frame_timeout_count = 0
            max_frame_timeout = 30  # Allow 30 consecutive failures before giving up

            while self.running:
                ret, frame = self.cap.read()

                if not ret:
                    frame_timeout_count += 1
                    if frame_timeout_count >= max_frame_timeout:
                        print(
                            f"[CAM{self.camera_id}] ⚠️ Too many frame read failures, stopping"
                        )
                        self._show_placeholder()
                        break
                    time.sleep(0.1)
                    continue

                # Reset timeout counter on successful read
                frame_timeout_count = 0

                # Apply object detection if enabled
                if self.detection_enabled and self.detector is not None:
                    frame = self._apply_detection(frame)

                # Add camera info overlay
                frame = self._add_overlay(frame)

                # Convert to QPixmap for Qt display
                pixmap = self._frame_to_pixmap(frame)
                self.frame_ready.emit(pixmap)

                # Calculate FPS
                self.fps_counter += 1
                if time.time() - self.fps_start_time >= 1.0:
                    fps = self.fps_counter / (time.time() - self.fps_start_time)
                    self.fps_update.emit(fps)
                    self.fps_counter = 0
                    self.fps_start_time = time.time()

                # Small delay to prevent CPU overload
                time.sleep(0.01)

        except Exception as e:
            error_msg = f"Camera {self.camera_id} error: {str(e)}"
            self.error_occurred.emit(error_msg)
            print(f"[CAM{self.camera_id}] ❌ {error_msg}")
            self._show_placeholder()

        finally:
            if self.cap:
                self.cap.release()
            print(f"[CAM{self.camera_id}] Stream closed")

    def _show_placeholder(self):
        """Show placeholder image when camera is unavailable."""
        # Create a placeholder frame
        placeholder = np.zeros((480, 640, 3), dtype=np.uint8)

        # Add text
        text = f"Camera {self.camera_id + 1} Unavailable"
        cv2.putText(
            placeholder,
            text,
            (100, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (100, 100, 100),
            2,
        )

        cv2.putText(
            placeholder,
            "Check network connection",
            (140, 280),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (80, 80, 80),
            1,
        )

        # Emit placeholder
        pixmap = self._frame_to_pixmap(placeholder)
        self.frame_ready.emit(pixmap)

    def _apply_detection(self, frame):
        """Apply object detection to frame."""
        if self.detection_type == "haar":
            return self._detect_haar(frame)
        return frame

    def _detect_haar(self, frame):
        """Haar Cascade detection (faces, or can be adapted for fish/objects)."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect objects
        detections = self.detector.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        # Draw bounding boxes
        for x, y, w, h in detections:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                "Object",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        # Add detection count
        if len(detections) > 0:
            cv2.putText(
                frame,
                f"Detected: {len(detections)}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        return frame

    def _add_overlay(self, frame):
        """Add camera information overlay."""
        # Camera ID badge
        cv2.rectangle(frame, (5, 5), (120, 35), (0, 0, 0), -1)
        cv2.rectangle(frame, (5, 5), (120, 35), (255, 136, 0), 2)
        cv2.putText(
            frame,
            f"CAM {self.camera_id + 1}",
            (15, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 136, 0),
            2,
        )

        # Detection status
        if self.detection_enabled:
            status_text = "DETECT: ON"
            status_color = (0, 255, 0)
        else:
            status_text = "DETECT: OFF"
            status_color = (128, 128, 128)

        cv2.putText(
            frame,
            status_text,
            (10, frame.shape[0] - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            status_color,
            1,
        )

        return frame

    def _frame_to_pixmap(self, frame):
        """Convert OpenCV frame to QPixmap."""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w

        # Create QImage
        q_image = QImage(
            rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
        )

        # Convert to QPixmap
        return QPixmap.fromImage(q_image)

    def toggle_detection(self, enabled):
        """Enable or disable object detection."""
        self.detection_enabled = enabled

    def stop(self):
        """Stop the camera thread."""
        self.running = False
        self.wait()


class DualCameraManager:
    """
    Manages two camera workers for dual camera setup.
    """

    def __init__(self, pipeline0, pipeline1):
        self.camera0 = CameraWorker(pipeline0, detection_enabled=True, camera_id=0)
        self.camera1 = CameraWorker(pipeline1, detection_enabled=True, camera_id=1)

        self.cameras = [self.camera0, self.camera1]

    def start_all(self):
        """Start both camera streams."""
        for cam in self.cameras:
            cam.start()

    def stop_all(self):
        """Stop both camera streams."""
        for cam in self.cameras:
            cam.stop()

    def toggle_detection(self, camera_id, enabled):
        """Toggle detection for specific camera."""
        if 0 <= camera_id < len(self.cameras):
            self.cameras[camera_id].toggle_detection(enabled)

    def toggle_all_detection(self, enabled):
        """Toggle detection for all cameras."""
        for cam in self.cameras:
            cam.toggle_detection(enabled)
