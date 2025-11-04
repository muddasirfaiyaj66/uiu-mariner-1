from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
import sys

from control import ControlPage
# from control import ArmThread
from sensor import SensorPage
from configuration import ConfigPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HYD.R.A")

        self.light_mode="""QWidget{background-color:#ffffff; color:black; font-family: Montserrat}"""
        self.dark_mode="""QWidget{background-color:#181e1c; color:white; font-family: Montserrat}"""

        self.current_mode = "dark"
        self.setStyleSheet(self.dark_mode)




        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)


        self.navbar = self.create_navbar()
        self.main_layout.addWidget(self.navbar)


        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)


        self.control_page = ControlPage(self)
        self.control_page.start_video_threads()
        self.sensor_page = SensorPage(self)
        self.config_page = ConfigPage(self)

        # # Threded        
        # self.control_page.arm_thread = ArmThread()
        # self.control_page.arm_thread.start()

        self.stacked_widget.addWidget(self.control_page)
        self.stacked_widget.addWidget(self.sensor_page)
        self.stacked_widget.addWidget(self.config_page)


        self.stacked_widget.setCurrentWidget(self.control_page)

    def create_navbar(self):
        navbar = QWidget()
        layout = QHBoxLayout(navbar)

        adminbtn = QPushButton('Admin')
        adminbtn.setStyleSheet("""
        background-color: #F95A00;
        width: 40px;
        padding: 5px;
        border-radius:5px;
        color:white;
        font-size:10px;                 
        """)
        layout.addWidget(adminbtn)
        layout.addStretch()
        

        control_button = QPushButton("Control")
        control_button.setStyleSheet("background-color: transparent; padding: 10px; font-size: 10px;")
        control_button.clicked.connect(self.show_control_page)

        sensor_button = QPushButton("Sensor")
        sensor_button.setStyleSheet("background-color: transparent; padding: 10px; font-size: 10px;")
        sensor_button.clicked.connect(self.show_sensor_page)

        config_button = QPushButton("Config")
        config_button.setStyleSheet("background-color: transparent; padding: 10px; font-size: 10px;")
        config_button.clicked.connect(self.show_config_page)


        layout.addWidget(control_button)
        layout.addWidget(sensor_button)
        layout.addWidget(config_button)
        layout.addStretch()

        self.toggleModebtn = QPushButton()

        self.toggleModebtn.setStyleSheet("""
        
        padding: 4px; 
        border-radius: 12px; 
        background: #F95A00;
""")
        btnicon = QIcon("Autonomous-Underwater-Vehicle---Team-UIU-H.Y.D.RA/assets/sun.png")
        self.toggleModebtn.setIcon(btnicon)
        self.toggleModebtn.clicked.connect(self.toggle_mode)
        layout.addWidget(self.toggleModebtn)

        return navbar
    
    def toggle_mode(self):
        if self.current_mode == "dark":
            self.setStyleSheet(self.light_mode)
            self.toggleModebtn.setIcon(QIcon("Autonomous-Underwater-Vehicle---Team-UIU-H.Y.D.RA/assets/moon.png"))
            self.toggleModebtn.setStyleSheet("""padding: 4px; border-radius: 12px; background: transparent; border: 1px solid #F95A00;""")
            self.current_mode = "light"
        else:
            self.setStyleSheet(self.dark_mode)
            self.toggleModebtn.setIcon(QIcon("Autonomous-Underwater-Vehicle---Team-UIU-H.Y.D.RA/assets/sun.png"))
            self.toggleModebtn.setStyleSheet("""
        
            padding: 4px; 
            border-radius: 12px; 
            background: #F95A00;
            """)
            self.current_mode = "dark"


    def show_control_page(self):
        self.stacked_widget.setCurrentWidget(self.control_page)

    def show_sensor_page(self):
        self.stacked_widget.setCurrentWidget(self.sensor_page)

    def show_config_page(self):
        self.stacked_widget.setCurrentWidget(self.config_page)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1920, 1080)
    window.setStyleSheet("""
    QWidget {
        background-color: #181e1c;
        margin: 0;
        padding: 0;
        font-family: Equinox ;
        color: white;
    }
    QVBoxLayout, QHBoxLayout {
        margin: 0;
        spacing: 0;
    }
""")
    window.show()
    sys.exit(app.exec())
