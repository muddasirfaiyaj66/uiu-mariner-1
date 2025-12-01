# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QStackedWidget, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1600, 1000)
        MainWindow.setStyleSheet(u"QMainWindow {\n"
"    background-color: #10121D;\n"
"}\n"
"QPushButton {\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 8px 16px;\n"
"    font-size: 14px;\n"
"    background-color: transparent;\n"
"    color: #ffffff;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #1a1d2e;\n"
"}\n"
"QPushButton:checked {\n"
"    background-color: #1e3a5f;\n"
"    color: #00d4ff;\n"
"}\n"
"QLineEdit, QComboBox {\n"
"    background-color: #1a1d2e;\n"
"    border: 1px solid #2a2d3e;\n"
"    border-radius: 6px;\n"
"    padding: 8px 12px;\n"
"    color: #ffffff;\n"
"    font-size: 14px;\n"
"}\n"
"QLineEdit:focus, QComboBox:focus {\n"
"    border: 1px solid #00d4ff;\n"
"}\n"
"QScrollArea {\n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"QScrollBar:vertical {\n"
"    background-color: #1a1d2e;\n"
"    width: 8px;\n"
"    border-radius: 4px;\n"
"}\n"
"QScrollBar::handle:vertical {\n"
"    background-color: #2a2d3e;\n"
"    border-radius: 4px;\n"
"    min-height: 20px;\n"
"}\n"
"QScro"
                        "llBar::handle:vertical:hover {\n"
"    background-color: #3a3d4e;\n"
"}\n"
"QTabWidget::pane {\n"
"    border: none;\n"
"    background-color: #10121D;\n"
"}\n"
"QTabBar::tab {\n"
"    background-color: transparent;\n"
"    color: #8B949E;\n"
"    padding: 12px 24px;\n"
"    border: none;\n"
"    font-size: 14px;\n"
"}\n"
"QTabBar::tab:selected {\n"
"    color: #ffffff;\n"
"    border-bottom: 2px solid #00d4ff;\n"
"}\n"
"QTabBar::tab:hover {\n"
"    color: #ffffff;\n"
"}\n"
"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_main = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_main.setSpacing(0)
        self.horizontalLayout_main.setObjectName(u"horizontalLayout_main")
        self.horizontalLayout_main.setContentsMargins(0, 0, 0, 0)
        self.sideBar = QFrame(self.centralwidget)
        self.sideBar.setObjectName(u"sideBar")
        self.sideBar.setMinimumSize(QSize(260, 0))
        self.sideBar.setMaximumSize(QSize(260, 16777215))
        self.sideBar.setStyleSheet(u"QFrame#sideBar {\n"
"    background-color: #10121D;\n"
"    border-right: 1px solid #1a1d2e;\n"
"}\n"
"")
        self.verticalLayout_sidebar = QVBoxLayout(self.sideBar)
        self.verticalLayout_sidebar.setSpacing(0)
        self.verticalLayout_sidebar.setObjectName(u"verticalLayout_sidebar")
        self.verticalLayout_sidebar.setContentsMargins(0, 0, 0, 0)
        self.logoSection = QFrame(self.sideBar)
        self.logoSection.setObjectName(u"logoSection")
        self.logoSection.setMinimumSize(QSize(0, 80))
        self.logoSection.setMaximumSize(QSize(16777215, 80))
        self.horizontalLayout_logo = QHBoxLayout(self.logoSection)
        self.horizontalLayout_logo.setSpacing(12)
        self.horizontalLayout_logo.setObjectName(u"horizontalLayout_logo")
        self.horizontalLayout_logo.setContentsMargins(20, 12, 20, 12)
        self.lblLogoIcon = QLabel(self.logoSection)
        self.lblLogoIcon.setObjectName(u"lblLogoIcon")
        self.lblLogoIcon.setStyleSheet(u"QLabel {\n"
"    background-color: #1a1d2e;\n"
"    border-radius: 20px;\n"
"    padding: 4px;\n"
"    min-width: 48px;\n"
"    max-width: 48px;\n"
"    min-height: 48px;\n"
"    max-height: 48px;\n"
"}\n"
"")
        self.lblLogoIcon.setScaledContents(True)
        self.lblLogoIcon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_logo.addWidget(self.lblLogoIcon)

        self.logoTextWidget = QWidget(self.logoSection)
        self.logoTextWidget.setObjectName(u"logoTextWidget")
        self.verticalLayout_logoText = QVBoxLayout(self.logoTextWidget)
        self.verticalLayout_logoText.setSpacing(2)
        self.verticalLayout_logoText.setObjectName(u"verticalLayout_logoText")
        self.verticalLayout_logoText.setContentsMargins(0, 0, 0, 0)
        self.lblLogoText = QLabel(self.logoTextWidget)
        self.lblLogoText.setObjectName(u"lblLogoText")
        self.lblLogoText.setStyleSheet(u"QLabel {\n"
"    color: #ffffff;\n"
"    font-size: 18px;\n"
"    font-weight: bold;\n"
"}\n"
"")

        self.verticalLayout_logoText.addWidget(self.lblLogoText)

        self.lblLogoSubtext = QLabel(self.logoTextWidget)
        self.lblLogoSubtext.setObjectName(u"lblLogoSubtext")
        self.lblLogoSubtext.setStyleSheet(u"QLabel {\n"
"    color: #8B949E;\n"
"    font-size: 12px;\n"
"}\n"
"")

        self.verticalLayout_logoText.addWidget(self.lblLogoSubtext)


        self.horizontalLayout_logo.addWidget(self.logoTextWidget)

        self.horizontalSpacer_logo = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_logo.addItem(self.horizontalSpacer_logo)

        self.btnMenuToggle = QPushButton(self.logoSection)
        self.btnMenuToggle.setObjectName(u"btnMenuToggle")
        self.btnMenuToggle.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    color: #ffffff;\n"
"    font-size: 20px;\n"
"    border: none;\n"
"    padding: 4px;\n"
"    min-width: 32px;\n"
"    max-width: 32px;\n"
"    min-height: 32px;\n"
"    max-height: 32px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #1a1d2e;\n"
"    border-radius: 4px;\n"
"}\n"
"")

        self.horizontalLayout_logo.addWidget(self.btnMenuToggle)


        self.verticalLayout_sidebar.addWidget(self.logoSection)

        self.navButtonsWidget = QWidget(self.sideBar)
        self.navButtonsWidget.setObjectName(u"navButtonsWidget")
        self.verticalLayout_nav = QVBoxLayout(self.navButtonsWidget)
        self.verticalLayout_nav.setSpacing(4)
        self.verticalLayout_nav.setObjectName(u"verticalLayout_nav")
        self.verticalLayout_nav.setContentsMargins(12, 12, 12, 12)
        self.btnMainControl = QPushButton(self.navButtonsWidget)
        self.btnMainControl.setObjectName(u"btnMainControl")
        self.btnMainControl.setCheckable(True)
        self.btnMainControl.setChecked(True)
        self.btnMainControl.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    color: #8B949E;\n"
"    text-align: left;\n"
"    padding: 12px 16px;\n"
"    font-size: 14px;\n"
"    border-radius: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #1a1d2e;\n"
"    color: #ffffff;\n"
"}\n"
"QPushButton:checked {\n"
"    background-color: #1e3a5f;\n"
"    color: #00d4ff;\n"
"    border-left: 3px solid #00d4ff;\n"
"}\n"
"")

        self.verticalLayout_nav.addWidget(self.btnMainControl)

        self.btnGallery = QPushButton(self.navButtonsWidget)
        self.btnGallery.setObjectName(u"btnGallery")
        self.btnGallery.setCheckable(True)
        self.btnGallery.setChecked(False)
        self.btnGallery.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    color: #8B949E;\n"
