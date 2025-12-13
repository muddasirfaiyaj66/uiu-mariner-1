"""
Simple Camera Integration with Object Detection
Draws rectangle boxes around detected objects
"""

import cv2
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal


class CameraDetector(QObject):
    """
    Simple detector that processes camera frames
    Detects objects and draws rectangle boxes
    """

    detection_stats = pyqtSignal(dict)

    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id
        self.enabled = False
        self.mode = "contour"  # contour, color, motion, edge

        # Color detection settings (default: blue)
        self.color_lower = np.array([100, 150, 0])
        self.color_upper = np.array([140, 255, 255])

        # Motion detection
        self.prev_frame = None
        self.motion_threshold = 25  # Lower threshold for better motion sensitivity

        # Contour detection settings - adjusted for better detection
        self.min_area = 300  # Lowered from 500 to detect smaller objects
        self.blur_size = 5
        self.threshold_value = 50  # Lowered from 60 for better edge detection

        print(f"[CV] Camera {camera_id} detector initialized")

    def process_frame(self, frame):
        """Process frame and return annotated frame with rectangles"""
        if frame is None:
            return frame
        
        if not self.enabled:
            # Still draw status to show detection is disabled
            output = frame.copy()
            cv2.putText(output, "DETECTION: OFF", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
            return output

        try:
            if self.mode == "contour":
                return self._detect_contours(frame)
            elif self.mode == "color":
                return self._detect_color(frame)
            elif self.mode == "motion":
                return self._detect_motion(frame)
            elif self.mode == "edge":
                return self._detect_edges(frame)
            else:
                return frame
        except Exception as e:
            print(f"[CV] Error: {e}")
            return frame

    def _detect_contours(self, frame):
        """Detect objects by contour and draw rectangle boxes"""
        output = frame.copy()
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (self.blur_size, self.blur_size), 0)
        
        # Apply threshold
        _, thresh = cv2.threshold(blurred, self.threshold_value, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_area:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Draw rectangle box (green)
                cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Draw center point
                cx, cy = x + w // 2, y + h // 2
                cv2.circle(output, (cx, cy), 4, (0, 0, 255), -1)
                
                # Label
                label = f"Obj {count + 1}"
                cv2.putText(output, label, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                count += 1

        # Status overlay
        cv2.putText(output, f"OBJECT DETECTION: {count} objects", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        self.detection_stats.emit({"mode": "contour", "count": count})
        return output

    def _detect_color(self, frame):
        """Detect colored objects and draw rectangle boxes"""
        output = frame.copy()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.color_lower, self.color_upper)

        # Clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Draw rectangle box (cyan for color mode)
                cv2.rectangle(output, (x, y), (x + w, y + h), (255, 255, 0), 2)
                
                # Center point
                cx, cy = x + w // 2, y + h // 2
                cv2.circle(output, (cx, cy), 4, (0, 0, 255), -1)
                
                label = f"Color {count + 1}"
                cv2.putText(output, label, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                count += 1

        cv2.putText(output, f"COLOR DETECTION: {count} objects", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        self.detection_stats.emit({"mode": "color", "count": count})
        return output

    def _detect_motion(self, frame):
        """Detect motion and draw rectangle boxes"""
        output = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.prev_frame is None:
            self.prev_frame = gray
            return output

        frame_diff = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_diff, self.motion_threshold, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        count = 0
        for contour in contours:
            if cv2.contourArea(contour) > 1000:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Draw rectangle box (yellow for motion)
                cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 255), 2)
                
                label = f"Motion {count + 1}"
                cv2.putText(output, label, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                count += 1

        self.prev_frame = gray

        cv2.putText(output, f"MOTION DETECTION: {count} areas", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        self.detection_stats.emit({"mode": "motion", "count": count})
        return output

    def _detect_edges(self, frame):
        """Edge detection with contour rectangles"""
        output = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours from edges
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        count = 0
        for contour in contours:
            if cv2.contourArea(contour) > self.min_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Draw rectangle box (magenta for edges)
                cv2.rectangle(output, (x, y), (x + w, y + h), (255, 0, 255), 2)
                count += 1

        cv2.putText(output, f"EDGE DETECTION: {count} shapes", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

        self.detection_stats.emit({"mode": "edge", "count": count})
        return output

    def set_mode(self, mode):
        """Set detection mode: contour, color, motion, edge"""
        if mode in ["contour", "color", "motion", "edge"]:
            self.mode = mode
            self.prev_frame = None
            print(f"[CV] Mode: {mode}")

    def set_color_target(self, color_name):
        """Set target color: red, green, blue, yellow, orange"""
        colors = {
            "red": ([0, 120, 70], [10, 255, 255]),
            "green": ([40, 40, 40], [80, 255, 255]),
            "blue": ([100, 150, 0], [140, 255, 255]),
            "yellow": ([20, 100, 100], [30, 255, 255]),
            "orange": ([10, 100, 100], [20, 255, 255]),
        }
        if color_name in colors:
            self.color_lower = np.array(colors[color_name][0])
            self.color_upper = np.array(colors[color_name][1])
            print(f"[CV] Target color: {color_name}")

    def set_min_area(self, area):
        """Set minimum detection area (default 500)"""
        self.min_area = max(100, area)
        print(f"[CV] Min area: {self.min_area}")

    def set_threshold(self, value):
        """Set threshold value for contour detection (0-255)"""
        self.threshold_value = max(0, min(255, value))
        print(f"[CV] Threshold: {self.threshold_value}")

    def enable(self):
        """Enable detection"""
        self.enabled = True
        print("[CV] Detection enabled")

    def disable(self):
        """Disable detection"""
        self.enabled = False
        print("[CV] Detection disabled")
