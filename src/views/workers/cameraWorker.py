"""
Camera Worker Module with OpenCV Object Detection
Handles dual camera feeds from Raspberry Pi via MJPEG HTTP streams with real-time object detection
"""

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap


class CameraWorker(QThread):
    """
    Worker thread for camera streaming with object detection.
    Receives MJPEG video stream via HTTP and applies OpenCV detection.
    """

    frame_ready = pyqtSignal(QPixmap)
    fps_update = pyqtSignal(float)
    error_occurred = pyqtSignal(str)

    def __init__(self, stream_url, detection_enabled=True, camera_id=0, parent=None):
        super().__init__(parent)
        self.stream_url = stream_url
        self.running = False
        self.detection_enabled = detection_enabled
        self.camera_id = camera_id
        self.cap = None
        self.current_frame = None

        self.detector = None
        self.detection_type = "none"

        self.fps_counter = 0
        self.fps_start_time = 0

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
        """Main camera capture loop with MJPEG stream."""
        import time

        self.running = True
        self.fps_start_time = time.time()
        retry_count = 0
        max_retries = 3

        try:
            while self.running and retry_count < max_retries:
                print(
                    f"[CAM{self.camera_id}] Attempting to open MJPEG stream (attempt {retry_count + 1}/{max_retries})..."
                )
                print(f"[CAM{self.camera_id}] URL: {self.stream_url}")

                # Open MJPEG stream via HTTP
                self.cap = cv2.VideoCapture(self.stream_url)

                if not self.cap.isOpened():
                    retry_count += 1
                    error_msg = f"Camera {self.camera_id}: Failed to open MJPEG stream"
                    self.error_occurred.emit(error_msg)
                    print(f"[CAM{self.camera_id}] ❌ Failed to open: {self.stream_url}")

                    if retry_count < max_retries:
                        print(f"[CAM{self.camera_id}] Retrying in 2 seconds...")
                        time.sleep(2)
                    else:
                        print(
                            f"[CAM{self.camera_id}] Max retries reached, showing placeholder"
                        )
                        self._show_placeholder()
                        return
                    continue

                print(f"[CAM{self.camera_id}] ✅ MJPEG stream opened successfully")
                break

            frame_timeout_count = 0
            max_frame_timeout = 30
            frame_skip_counter = 0
            FRAME_SKIP = 1  # Less aggressive frame skipping for MJPEG

            while self.running:
                ret, frame = self.cap.read()

                if not ret:
                    frame_timeout_count += 1
                    if frame_timeout_count >= max_frame_timeout:
                        print(
                            f"[CAM{self.camera_id}] Too many frame read failures, reconnecting..."
                        )
                        # Try to reconnect
                        if self.cap:
                            self.cap.release()
                        time.sleep(1)
                        self.cap = cv2.VideoCapture(self.stream_url)
                        if not self.cap.isOpened():
                            self._show_placeholder()
                            break
                        frame_timeout_count = 0
                    time.sleep(0.1)
                    continue

                frame_timeout_count = 0

                # Optional frame skipping for performance
                frame_skip_counter += 1
                if frame_skip_counter <= FRAME_SKIP:
                    continue
                frame_skip_counter = 0

                # Ensure consistent resolution (1920x1080 for HD)
                if frame.shape[:2] != (1080, 1920):
                    frame = cv2.resize(
                        frame, (1920, 1080), interpolation=cv2.INTER_LINEAR
                    )

                # Apply object detection if enabled
                if self.detection_enabled and self.detector is not None:
                    frame = self._apply_detection(frame)

                # Add overlay information
                frame = self._add_overlay(frame)

                # Convert to QPixmap and emit
                pixmap = self._frame_to_pixmap(frame)
                self.frame_ready.emit(pixmap)

                # Store current frame for capture
                self.current_frame = frame.copy()

                # Update FPS
                self.fps_counter += 1
                if time.time() - self.fps_start_time >= 1.0:
                    fps = self.fps_counter / (time.time() - self.fps_start_time)
                    self.fps_update.emit(fps)
                    self.fps_counter = 0
                    self.fps_start_time = time.time()

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
        placeholder = np.zeros((1080, 1920, 3), dtype=np.uint8)

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

        pixmap = self._frame_to_pixmap(placeholder)
        self.frame_ready.emit(pixmap)

    def _apply_detection(self, frame):
        """Apply object detection to frame."""
        if self.detection_type == "haar":
            return self._detect_haar(frame)
        return frame

    def _detect_haar(self, frame):
        """Haar Cascade detection."""
        self.fps_counter += 1
        if self.fps_counter % 5 != 0:
            return frame

        small_frame = cv2.resize(frame, (320, 240))
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

        detections = self.detector.detectMultiScale(
            gray, scaleFactor=1.2, minNeighbors=6, minSize=(50, 50)
        )

        if len(detections) > 0:
            scale_x = frame.shape[1] / small_frame.shape[1]
            scale_y = frame.shape[0] / small_frame.shape[0]

            for i, (x, y, w, h) in enumerate(detections[:5]):
                x, y = int(x * scale_x), int(y * scale_y)
                w, h = int(w * scale_x), int(h * scale_y)
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
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w

        q_image = QImage(
            rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
        )

        return QPixmap.fromImage(q_image)

    def toggle_detection(self, enabled):
        """Enable or disable object detection."""
        self.detection_enabled = enabled

    def get_frame(self):
        """Get current frame for capture"""
        if self.current_frame is not None:
            return self.current_frame.copy()
        return None

    def stop(self):
        """Stop the camera thread."""
        self.running = False
        self.wait()


class DualCameraManager:
    """
    Manages two camera workers for dual camera setup with MJPEG streams.
    """

    def __init__(self, stream_url0, stream_url1):
        self.camera0 = CameraWorker(stream_url0, detection_enabled=True, camera_id=0)
        self.camera1 = CameraWorker(stream_url1, detection_enabled=True, camera_id=1)

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