"    text-align: left;\n"
"    padding: 12px 16px;\n"
"    font-size: 14px;\n"
"    border-radius: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #1a1d2e;\n"
"    color: #ffffff;\n"
"}\n"
"QPushButton:checked {\n"
"    background-color: #1e3a5f;\n"
"    color: #00d4ff;\n"
"    border-left: 3px solid #00d4ff;\n"
"}\n"
"")

        self.verticalLayout_nav.addWidget(self.btnGallery)

        self.btnMissionLogs = QPushButton(self.navButtonsWidget)
        self.btnMissionLogs.setObjectName(u"btnMissionLogs")
        self.btnMissionLogs.setCheckable(True)
        self.btnMissionLogs.setChecked(False)
        self.btnMissionLogs.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    color: #8B949E;\n"
"    text-align: left;\n"
"    padding: 12px 16px;\n"
"    font-size: 14px;\n"
"    border-radius: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #1a1d2e;\n"
"    color: #ffffff;\n"
"}\n"
"QPushButton:checked {\n"
"    background-color: #1e3a5f;\n"
"    color: #00d4ff;\n"
"    border-left: 3px solid #00d4ff;\n"
"}\n"
"")

        self.verticalLayout_nav.addWidget(self.btnMissionLogs)

        self.btnSystemStatus = QPushButton(self.navButtonsWidget)
        self.btnSystemStatus.setObjectName(u"btnSystemStatus")
        self.btnSystemStatus.setCheckable(True)
        self.btnSystemStatus.setChecked(False)
        self.btnSystemStatus.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    color: #8B949E;\n"
"    text-align: left;\n"
"    padding: 12px 16px;\n"
"    font-size: 14px;\n"
"    border-radius: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #1a1d2e;\n"
"    color: #ffffff;\n"
"}\n"
"QPushButton:checked {\n"
"    background-color: #1e3a5f;\n"
"    color: #00d4ff;\n"
"    border-left: 3px solid #00d4ff;\n"
"}\n"
"")

        self.verticalLayout_nav.addWidget(self.btnSystemStatus)

        self.btnSettings = QPushButton(self.navButtonsWidget)
        self.btnSettings.setObjectName(u"btnSettings")
        self.btnSettings.setCheckable(True)
        self.btnSettings.setChecked(False)
        self.btnSettings.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    color: #8B949E;\n"
