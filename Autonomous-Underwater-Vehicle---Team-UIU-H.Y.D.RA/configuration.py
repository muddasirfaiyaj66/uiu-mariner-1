import sys
import time
import psutil
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
    QTextEdit,
    QComboBox
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush
from PyQt6.QtCore import Qt, QRectF, QTimer
from PyQt6.QtCharts import QChart, QChartView, QLineSeries
import serial.tools.list_ports

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ConfigPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()





    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        self.setLayout(main_layout)
