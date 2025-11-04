import sys
import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QLineEdit

import matplotlib.pyplot as plt

class LengthMeasurementApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Length Measurement Tool")
        self.setGeometry(100, 100, 800, 600)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image_label)

        # UI Elements for file upload and input
        self.upload_button = QPushButton("Upload Image", self)
        self.upload_button.clicked.connect(self.upload_image)
        
        self.width_input_label = QLineEdit(self)
        self.width_input_label.setPlaceholderText("Enter known width (in cm, e.g. 3.5)")

        self.measure_button = QPushButton("Measure Object", self)
        self.measure_button.clicked.connect(self.measure_object)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.upload_button)
        layout.addWidget(self.width_input_label)
        layout.addWidget(self.measure_button)

        container = QWidget()
        container.setLayout(layout)
        self.setMenuWidget(container)

        self.image_path = None
        self.known_width_cm = None

    def upload_image(self):

        file, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp)")


        if file:
            self.image_path = file
            self.display_image(file)

    def display_image(self, file_path):
        image = cv2.imread(file_path)
        height, width, channels = image.shape
        bytes_per_line = channels * width
        q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        pixmap = QPixmap(q_img)
        self.image_label.setPixmap(pixmap)

    def measure_object(self):
        if not self.image_path:
            return
        
        # Get the known width from input field
        try:
            self.known_width_cm = float(self.width_input_label.text())
        except ValueError:
            self.known_width_cm = None

        # Perform the measurement
        output = self.measure_single_object_cm(self.image_path, known_width_cm=self.known_width_cm)

    def measure_single_object_cm(self, image_path, known_width_cm=None):
        image = cv2.imread(image_path)
        output = image.copy()

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            print("No objects detected!")
            return output

        largest_contour = max(contours, key=cv2.contourArea)

        cv2.drawContours(output, [largest_contour], -1, (0, 255, 0), 2)

        rect = cv2.minAreaRect(largest_contour)
        box = cv2.boxPoints(rect)
        box = np.array(box, dtype=np.int32)

        cv2.drawContours(output, [box], 0, (0, 0, 255), 2)

        (center_x, center_y), (width_px, height_px), angle = rect

        length_px = max(width_px, height_px)
        width_px = min(width_px, height_px)

        if known_width_cm:
            pixels_per_cm = width_px / known_width_cm
            length_cm = length_px / pixels_per_cm

            unit = "cm"
            print(f"Object width: {known_width_cm} cm")
            print(f"Object length: {length_cm:.2f} cm")
            print(f"Pixels per cm: {pixels_per_cm:.2f}")
        else:
            length_cm = length_px
            unit = "pixels"
            print(f"Object length: {length_px:.2f} pixels")
            print(f"Object width: {width_px:.2f} pixels")

        text_x = int(center_x) - 50
        text_y = int(center_y) + 50

        cv2.putText(output, f"Length: {length_cm:.2f} {unit}", (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        angle_rad = angle * np.pi / 180

        if width_px > height_px:
            half_length = width_px / 2
            dx = half_length * np.cos(angle_rad)
            dy = half_length * np.sin(angle_rad)
        else:
            half_length = height_px / 2
            dx = half_length * np.sin(angle_rad)
            dy = half_length * np.cos(angle_rad)

        pt1 = (int(center_x - dx), int(center_y - dy))
        pt2 = (int(center_x + dx), int(center_y + dy))

        cv2.line(output, pt1, pt2, (255, 0, 0), 2)

        # Show the result in Matplotlib
        plt.figure(figsize=(15, 5))

        plt.subplot(1, 3, 1)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.title('Original Image')
        plt.axis('off')

        plt.subplot(1, 3, 2)
        plt.imshow(thresh, cmap='gray')
        plt.title('Thresholded Image')
        plt.axis('off')

        plt.subplot(1, 3, 3)
        plt.imshow(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))
        plt.title('Object Measurement')
        plt.axis('off')

        plt.tight_layout()
        plt.show()

        return output

def main():
    app = QApplication(sys.argv)
    window = LengthMeasurementApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