"    text-align: left;\n"
"    padding: 12px 16px;\n"
"    font-size: 14px;\n"
"    border-radius: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #1a1d2e;\n"
"    color: #ffffff;\n"
"}\n"
"QPushButton:checked {\n"
"    background-color: #1e3a5f;\n"
"    color: #00d4ff;\n"
"    border-left: 3px solid #00d4ff;\n"
"}\n"
"")

        self.verticalLayout_nav.addWidget(self.btnSettings)


        self.verticalLayout_sidebar.addWidget(self.navButtonsWidget)

        self.verticalSpacer_sidebar = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_sidebar.addItem(self.verticalSpacer_sidebar)

        self.lblSidebarFooter = QLabel(self.sideBar)
        self.lblSidebarFooter.setObjectName(u"lblSidebarFooter")
        self.lblSidebarFooter.setStyleSheet(u"QLabel {\n"
"    color: #8B949E;\n"
"    font-size: 11px;\n"
"    padding: 12px 20px;\n"
"}\n"
"")
        self.lblSidebarFooter.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_sidebar.addWidget(self.lblSidebarFooter)


        self.horizontalLayout_main.addWidget(self.sideBar)

        self.mainContent = QWidget(self.centralwidget)
        self.mainContent.setObjectName(u"mainContent")
        self.mainContent.setStyleSheet(u"QWidget#mainContent {\n"
"    background-color: #10121D;\n"
"}\n"
"")
        self.verticalLayout_mainContent = QVBoxLayout(self.mainContent)
        self.verticalLayout_mainContent.setSpacing(0)
        self.verticalLayout_mainContent.setObjectName(u"verticalLayout_mainContent")
        self.verticalLayout_mainContent.setContentsMargins(0, 0, 0, 0)
        self.topBar = QFrame(self.mainContent)
        self.topBar.setObjectName(u"topBar")
        self.topBar.setMinimumSize(QSize(0, 100))
        self.topBar.setMaximumSize(QSize(16777215, 100))
        self.topBar.setStyleSheet(u"QFrame#topBar {\n"
"    background-color: #1a1d2e;\n"
"    border-bottom: 1px solid #2a2d3e;\n"
"}\n"
"")
        self.horizontalLayout_topBar = QHBoxLayout(self.topBar)
        self.horizontalLayout_topBar.setSpacing(16)
        self.horizontalLayout_topBar.setObjectName(u"horizontalLayout_topBar")
        self.horizontalLayout_topBar.setContentsMargins(24, 12, 24, 12)
        self.titleSection = QWidget(self.topBar)
        self.titleSection.setObjectName(u"titleSection")
        self.verticalLayout_title = QVBoxLayout(self.titleSection)
        self.verticalLayout_title.setSpacing(4)
        self.verticalLayout_title.setObjectName(u"verticalLayout_title")
        self.verticalLayout_title.setContentsMargins(0, 0, 0, 0)
        self.lblMainTitle = QLabel(self.titleSection)
        self.lblMainTitle.setObjectName(u"lblMainTitle")
        self.lblMainTitle.setStyleSheet(u"QLabel {\n"
"    color: #ffffff;\n"
"    font-size: 28px;\n"
"    font-weight: bold;\n"
"}\n"
"")

        self.verticalLayout_title.addWidget(self.lblMainTitle)

        self.lblSubtitle = QLabel(self.titleSection)
        self.lblSubtitle.setObjectName(u"lblSubtitle")
        self.lblSubtitle.setStyleSheet(u"QLabel {\n"
"    color: #8B949E;\n"
"    font-size: 14px;\n"
"}\n"
"")

        self.verticalLayout_title.addWidget(self.lblSubtitle)


        self.horizontalLayout_topBar.addWidget(self.titleSection)

        self.horizontalSpacer_topBar = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_topBar.addItem(self.horizontalSpacer_topBar)

        self.statusSection = QWidget(self.topBar)
        self.statusSection.setObjectName(u"statusSection")
        self.horizontalLayout_status = QHBoxLayout(self.statusSection)
        self.horizontalLayout_status.setSpacing(12)
        self.horizontalLayout_status.setObjectName(u"horizontalLayout_status")
        self.horizontalLayout_status.setContentsMargins(0, 0, 0, 0)
        self.lblConnectionStatus = QLabel(self.statusSection)
        self.lblConnectionStatus.setObjectName(u"lblConnectionStatus")
        self.lblConnectionStatus.setStyleSheet(u"QLabel {\n"
"    color: #00ff00;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"}\n"
"")

        self.horizontalLayout_status.addWidget(self.lblConnectionStatus)

        self.lblTime = QLabel(self.statusSection)
        self.lblTime.setObjectName(u"lblTime")
        self.lblTime.setStyleSheet(u"QLabel {\n"
"    color: #ffffff;\n"
"    font-size: 14px;\n"
"}\n"
"")

        self.horizontalLayout_status.addWidget(self.lblTime)


        self.horizontalLayout_topBar.addWidget(self.statusSection)


        self.verticalLayout_mainContent.addWidget(self.topBar)

        self.contentStack = QStackedWidget(self.mainContent)
        self.contentStack.setObjectName(u"contentStack")
        self.contentStack.setStyleSheet(u"QStackedWidget {\n"
"    background-color: #10121D;\n"
"}\n"
"")
        self.mainControlPage = QWidget()
        self.mainControlPage.setObjectName(u"mainControlPage")
        self.mainControlPage.setStyleSheet(u"QWidget {\n"
"    background-color: #10121D;\n"
"}\n"
"")
        self.verticalLayout_mainControl = QVBoxLayout(self.mainControlPage)
        self.verticalLayout_mainControl.setSpacing(0)
        self.verticalLayout_mainControl.setObjectName(u"verticalLayout_mainControl")
        self.verticalLayout_mainControl.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.mainControlPage)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setStyleSheet(u"QTabWidget::pane {\n"
"    border: none;\n"
"    background-color: #10121D;\n"
"}\n"
"QTabBar::tab {\n"
"    background-color: transparent;\n"
"    color: #8B949E;\n"
"    padding: 12px 24px;\n"
"    border: none;\n"
"    font-size: 14px;\n"
"    min-width: 120px;\n"
"}\n"
"QTabBar::tab:selected {\n"
"    color: #ffffff;\n"
"    border-bottom: 2px solid #00d4ff;\n"
"}\n"
"QTabBar::tab:hover {\n"
"    color: #ffffff;\n"
"}\n"
"")
        self.overviewTab = QWidget()
        self.overviewTab.setObjectName(u"overviewTab")
        self.horizontalLayout_overview = QHBoxLayout(self.overviewTab)
        self.horizontalLayout_overview.setSpacing(24)
        self.horizontalLayout_overview.setObjectName(u"horizontalLayout_overview")
        self.horizontalLayout_overview.setContentsMargins(24, 24, 24, 24)
        self.cameraSection = QWidget(self.overviewTab)
        self.cameraSection.setObjectName(u"cameraSection")
        self.verticalLayout_cameras = QVBoxLayout(self.cameraSection)
        self.verticalLayout_cameras.setSpacing(16)
        self.verticalLayout_cameras.setObjectName(u"verticalLayout_cameras")
        self.verticalLayout_cameras.setContentsMargins(0, 0, 0, 0)
        self.mainCameraFrame = QFrame(self.cameraSection)
        self.mainCameraFrame.setObjectName(u"mainCameraFrame")
        self.verticalLayout_mainCamera = QVBoxLayout(self.mainCameraFrame)
        self.verticalLayout_mainCamera.setSpacing(8)
        self.verticalLayout_mainCamera.setObjectName(u"verticalLayout_mainCamera")
        self.lblMainCameraTitle = QLabel(self.mainCameraFrame)
        self.lblMainCameraTitle.setObjectName(u"lblMainCameraTitle")
        self.lblMainCameraTitle.setStyleSheet(u"QLabel { color: #00d4ff; font-size: 16px; font-weight: bold; }")

        self.verticalLayout_mainCamera.addWidget(self.lblMainCameraTitle)

        self.lblMainCameraFeed = QLabel(self.mainCameraFrame)
        self.lblMainCameraFeed.setObjectName(u"lblMainCameraFeed")
        self.lblMainCameraFeed.setMinimumSize(QSize(640, 320))
        self.lblMainCameraFeed.setStyleSheet(u"QLabel { background-color: #181b2a; border: 1px solid #23263a; border-radius: 8px; color: #8B949E; }")
        self.lblMainCameraFeed.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_mainCamera.addWidget(self.lblMainCameraFeed)


        self.verticalLayout_cameras.addWidget(self.mainCameraFrame)

        self.secondaryCamerasContainer = QWidget(self.cameraSection)
        self.secondaryCamerasContainer.setObjectName(u"secondaryCamerasContainer")
        self.horizontalLayout_secondaryCameras = QHBoxLayout(self.secondaryCamerasContainer)
        self.horizontalLayout_secondaryCameras.setSpacing(12)
        self.horizontalLayout_secondaryCameras.setObjectName(u"horizontalLayout_secondaryCameras")
        self.horizontalLayout_secondaryCameras.setContentsMargins(0, 0, 0, 0)
        self.bottomCameraFrame = QFrame(self.secondaryCamerasContainer)
        self.bottomCameraFrame.setObjectName(u"bottomCameraFrame")
        self.verticalLayout_bottomCamera = QVBoxLayout(self.bottomCameraFrame)
        self.verticalLayout_bottomCamera.setObjectName(u"verticalLayout_bottomCamera")
        self.lblBottomCameraTitle = QLabel(self.bottomCameraFrame)
        self.lblBottomCameraTitle.setObjectName(u"lblBottomCameraTitle")
        self.lblBottomCameraTitle.setStyleSheet(u"QLabel { color: #00d4ff; font-size: 14px; font-weight: bold; }")

        self.verticalLayout_bottomCamera.addWidget(self.lblBottomCameraTitle)

        self.lblBottomCameraFeed = QLabel(self.bottomCameraFrame)
        self.lblBottomCameraFeed.setObjectName(u"lblBottomCameraFeed")
        self.lblBottomCameraFeed.setMinimumSize(QSize(300, 160))
        self.lblBottomCameraFeed.setStyleSheet(u"QLabel { background-color: #181b2a; border: 1px solid #23263a; border-radius: 8px; color: #8B949E; }")
        self.lblBottomCameraFeed.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_bottomCamera.addWidget(self.lblBottomCameraFeed)


        self.horizontalLayout_secondaryCameras.addWidget(self.bottomCameraFrame)

        self.gripperCameraFrame = QFrame(self.secondaryCamerasContainer)
        self.gripperCameraFrame.setObjectName(u"gripperCameraFrame")
        self.verticalLayout_gripperCamera = QVBoxLayout(self.gripperCameraFrame)
        self.verticalLayout_gripperCamera.setObjectName(u"verticalLayout_gripperCamera")
        self.lblGripperCameraTitle = QLabel(self.gripperCameraFrame)
        self.lblGripperCameraTitle.setObjectName(u"lblGripperCameraTitle")
        self.lblGripperCameraTitle.setStyleSheet(u"QLabel { color: #00d4ff; font-size: 14px; font-weight: bold; }")

        self.verticalLayout_gripperCamera.addWidget(self.lblGripperCameraTitle)

        self.lblGripperCameraFeed = QLabel(self.gripperCameraFrame)
        self.lblGripperCameraFeed.setObjectName(u"lblGripperCameraFeed")
        self.lblGripperCameraFeed.setMinimumSize(QSize(300, 160))
        self.lblGripperCameraFeed.setStyleSheet(u"QLabel { background-color: #181b2a; border: 1px solid #23263a; border-radius: 8px; color: #8B949E; }")
        self.lblGripperCameraFeed.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_gripperCamera.addWidget(self.lblGripperCameraFeed)


        self.horizontalLayout_secondaryCameras.addWidget(self.gripperCameraFrame)


        self.verticalLayout_cameras.addWidget(self.secondaryCamerasContainer)


        self.horizontalLayout_overview.addWidget(self.cameraSection)

        self.rightPanelFrame = QFrame(self.overviewTab)
        self.rightPanelFrame.setObjectName(u"rightPanelFrame")
        self.rightPanelFrame.setStyleSheet(u"QFrame#rightPanelFrame {\n"
"    background-color: #181b2a;\n"
"    border: 1px solid #23263a;\n"
"    border-radius: 12px;\n"
"    padding: 18px 16px 18px 16px;\n"
"}")
        self.verticalLayout_rightPanel = QVBoxLayout(self.rightPanelFrame)
        self.verticalLayout_rightPanel.setSpacing(18)
        self.verticalLayout_rightPanel.setObjectName(u"verticalLayout_rightPanel")
        self.verticalLayout_rightPanel.setContentsMargins(12, 12, 12, 12)
        self.orientationHeadingCard = QFrame(self.rightPanelFrame)
        self.orientationHeadingCard.setObjectName(u"orientationHeadingCard")
        self.verticalLayout_orientation = QVBoxLayout(self.orientationHeadingCard)
        self.verticalLayout_orientation.setObjectName(u"verticalLayout_orientation")
        self.lblOrientationTitle = QLabel(self.orientationHeadingCard)
        self.lblOrientationTitle.setObjectName(u"lblOrientationTitle")
        self.lblOrientationTitle.setStyleSheet(u"QLabel { color: #00d4ff; font-size: 15px; font-weight: bold; }")

        self.verticalLayout_orientation.addWidget(self.lblOrientationTitle)

        self.lblCompass = QLabel(self.orientationHeadingCard)
        self.lblCompass.setObjectName(u"lblCompass")
        self.lblCompass.setMinimumSize(QSize(180, 120))
        self.lblCompass.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblCompass.setStyleSheet(u"QLabel { background: #10121D; border-radius: 90px; color: #8B949E; }")

        self.verticalLayout_orientation.addWidget(self.lblCompass)

        self.lblPitchRollYaw = QLabel(self.orientationHeadingCard)
        self.lblPitchRollYaw.setObjectName(u"lblPitchRollYaw")
        self.lblPitchRollYaw.setStyleSheet(u"QLabel { color: #8B949E; font-size: 13px; }")

        self.verticalLayout_orientation.addWidget(self.lblPitchRollYaw)


        self.verticalLayout_rightPanel.addWidget(self.orientationHeadingCard)

        self.sensorDataCard = QFrame(self.rightPanelFrame)
        self.sensorDataCard.setObjectName(u"sensorDataCard")
        self.verticalLayout_sensorData = QVBoxLayout(self.sensorDataCard)
        self.verticalLayout_sensorData.setObjectName(u"verticalLayout_sensorData")
        self.lblSensorDataTitle = QLabel(self.sensorDataCard)
        self.lblSensorDataTitle.setObjectName(u"lblSensorDataTitle")
        self.lblSensorDataTitle.setStyleSheet(u"QLabel { color: #00d4ff; font-size: 15px; font-weight: bold; }")

        self.verticalLayout_sensorData.addWidget(self.lblSensorDataTitle)

        self.lblDepth = QLabel(self.sensorDataCard)
        self.lblDepth.setObjectName(u"lblDepth")
        self.lblDepth.setStyleSheet(u"QLabel { color: #8B949E; font-size: 13px; }")

        self.verticalLayout_sensorData.addWidget(self.lblDepth)

        self.lblTemperature = QLabel(self.sensorDataCard)
        self.lblTemperature.setObjectName(u"lblTemperature")
        self.lblTemperature.setStyleSheet(u"QLabel { color: #8B949E; font-size: 13px; }")

        self.verticalLayout_sensorData.addWidget(self.lblTemperature)

        self.lblPressure = QLabel(self.sensorDataCard)
        self.lblPressure.setObjectName(u"lblPressure")
        self.lblPressure.setStyleSheet(u"QLabel { color: #8B949E; font-size: 13px; }")

        self.verticalLayout_sensorData.addWidget(self.lblPressure)

        self.lblBattery = QLabel(self.sensorDataCard)
        self.lblBattery.setObjectName(u"lblBattery")
        self.lblBattery.setStyleSheet(u"QLabel { color: #8B949E; font-size: 13px; }")

        self.verticalLayout_sensorData.addWidget(self.lblBattery)


        self.verticalLayout_rightPanel.addWidget(self.sensorDataCard)

        self.quickActionsCard = QFrame(self.rightPanelFrame)
        self.quickActionsCard.setObjectName(u"quickActionsCard")
        self.gridLayout_quickActions = QGridLayout(self.quickActionsCard)
        self.gridLayout_quickActions.setObjectName(u"gridLayout_quickActions")
        self.btnCapture = QPushButton(self.quickActionsCard)
        self.btnCapture.setObjectName(u"btnCapture")

        self.gridLayout_quickActions.addWidget(self.btnCapture, 0, 0, 1, 1)

        self.btnRecord = QPushButton(self.quickActionsCard)
        self.btnRecord.setObjectName(u"btnRecord")

        self.gridLayout_quickActions.addWidget(self.btnRecord, 0, 1, 1, 1)

        self.btnLights = QPushButton(self.quickActionsCard)
        self.btnLights.setObjectName(u"btnLights")

        self.gridLayout_quickActions.addWidget(self.btnLights, 1, 0, 1, 1)

        self.btnAutoHold = QPushButton(self.quickActionsCard)
        self.btnAutoHold.setObjectName(u"btnAutoHold")

        self.gridLayout_quickActions.addWidget(self.btnAutoHold, 1, 1, 1, 1)

        self.btnWaypoint = QPushButton(self.quickActionsCard)
        self.btnWaypoint.setObjectName(u"btnWaypoint")

        self.gridLayout_quickActions.addWidget(self.btnWaypoint, 2, 0, 1, 1)

        self.btnSurface = QPushButton(self.quickActionsCard)
        self.btnSurface.setObjectName(u"btnSurface")

        self.gridLayout_quickActions.addWidget(self.btnSurface, 2, 1, 1, 1)


        self.verticalLayout_rightPanel.addWidget(self.quickActionsCard)


        self.horizontalLayout_overview.addWidget(self.rightPanelFrame)

        self.tabWidget.addTab(self.overviewTab, "")
        self.thrusterControlTab = QWidget()
        self.thrusterControlTab.setObjectName(u"thrusterControlTab")
        self.verticalLayout_thrusterControl = QVBoxLayout(self.thrusterControlTab)
        self.verticalLayout_thrusterControl.setSpacing(20)
        self.verticalLayout_thrusterControl.setObjectName(u"verticalLayout_thrusterControl")
        self.verticalLayout_thrusterControl.setContentsMargins(24, 24, 24, 24)
        self.lblThrusterControlTitle = QLabel(self.thrusterControlTab)
        self.lblThrusterControlTitle.setObjectName(u"lblThrusterControlTitle")
        self.lblThrusterControlTitle.setStyleSheet(u"QLabel {\n"
"    color: #ffffff;\n"
"    font-size: 24px;\n"
"    font-weight: bold;\n"
"}\n"
"")

        self.verticalLayout_thrusterControl.addWidget(self.lblThrusterControlTitle)

        self.tabWidget.addTab(self.thrusterControlTab, "")
        self.sensorsTab = QWidget()
        self.sensorsTab.setObjectName(u"sensorsTab")
        self.verticalLayout_sensors = QVBoxLayout(self.sensorsTab)
        self.verticalLayout_sensors.setSpacing(20)
        self.verticalLayout_sensors.setObjectName(u"verticalLayout_sensors")
        self.verticalLayout_sensors.setContentsMargins(24, 24, 24, 24)
        self.lblSensorsTitle = QLabel(self.sensorsTab)
        self.lblSensorsTitle.setObjectName(u"lblSensorsTitle")
        self.lblSensorsTitle.setStyleSheet(u"QLabel {\n"
"    color: #ffffff;\n"
"    font-size: 24px;\n"
"    font-weight: bold;\n"
"}\n"
"")

        self.verticalLayout_sensors.addWidget(self.lblSensorsTitle)

        self.tabWidget.addTab(self.sensorsTab, "")
        self.toolsTab = QWidget()
        self.toolsTab.setObjectName(u"toolsTab")
        self.verticalLayout_tools = QVBoxLayout(self.toolsTab)
        self.verticalLayout_tools.setSpacing(20)
        self.verticalLayout_tools.setObjectName(u"verticalLayout_tools")
        self.verticalLayout_tools.setContentsMargins(24, 24, 24, 24)
        self.lblToolsTitle = QLabel(self.toolsTab)
        self.lblToolsTitle.setObjectName(u"lblToolsTitle")
        self.lblToolsTitle.setStyleSheet(u"QLabel {\n"
"    color: #ffffff;\n"
"    font-size: 24px;\n"
"    font-weight: bold;\n"
"}\n"
"")

        self.verticalLayout_tools.addWidget(self.lblToolsTitle)

        self.tabWidget.addTab(self.toolsTab, "")

        self.verticalLayout_mainControl.addWidget(self.tabWidget)

        self.contentStack.addWidget(self.mainControlPage)
        self.galleryPage = QWidget()
        self.galleryPage.setObjectName(u"galleryPage")
        self.galleryPage.setStyleSheet(u"QWidget {\n"
"    background-color: #10121D;\n"
"}\n"
"")
        self.verticalLayout_gallery = QVBoxLayout(self.galleryPage)
        self.verticalLayout_gallery.setSpacing(20)
        self.verticalLayout_gallery.setObjectName(u"verticalLayout_gallery")
        self.verticalLayout_gallery.setContentsMargins(24, 24, 24, 24)
        self.lblGalleryTitle = QLabel(self.galleryPage)
        self.lblGalleryTitle.setObjectName(u"lblGalleryTitle")
        self.lblGalleryTitle.setStyleSheet(u"QLabel {\n"
"    color: #ffffff;\n"
"    font-size: 28px;\n"
"    font-weight: bold;\n"
"}\n"
"")

        self.verticalLayout_gallery.addWidget(self.lblGalleryTitle)

        self.lblGallerySubtitle = QLabel(self.galleryPage)
        self.lblGallerySubtitle.setObjectName(u"lblGallerySubtitle")
        self.lblGallerySubtitle.setStyleSheet(u"QLabel {\n"
"    color: #8B949E;\n"
"    font-size: 14px;\n"
"}\n"
"")

        self.verticalLayout_gallery.addWidget(self.lblGallerySubtitle)

        self.galleryFilters = QWidget(self.galleryPage)
        self.galleryFilters.setObjectName(u"galleryFilters")
        self.horizontalLayout_galleryFilters = QHBoxLayout(self.galleryFilters)
        self.horizontalLayout_galleryFilters.setSpacing(12)
        self.horizontalLayout_galleryFilters.setObjectName(u"horizontalLayout_galleryFilters")
        self.horizontalLayout_galleryFilters.setContentsMargins(0, 0, 0, 0)
        self.btnFilterAllMedia = QPushButton(self.galleryFilters)
        self.btnFilterAllMedia.setObjectName(u"btnFilterAllMedia")
        self.btnFilterAllMedia.setCheckable(True)
        self.btnFilterAllMedia.setChecked(True)
        self.btnFilterAllMedia.setStyleSheet(u"QPushButton {\n"
"    background-color: #00d4ff;\n"
"    color: #ffffff;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 10px 20px;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #00b8e6;\n"
"}\n"
"QPushButton:checked {\n"
"    background-color: #00d4ff;\n"
"}\n"
"")

        self.horizontalLayout_galleryFilters.addWidget(self.btnFilterAllMedia)

        self.btnFilterImages = QPushButton(self.galleryFilters)
        self.btnFilterImages.setObjectName(u"btnFilterImages")
        self.btnFilterImages.setCheckable(True)
        self.btnFilterImages.setChecked(False)
        self.btnFilterImages.setStyleSheet(u"QPushButton {\n"
"    background-color: #1a1d2e;\n"
"    color: #8B949E;\n"
"    border: 1px solid #2a2d3e;\n"
"    border-radius: 6px;\n"
"    padding: 10px 20px;\n"
"    font-size: 14px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #2a2d3e;\n"
"    color: #ffffff;\n"
"}\n"
"QPushButton:checked {\n"
"    background-color: #1e3a5f;\n"
"    color: #00d4ff;\n"
"    border: 1px solid #00d4ff;\n"
"}\n"
"")

        self.horizontalLayout_galleryFilters.addWidget(self.btnFilterImages)

        self.btnFilterVideos = QPushButton(self.galleryFilters)
        self.btnFilterVideos.setObjectName(u"btnFilterVideos")
        self.btnFilterVideos.setCheckable(True)
        self.btnFilterVideos.setChecked(False)
        self.btnFilterVideos.setStyleSheet(u"QPushButton {\n"
"    background-color: #1a1d2e;\n"
"    color: #8B949E;\n"
"    border: 1px solid #2a2d3e;\n"
"    border-radius: 6px;\n"
"    padding: 10px 20px;\n"
"    font-size: 14px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #2a2d3e;\n"
"    color: #ffffff;\n"
"}\n"
"QPushButton:checked {\n"
"    background-color: #1e3a5f;\n"
"    color: #00d4ff;\n"
"    border: 1px solid #00d4ff;\n"
"}\n"
"")

        self.horizontalLayout_galleryFilters.addWidget(self.btnFilterVideos)


        self.verticalLayout_gallery.addWidget(self.galleryFilters)

        self.scrollAreaGallery = QScrollArea(self.galleryPage)
        self.scrollAreaGallery.setObjectName(u"scrollAreaGallery")
        self.scrollAreaGallery.setWidgetResizable(True)
        self.scrollAreaGallery.setStyleSheet(u"QScrollArea {\n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"")
        self.galleryContent = QWidget()
        self.galleryContent.setObjectName(u"galleryContent")
        self.galleryContent.setGeometry(QRect(0, 0, 1200, 600))
        self.gridLayout_gallery = QGridLayout(self.galleryContent)
        self.gridLayout_gallery.setSpacing(16)
        self.gridLayout_gallery.setObjectName(u"gridLayout_gallery")
        self.gridLayout_gallery.setContentsMargins(0, 0, 0, 0)
        self.scrollAreaGallery.setWidget(self.galleryContent)

        self.verticalLayout_gallery.addWidget(self.scrollAreaGallery)

        self.contentStack.addWidget(self.galleryPage)
        self.missionLogsPage = QWidget()
        self.missionLogsPage.setObjectName(u"missionLogsPage")
        self.missionLogsPage.setStyleSheet(u"QWidget {\n"
"    background-color: #10121D;\n"
"}\n"
"")
        self.verticalLayout_missionLogs = QVBoxLayout(self.missionLogsPage)
        self.verticalLayout_missionLogs.setSpacing(20)
        self.verticalLayout_missionLogs.setObjectName(u"verticalLayout_missionLogs")
        self.verticalLayout_missionLogs.setContentsMargins(24, 24, 24, 24)
        self.lblMissionLogsTitle = QLabel(self.missionLogsPage)
        self.lblMissionLogsTitle.setObjectName(u"lblMissionLogsTitle")
        self.lblMissionLogsTitle.setStyleSheet(u"QLabel {\n"
"    color: #ffffff;\n"
"    font-size: 28px;\n"
"    font-weight: bold;\n"
"}\n"
"")

        self.verticalLayout_missionLogs.addWidget(self.lblMissionLogsTitle)

        self.contentStack.addWidget(self.missionLogsPage)
        self.systemStatusPage = QWidget()
        self.systemStatusPage.setObjectName(u"systemStatusPage")
        self.systemStatusPage.setStyleSheet(u"QWidget {\n"
"    background-color: #10121D;\n"
"}\n"
"")
        self.verticalLayout_systemStatus = QVBoxLayout(self.systemStatusPage)
        self.verticalLayout_systemStatus.setSpacing(20)
        self.verticalLayout_systemStatus.setObjectName(u"verticalLayout_systemStatus")
        self.verticalLayout_systemStatus.setContentsMargins(24, 24, 24, 24)
        self.lblSystemStatusTitle = QLabel(self.systemStatusPage)
        self.lblSystemStatusTitle.setObjectName(u"lblSystemStatusTitle")
        self.lblSystemStatusTitle.setStyleSheet(u"QLabel {\n"
"    color: #ffffff;\n"
"    font-size: 28px;\n"
"    font-weight: bold;\n"
"}\n"
"")

        self.verticalLayout_systemStatus.addWidget(self.lblSystemStatusTitle)

        self.lblSystemStatusSubtitle = QLabel(self.systemStatusPage)
        self.lblSystemStatusSubtitle.setObjectName(u"lblSystemStatusSubtitle")
        self.lblSystemStatusSubtitle.setStyleSheet(u"QLabel {\n"
"    color: #8B949E;\n"
"    font-size: 14px;\n"
"}\n"
"")

        self.verticalLayout_systemStatus.addWidget(self.lblSystemStatusSubtitle)

        self.contentStack.addWidget(self.systemStatusPage)
        self.settingsPage = QWidget()
        self.settingsPage.setObjectName(u"settingsPage")
        self.settingsPage.setStyleSheet(u"QWidget {\n"
"    background-color: #10121D;\n"
"}\n"
"")
        self.verticalLayout_settings = QVBoxLayout(self.settingsPage)
        self.verticalLayout_settings.setSpacing(20)
        self.verticalLayout_settings.setObjectName(u"verticalLayout_settings")
        self.verticalLayout_settings.setContentsMargins(24, 24, 24, 24)
        self.lblSettingsTitle = QLabel(self.settingsPage)
        self.lblSettingsTitle.setObjectName(u"lblSettingsTitle")
        self.lblSettingsTitle.setStyleSheet(u"QLabel {\n"
"    color: #ffffff;\n"
"    font-size: 28px;\n"
"    font-weight: bold;\n"
"}\n"
"")

        self.verticalLayout_settings.addWidget(self.lblSettingsTitle)

        self.lblSettingsSubtitle = QLabel(self.settingsPage)
        self.lblSettingsSubtitle.setObjectName(u"lblSettingsSubtitle")
        self.lblSettingsSubtitle.setStyleSheet(u"QLabel {\n"
"    color: #8B949E;\n"
"    font-size: 14px;\n"
"}\n"
"")

        self.verticalLayout_settings.addWidget(self.lblSettingsSubtitle)

        self.contentStack.addWidget(self.settingsPage)

        self.verticalLayout_mainContent.addWidget(self.contentStack)


        self.horizontalLayout_main.addWidget(self.mainContent)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"ROV Control Station", None))
        self.lblLogoIcon.setText("")
        self.lblLogoText.setText(QCoreApplication.translate("MainWindow", u"UIU AURA", None))
        self.lblLogoSubtext.setText(QCoreApplication.translate("MainWindow", u"Underwater Robotics", None))
        self.btnMenuToggle.setText(QCoreApplication.translate("MainWindow", u"\u2630", None))
        self.btnMainControl.setText(QCoreApplication.translate("MainWindow", u"\U0001f3ae Main Control", None))
        self.btnGallery.setText(QCoreApplication.translate("MainWindow", u"\U0001f5bc\U0000fe0f Gallery", None))
        self.btnMissionLogs.setText(QCoreApplication.translate("MainWindow", u"\U0001f4cb Mission Logs", None))
        self.btnSystemStatus.setText(QCoreApplication.translate("MainWindow", u"\u26a1 System Status", None))
        self.btnSettings.setText(QCoreApplication.translate("MainWindow", u"\u2699\ufe0f Settings", None))
        self.lblSidebarFooter.setText(QCoreApplication.translate("MainWindow", u"UIU Underwater Robotics and Automation Crew", None))
        self.lblMainTitle.setText(QCoreApplication.translate("MainWindow", u"ROV Control Station", None))
        self.lblSubtitle.setText(QCoreApplication.translate("MainWindow", u"UIU AURA - Underwater Robotics Control", None))
        self.lblConnectionStatus.setText(QCoreApplication.translate("MainWindow", u"\U0001f7e2 Connected", None))
        self.lblTime.setText(QCoreApplication.translate("MainWindow", u"23:51:16", None))
        self.lblMainCameraTitle.setText(QCoreApplication.translate("MainWindow", u"Main Camera", None))
        self.lblMainCameraFeed.setText(QCoreApplication.translate("MainWindow", u"Camera Feed", None))
        self.lblBottomCameraTitle.setText(QCoreApplication.translate("MainWindow", u"Bottom Camera", None))
        self.lblBottomCameraFeed.setText(QCoreApplication.translate("MainWindow", u"Camera Feed", None))
        self.lblGripperCameraTitle.setText(QCoreApplication.translate("MainWindow", u"Gripper Camera", None))
        self.lblGripperCameraFeed.setText(QCoreApplication.translate("MainWindow", u"Camera Feed", None))
        self.lblOrientationTitle.setText(QCoreApplication.translate("MainWindow", u"Orientation & Heading", None))
        self.lblCompass.setText(QCoreApplication.translate("MainWindow", u"Compass Widget", None))
        self.lblPitchRollYaw.setText(QCoreApplication.translate("MainWindow", u"Pitch: 0\u00b0  Roll: 0\u00b0  Yaw: 0\u00b0", None))
        self.lblSensorDataTitle.setText(QCoreApplication.translate("MainWindow", u"Sensor Data", None))
        self.lblDepth.setText(QCoreApplication.translate("MainWindow", u"Depth: 0.00 m", None))
        self.lblTemperature.setText(QCoreApplication.translate("MainWindow", u"Temperature: 0.0 \u00b0C", None))
        self.lblPressure.setText(QCoreApplication.translate("MainWindow", u"Pressure: 0.00 bar", None))
        self.lblBattery.setText(QCoreApplication.translate("MainWindow", u"Battery: 100%", None))
        self.btnCapture.setText(QCoreApplication.translate("MainWindow", u"Capture", None))
        self.btnRecord.setText(QCoreApplication.translate("MainWindow", u"Record", None))
        self.btnLights.setText(QCoreApplication.translate("MainWindow", u"Lights", None))
        self.btnAutoHold.setText(QCoreApplication.translate("MainWindow", u"Auto-Hold", None))
        self.btnWaypoint.setText(QCoreApplication.translate("MainWindow", u"Waypoint", None))
        self.btnSurface.setText(QCoreApplication.translate("MainWindow", u"Surface", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.overviewTab), QCoreApplication.translate("MainWindow", u"Overview", None))
        self.lblThrusterControlTitle.setText(QCoreApplication.translate("MainWindow", u"Thruster Control", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.thrusterControlTab), QCoreApplication.translate("MainWindow", u"Thruster Control", None))
        self.lblSensorsTitle.setText(QCoreApplication.translate("MainWindow", u"Sensors", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sensorsTab), QCoreApplication.translate("MainWindow", u"Sensors", None))
        self.lblToolsTitle.setText(QCoreApplication.translate("MainWindow", u"Tools", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.toolsTab), QCoreApplication.translate("MainWindow", u"Tools", None))
        self.lblGalleryTitle.setText(QCoreApplication.translate("MainWindow", u"Media Gallery", None))
        self.lblGallerySubtitle.setText(QCoreApplication.translate("MainWindow", u"Captured images and recorded videos", None))
        self.btnFilterAllMedia.setText(QCoreApplication.translate("MainWindow", u"\U0001f5bc\U0000fe0f All Media", None))
        self.btnFilterImages.setText(QCoreApplication.translate("MainWindow", u"\U0001f4f7 Images", None))
        self.btnFilterVideos.setText(QCoreApplication.translate("MainWindow", u"\U0001f3a5 Videos", None))
        self.lblMissionLogsTitle.setText(QCoreApplication.translate("MainWindow", u"Mission Logs", None))
        self.lblSystemStatusTitle.setText(QCoreApplication.translate("MainWindow", u"System Status", None))
        self.lblSystemStatusSubtitle.setText(QCoreApplication.translate("MainWindow", u"Hardware and software diagnostics", None))
        self.lblSettingsTitle.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.lblSettingsSubtitle.setText(QCoreApplication.translate("MainWindow", u"Configure ROV system parameters", None))
    # retranslateUi

