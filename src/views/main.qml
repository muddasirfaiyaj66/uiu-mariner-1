import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    visible: true
    width: 1920
    height: 1080
    title: "UIU AURA - Underwater ROV Control"
    color: "#000000"

    // Connect to Python backend
    Component.onCompleted: {
        console.log("QML Window loaded - visible:", visible, "width:", width, "height:", height)
        if (typeof backend !== 'undefined') {
            backend.initializeComponents()
            console.log("Backend initialized")
            console.log("Initial values - Depth:", backend.depth, "Temp:", backend.temperature, "Compass:", backend.compassHeading)
            
            // Connect media signals
            backend.imageCaptured.connect(function(filename) {
                showNotification("📸 Image Captured", filename)
            })
            backend.videoSaved.connect(function(filename) {
                showNotification("📹 Video Saved", filename)
            })
            
            // Test value updates
            backend.testUpdate()
        } else {
            console.error("Backend is undefined!")
        }
    }
    
    // Notification function
    function showNotification(title, message) {
        notificationText.text = title + "\n" + message
        notificationPopup.open()
        notificationTimer.restart()
    }

    QtObject {
        id: appTheme
        property color bg: "#000000"
        property color primary: "#00D4FF"
        property color primaryDark: "#0088AA"
        property color success: "#00FF88"
        property color error: "#FF3366"
        property color warning: "#FFB800"
        property color dark: "#0a0a0a"
        property color darker: "#050505"
        property color mid: "#1a1a1a"
        property color light: "#2a2a2a"
        property color text: "#FFFFFF"
        property color textDim: "#a0a0a0"
        property color border: "#333333"
        property color gradientStart: "#000000"
        property color gradientEnd: "#0a0a0a"
    }

    property bool sidebarOpen: true
    property int currentPage: 0
    property int missionTimerSeconds: 0
    property bool missionTimerRunning: false
    property int recordingTimerSeconds: 0
    property bool recordingTimerRunning: false
    
    // Direct backend property access - no intermediate properties needed
    property int activeCamera: backend.activeCamera
    property bool thrusterArmed: backend.thrusterArmed
    property bool isRecording: backend.isRecording
    
    // Watch for recording state changes to control recording timer only
    onIsRecordingChanged: {
        if (isRecording) {
            recordingTimerSeconds = 0
            recordingTimerRunning = true
        } else {
            recordingTimerRunning = false
        }
    }
    
    // Connect backend mission timer toggle signal
    Connections {
        target: backend
        function onToggleMissionTimer() {
            missionTimerRunning = !missionTimerRunning
            console.log("Mission timer:", missionTimerRunning ? "STARTED" : "STOPPED")
        }
    }
    property real compassHeading: backend.compassHeading
    property real depth: backend.depth
    property real temperature: backend.temperature
    property real salinity: backend.salinity
    property real phLevel: backend.phLevel
    property real oxygen: backend.oxygen
    property real turbidity: backend.turbidity
    property string connectionStatus: backend.connectionStatus

    Timer {
        id: missionTimer
        interval: 1000
        running: missionTimerRunning
        repeat: true
        onTriggered: missionTimerSeconds++
    }
    
    Timer {
        id: recordingTimer
        interval: 1000
        running: recordingTimerRunning
        repeat: true
        onTriggered: recordingTimerSeconds++
    }

    // Mock sensor timer disabled - using real backend data
    Timer {
        id: sensorUpdateTimer
        interval: 2000
        running: false  // Disabled - backend provides real data
        repeat: true
        onTriggered: {
            // Mock data disabled
        }
    }

    // Background gradient (simplified without LinearGradient)
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: appTheme.gradientStart }
            GradientStop { position: 1.0; color: appTheme.gradientEnd }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

        // TOP BAR - Modernized
        Rectangle {
            id: topBar
            Layout.fillWidth: true
            Layout.preferredHeight: 110
            color: "transparent"
            border.width: 1
            border.color: Qt.rgba(1,1,1,0.2)
            radius: 12
            z: 10

            // Qt6 compatible gradient using Rectangle
            Rectangle {
                anchors.fill: parent
                color: "transparent"
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0.0; color: Qt.rgba(0, 0.83, 1, 0.1) }
                    GradientStop { position: 1.0; color: "transparent" }
                }
            }

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                // Sidebar Toggle
                Rectangle {
                    Layout.preferredWidth: 56
                    Layout.fillHeight: true
                    radius: 8
                    color: Qt.rgba(1,1,1,0.1)
                    border.width: 1
                    border.color: Qt.rgba(1,1,1,0.2)

                    Text {
                        anchors.centerIn: parent
                        text: sidebarOpen ? "◀" : "▶"
                        color: appTheme.primary
                        font.pixelSize: 16
                        font.bold: true
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: sidebarOpen = !sidebarOpen
                    }
                }

                // Camera Selector with Live Previews
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    Repeater {
                        model: 4
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 100
                            radius: 8
                            color: activeCamera === index ? Qt.rgba(0, 0.83, 1, 0.2) : Qt.rgba(1,1,1,0.05)
                            border.width: activeCamera === index ? 2 : 1
                            border.color: activeCamera === index ? appTheme.primary : Qt.rgba(1,1,1,0.1)
                            clip: true

                            ColumnLayout {
                                anchors.fill: parent
                                spacing: 0

                                // Camera preview thumbnail
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    color: "#000000"
                                    
                                    Image {
                                        id: previewImage
                                        anchors.fill: parent
                                        fillMode: Image.PreserveAspectCrop
                                        source: "image://camera" + index + "/image"
                                        cache: false
                                        asynchronous: true
                                        
                                        // Refresh preview when frame updates
                                        Connections {
                                            target: backend
                                            function onCameraFrameUpdated(cameraId) {
                                                if (cameraId === index) {
                                                    var timestamp = Date.now()
                                                    previewImage.source = "image://camera" + index + "/image?t=" + timestamp
                                                }
                                            }
                                        }
                                        
                                        // Placeholder when no feed
                                        Text {
                                            anchors.centerIn: parent
                                            text: "CAM " + (index + 1)
                                            color: appTheme.textDim
                                            font.pixelSize: 12
                                            visible: previewImage.status !== Image.Ready
                                        }
                                    }
                                    
                                    // Dark overlay for inactive cameras
                                    Rectangle {
                                        anchors.fill: parent
                                        color: "#000000"
                                        opacity: activeCamera === index ? 0 : 0.4
                                    }
                                }
                                
                                // Camera label bar
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 28
                                    color: activeCamera === index ? appTheme.primary : Qt.rgba(0,0,0,0.6)
                                    
                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 8
                                        anchors.rightMargin: 8
                                        spacing: 6
                                        
                                        Rectangle {
                                            Layout.preferredWidth: 6
                                            Layout.preferredHeight: 6
                                            radius: 3
                                            color: activeCamera === index ? "#000000" : appTheme.textDim
                                        }
                                        
                                        Text {
                                            text: "CAM " + (index + 1)
                                            color: activeCamera === index ? "#000000" : appTheme.text
                                            font.pixelSize: 11
                                            font.bold: true
                                        }
                                        
                                        Item { Layout.fillWidth: true }
                                        
                                        Text {
                                            text: ["Front", "Bottom", "Port", "Starboard"][index]
                                            color: activeCamera === index ? "#000000" : appTheme.textDim
                                            font.pixelSize: 9
                                        }
                                    }
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    backend.setActiveCamera(index)
                                }
                            }
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                // Timer Section - Improved
                Rectangle {
                    Layout.preferredWidth: 220
                    Layout.fillHeight: true
                    radius: 8
                    color: "#0a0a0a"
                    border.width: 1
                    border.color: Qt.rgba(1,1,1,0.2)

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 12

                        ColumnLayout {
                            spacing: 4
                            Text {
                                text: "MISSION TIMER"
                                color: appTheme.primary
                                font.pixelSize: 10
                                font.letterSpacing: 2
                                font.bold: true
                            }
                            Text {
                                text: {
                                    var h = Math.floor(missionTimerSeconds / 3600)
                                    var m = Math.floor((missionTimerSeconds % 3600) / 60)
                                    var s = missionTimerSeconds % 60
                                    return (h < 10 ? "0" + h : h) + ":" + 
                                           (m < 10 ? "0" + m : m) + ":" + 
                                           (s < 10 ? "0" + s : s)
                                }
                                color: missionTimerRunning ? appTheme.success : appTheme.text
                                font.pixelSize: 22
                                font.family: "Monospace"
                                font.bold: true
                            }
                        }

                        Column {
                            spacing: 4
                            Rectangle {
                                width: 32
                                height: 32
                                radius: 8
                                color: missionTimerRunning ? appTheme.error : appTheme.success
                                border.width: 1
                                border.color: Qt.rgba(0,0,0,0.3)

                                Text {
                                    anchors.centerIn: parent
                                    text: missionTimerRunning ? "⏸" : "▶"
                                    color: "#000"
                                    font.pixelSize: 14
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: missionTimerRunning = !missionTimerRunning
                                }
                            }

                            Rectangle {
                                width: 32
                                height: 16
                                radius: 4
                                color: appTheme.warning
                                border.width: 1
                                border.color: Qt.rgba(0,0,0,0.3)

                                Text {
                                    anchors.centerIn: parent
                                    text: "↻"
                                    color: "#000"
                                    font.pixelSize: 10
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: { missionTimerSeconds = 0; missionTimerRunning = false }
                                }
                            }
                        }
                    }
                }

                // Media Controls
                RowLayout {
                    Layout.fillHeight: true
                    spacing: 8
                    MediaButton {
                        icon: "📸"
                        tooltip: "Capture Image"
                        onClicked: {
                            if (typeof backend !== 'undefined') {
                                backend.captureImage()
                            }
                        }
                    }
                    MediaButton {
                        icon: isRecording ? "⏹" : "🔴"
                        active: isRecording
                        tooltip: isRecording ? "Stop Recording" : "Start Recording"
                        onClicked: {
                            if (typeof backend !== 'undefined') {
                                backend.isRecording = !backend.isRecording
                            } else {
                                isRecording = !isRecording
                            }
                        }
                    }
                }
            }
        }

        // MAIN CONTENT
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 8

            // SIDEBAR - Modernized
            Rectangle {
                Layout.preferredWidth: sidebarOpen ? 240 : 0
                Layout.fillHeight: true
                color: "transparent"
                border.width: 1
                border.color: Qt.rgba(1,1,1,0.2)
                radius: 12
                clip: true
                z: 5

                Behavior on Layout.preferredWidth {
                    NumberAnimation { duration: 300; easing.type: Easing.InOutQuad }
                }

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    // UIU AURA CREW BRANDING SECTION
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 140
                        color: "#0a1929"
                        border.width: 2
                        border.color: appTheme.primary
                        radius: 12
                        
                        // Animated gradient background
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: Qt.rgba(0, 0.83, 1, 0.15) }
                            GradientStop { position: 0.5; color: Qt.rgba(0, 0.5, 0.8, 0.08) }
                            GradientStop { position: 1.0; color: "transparent" }
                        }

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 6

                            // Logo with glow background
                            Rectangle {
                                Layout.preferredWidth: 90
                                Layout.preferredHeight: 90
                                Layout.alignment: Qt.AlignHCenter
                                color: "transparent"
                                
                                // Outer glow
                                Rectangle {
                                    anchors.centerIn: parent
                                    width: parent.width + 10
                                    height: parent.height + 10
                                    color: "transparent"
                                    border.width: 2
                                    border.color: Qt.rgba(0, 0.83, 1, 0.3)
                                    radius: width / 2
                                }
                                
                                Image {
                                    anchors.fill: parent
                                    source: "file:///f:/UIU UNDERWATER ROBOTICS SOFTWARES/uiu-mariner-1/public/logo.png"
                                    fillMode: Image.PreserveAspectFit
                                }
                            }
                            
                            // Team Name
                            Text {
                                text: "UIU AURA CREW"
                                color: appTheme.primary
                                font.pixelSize: 18
                                font.bold: true
                                font.letterSpacing: 1.5
                                Layout.alignment: Qt.AlignHCenter
                                style: Text.Outline
                                styleColor: Qt.rgba(0, 0.83, 1, 0.3)
                            }
                            
                            // Full Name
                            Text {
                                text: ""
                                color: Qt.rgba(0, 212, 255, 0.9)
                                font.pixelSize: 7
                                font.letterSpacing: 1
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                                Layout.alignment: Qt.AlignHCenter
                                lineHeight: 1.2
                            }
                        }
                    }

                    // Navigation
                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 4
                        Layout.margins: 8

                        NavBtn { 
                            icon: "📊"; label: "Dashboard"; 
                            onClicked: currentPage = 0; active: currentPage === 0 
                        }
                        NavBtn { 
                            icon: "⚡"; label: "Thrusters"; 
                            onClicked: currentPage = 1; active: currentPage === 1 
                        }
                        NavBtn { 
                            icon: "📡"; label: "Sensors"; 
                            onClicked: currentPage = 2; active: currentPage === 2 
                        }
                        NavBtn { 
                            icon: "🧪"; label: "Water Analysis"; 
                            onClicked: currentPage = 3; active: currentPage === 3 
                        }
                        NavBtn { 
                            icon: "🖼️"; label: "Media Gallery"; 
                            onClicked: currentPage = 4; active: currentPage === 4 
                        }
                        NavBtn { 
                            icon: "⚙️"; label: "Settings"; 
                            onClicked: currentPage = 5; active: currentPage === 5 
                        }

                        Item { Layout.fillHeight: true }

                        // Status Panel
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 80
                            radius: 8
                            color: "#0a0a0a"
                            border.width: 1
                            border.color: Qt.rgba(1,1,1,0.2)

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 6

                                RowLayout {
                                    spacing: 8
                                    StatusDot { active: true; color: appTheme.success }
                                    Text {
                                        text: "System Status"
                                        color: appTheme.textDim
                                        font.pixelSize: 9
                                    }
                                    Item { Layout.fillWidth: true }
                                    Text {
                                        text: thrusterArmed ? "ARMED" : "SAFE"
                                        color: thrusterArmed ? appTheme.success : appTheme.textDim
                                        font.pixelSize: 9
                                        font.bold: true
                                    }
                                }

                                RowLayout {
                                    spacing: 8
                                    StatusDot { active: isRecording; color: appTheme.error }
                                    Text {
                                        text: "Recording"
                                        color: appTheme.textDim
                                        font.pixelSize: 9
                                    }
                                    Item { Layout.fillWidth: true }
                                    Text {
                                        text: isRecording ? "ACTIVE" : "INACTIVE"
                                        color: isRecording ? appTheme.error : appTheme.textDim
                                        font.pixelSize: 9
                                    }
                                }

                                ProgressBar {
                                    Layout.fillWidth: true
                                    value: 0.87
                                    background: Rectangle {
                                        implicitHeight: 4
                                        radius: 2
                                        color: Qt.rgba(1,1,1,0.1)
                                    }
                                    contentItem: Item {
                                        implicitHeight: 4
                                        Rectangle {
                                            width: parent.width * parent.parent.value
                                            height: parent.height
                                            radius: 2
                                            color: appTheme.success
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // MAIN CONTENT AREA
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "transparent"
                z: 1

                StackLayout {
                    anchors.fill: parent
                    currentIndex: currentPage

                    // PAGE 0: DASHBOARD
                    ColumnLayout {
                        spacing: 8

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            // Main Camera Feed
                            Rectangle {
                                Layout.preferredWidth: parent.width * 0.7
                                Layout.fillHeight: true
                                radius: 12
                                color: "#000"

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 1
                                    spacing: 0

                                    Rectangle {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 40
                                        color: Qt.rgba(0,0,0,0.8)
                                        radius: 12
                                        z: 2

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: 8
                                            spacing: 8

                                            Text {
                                                text: "ACTIVE CAMERA: " + ["FRONT", "BOTTOM", "PORT", "STARBOARD"][activeCamera]
                                                color: appTheme.primary
                                                font.pixelSize: 12
                                                font.bold: true
                                            }

                                            Item { Layout.fillWidth: true }

                                            Row {
                                                spacing: 8
                                                Rectangle {
                                                    width: 24
                                                    height: 24
                                                    radius: 4
                                                    color: isRecording ? appTheme.error : "transparent"
                                                    border.width: 1
                                                    border.color: isRecording ? appTheme.error : appTheme.textDim

                                                    Text {
                                                        anchors.centerIn: parent
                                                        text: "●"
                                                        color: isRecording ? "#FFF" : appTheme.textDim
                                                        font.pixelSize: 10
                                                    }
                                                }

                                                Text {
                                                    text: isRecording ? "REC " + Math.floor(recordingTimerSeconds / 60).toString().padStart(2, '0') + ":" + (recordingTimerSeconds % 60).toString().padStart(2, '0') : "LIVE"
                                                    color: isRecording ? appTheme.error : appTheme.success
                                                    font.pixelSize: 10
                                                    font.bold: true
                                                    anchors.verticalCenter: parent.verticalCenter
                                                }
                                            }
                                        }
                                    }

                                    // Camera Feed
                                    Rectangle {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        color: "#000"

                                        // Live camera feed from backend
                                        Image {
                                            id: cameraFeed
                                            anchors.fill: parent
                                            fillMode: Image.PreserveAspectFit
                                            source: "image://camera" + activeCamera + "/image"
                                            cache: false
                                            asynchronous: true
                                            
                                            // Refresh image when camera frame updates
                                            Connections {
                                                target: backend
                                                function onCameraFrameUpdated(cameraId) {
                                                    if (cameraId === activeCamera) {
                                                        // Force image refresh by changing source
                                                        var timestamp = Date.now()
                                                        cameraFeed.source = "image://camera" + activeCamera + "/image?t=" + timestamp
                                                    }
                                                }
                                            }
                                            
                                            // Placeholder text when no feed
                                            Text {
                                                anchors.centerIn: parent
                                                text: "Camera " + (activeCamera + 1) + "\nConnecting..."
                                                color: appTheme.textDim
                                                font.pixelSize: 16
                                                horizontalAlignment: Text.AlignHCenter
                                                visible: cameraFeed.status !== Image.Ready
                                            }
                                        }
                                        
                                        // Crosshair overlay
                                        Canvas {
                                            anchors.fill: parent
                                            onPaint: {
                                                var ctx = getContext("2d")
                                                var w = width
                                                var h = height
                                                var cx = w / 2
                                                var cy = h / 2
                                                
                                                ctx.strokeStyle = appTheme.primary
                                                ctx.lineWidth = 1
                                                ctx.setLineDash([5, 3])
                                                
                                                // Circle
                                                ctx.beginPath()
                                                ctx.arc(cx, cy, 50, 0, Math.PI * 2)
                                                ctx.stroke()
                                                
                                                // Cross
                                                ctx.setLineDash([])
                                                ctx.beginPath()
                                                ctx.moveTo(cx - 15, cy)
                                                ctx.lineTo(cx + 15, cy)
                                                ctx.moveTo(cx, cy - 15)
                                                ctx.lineTo(cx, cy + 15)
                                                ctx.stroke()
                                            }
                                            Timer {
                                                interval: 1000
                                                running: true
                                                repeat: true
                                                onTriggered: parent.requestPaint()
                                            }
                                        }
                                        
                                        // Depth/Temp overlay
                                        Text {
                                            anchors.left: parent.left
                                            anchors.top: parent.top
                                            anchors.margins: 20
                                            text: depth.toFixed(1) + "m\n" + temperature.toFixed(1) + "°C"
                                            color: appTheme.primary
                                            font.pixelSize: 14
                                            font.bold: true
                                            style: Text.Outline
                                            styleColor: "#000"
                                        }
                                    }
                                }
                            }

                            // Control Panel
                            ColumnLayout {
                                Layout.preferredWidth: 300
                                Layout.fillHeight: true
                                spacing: 8

                                // Compass
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 250
                                    radius: 12
                                    color: "#0a1929"
                                    border.width: 1
                                    border.color: Qt.rgba(0, 212, 255, 0.3)

                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 6

                                        Text {
                                            text: "NAVIGATION COMPASS"
                                            color: appTheme.primary
                                            font.pixelSize: 10
                                            font.letterSpacing: 1
                                            Layout.alignment: Qt.AlignHCenter
                                        }

                                        Item {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                            Layout.alignment: Qt.AlignCenter

                                            // Compass background circle
                                            Rectangle {
                                                anchors.centerIn: parent
                                                width: Math.min(parent.width, parent.height) * 0.85
                                                height: width
                                                radius: width / 2
                                                color: "#0d1d2f"
                                                border.width: 2
                                                border.color: appTheme.primary

                                                // Inner compass ring
                                                Rectangle {
                                                    anchors.centerIn: parent
                                                    width: parent.width - 40
                                                    height: width
                                                    radius: width / 2
                                                    color: "transparent"
                                                    border.width: 1
                                                    border.color: Qt.rgba(0, 212, 255, 0.3)
                                                }

                                                // Center dot
                                                Rectangle {
                                                    anchors.centerIn: parent
                                                    width: 8
                                                    height: 8
                                                    radius: 4
                                                    color: appTheme.primary
                                                }

                                                // N label
                                                Text {
                                                    anchors.horizontalCenter: parent.horizontalCenter
                                                    anchors.top: parent.top
                                                    anchors.topMargin: 15
                                                    text: "N"
                                                    color: appTheme.primary
                                                    font.pixelSize: 16
                                                    font.bold: true
                                                }

                                                // W label
                                                Text {
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    anchors.left: parent.left
                                                    anchors.leftMargin: 12
                                                    text: "W"
                                                    color: appTheme.primary
                                                    font.pixelSize: 16
                                                    font.bold: true
                                                }

                                                // E label
                                                Text {
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    anchors.right: parent.right
                                                    anchors.rightMargin: 12
                                                    text: "E"
                                                    color: appTheme.primary
                                                    font.pixelSize: 16
                                                    font.bold: true
                                                }

                                                // S label
                                                Text {
                                                    anchors.horizontalCenter: parent.horizontalCenter
                                                    anchors.bottom: parent.bottom
                                                    anchors.bottomMargin: 15
                                                    text: "S"
                                                    color: appTheme.primary
                                                    font.pixelSize: 16
                                                    font.bold: true
                                                }

                                                // Rotating heading indicator (triangle)
                                                Canvas {
                                                    id: compassCanvas
                                                    anchors.centerIn: parent
                                                    width: parent.width
                                                    height: parent.height
                                                    rotation: compassHeading

                                                    onPaint: {
                                                        var ctx = getContext("2d")
                                                        var w = width
                                                        var h = height
                                                        var cx = w / 2
                                                        var cy = h / 2
                                                        
                                                        ctx.clearRect(0, 0, w, h)
                                                        
                                                        // Draw triangle pointer
                                                        ctx.fillStyle = appTheme.primary
                                                        ctx.beginPath()
                                                        ctx.moveTo(cx, cy - h/2 + 30)
                                                        ctx.lineTo(cx - 12, cy - h/2 + 55)
                                                        ctx.lineTo(cx + 12, cy - h/2 + 55)
                                                        ctx.closePath()
                                                        ctx.fill()
                                                    }

                                                    Component.onCompleted: requestPaint()
                                                    onRotationChanged: requestPaint()
                                                }
                                            }
                                        }

                                        Text {
                                            text: "HEADING: " + Math.round(compassHeading) + "°"
                                            color: "#FFFFFF"
                                            font.pixelSize: 16
                                            font.bold: true
                                            font.family: "Monospace"
                                            Layout.alignment: Qt.AlignHCenter
                                        }
                                    }
                                }

                                // Arm Button
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 60
                                    radius: 12
                                    color: thrusterArmed ? Qt.rgba(255, 51, 102, 0.15) : Qt.rgba(0, 255, 136, 0.15)
                                    border.width: 2
                                    border.color: thrusterArmed ? "#FF3366" : "#00FF88"

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 10
                                        spacing: 10

                                        Rectangle {
                                            width: 40
                                            height: 40
                                            radius: 6
                                            color: thrusterArmed ? "#FF3366" : "#00FF88"

                                            Text {
                                                anchors.centerIn: parent
                                                text: "⚠"
                                                color: "#000000"
                                                font.pixelSize: 22
                                                font.bold: true
                                            }
                                        }

                                        ColumnLayout {
                                            spacing: 2
                                            Text {
                                                text: "ARM THRUSTERS"
                                                color: "#FFFFFF"
                                                font.pixelSize: 11
                                                font.bold: true
                                            }
                                            Text {
                                                text: thrusterArmed ? "Click to disable thrusters" : "Click to enable thrusters"
                                                color: Qt.rgba(155, 163, 175, 1)
                                                font.pixelSize: 8
                                            }
                                        }

                                        Item { Layout.fillWidth: true }
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: {
                                            backend.toggleArm()
                                        }
                                        cursorShape: Qt.PointingHandCursor
                                    }
                                }

                                // Quick Stats
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    radius: 12
                                    color: "#0a1929"
                                    border.width: 1
                                    border.color: Qt.rgba(0, 212, 255, 0.3)

                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 8

                                        Text {
                                            text: "QUICK STATS"
                                            color: appTheme.primary
                                            font.pixelSize: 10
                                            font.letterSpacing: 1
                                        }

                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                            spacing: 8

                                            // Depth
                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 8
                                                
                                                Text {
                                                    text: "🌊"
                                                    font.pixelSize: 22
                                                }
                                                
                                                ColumnLayout {
                                                    spacing: 0
                                                    Text {
                                                        text: "Depth"
                                                        color: Qt.rgba(155, 163, 175, 1)
                                                        font.pixelSize: 9
                                                    }
                                                    RowLayout {
                                                        spacing: 4
                                                        Text {
                                                            text: depth.toFixed(1)
                                                            color: "#FFFFFF"
                                                            font.pixelSize: 18
                                                            font.bold: true
                                                            font.family: "Monospace"
                                                        }
                                                        Text {
                                                            text: "m"
                                                            color: Qt.rgba(155, 163, 175, 1)
                                                            font.pixelSize: 10
                                                        }
                                                    }
                                                }
                                            }

                                            // Temperature
                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 8
                                                
                                                Text {
                                                    text: "🌡"
                                                    font.pixelSize: 22
                                                }
                                                
                                                ColumnLayout {
                                                    spacing: 0
                                                    Text {
                                                        text: "Temp"
                                                        color: Qt.rgba(155, 163, 175, 1)
                                                        font.pixelSize: 9
                                                    }
                                                    RowLayout {
                                                        spacing: 4
                                                        Text {
                                                            text: temperature.toFixed(1)
                                                            color: "#FFFFFF"
                                                            font.pixelSize: 18
                                                            font.bold: true
                                                            font.family: "Monospace"
                                                        }
                                                        Text {
                                                            text: "°C"
                                                            color: Qt.rgba(155, 163, 175, 1)
                                                            font.pixelSize: 10
                                                        }
                                                    }
                                                }
                                            }

                                            // Pi Connection
                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 8
                                                
                                                Rectangle {
                                                    width: 12
                                                    height: 12
                                                    radius: 6
                                                    color: backend.piConnected ? appTheme.success : appTheme.error
                                                }
                                                
                                                ColumnLayout {
                                                    spacing: 0
                                                    Text {
                                                        text: "Pi Status"
                                                        color: Qt.rgba(155, 163, 175, 1)
                                                        font.pixelSize: 9
                                                    }
                                                    Text {
                                                        text: backend.piConnected ? "Connected" : "Disconnected"
                                                        color: backend.piConnected ? appTheme.success : appTheme.error
                                                        font.pixelSize: 12
                                                        font.bold: true
                                                    }
                                                }
                                            }

                                            // Pixhawk Connection
                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 8
                                                
                                                Rectangle {
                                                    width: 12
                                                    height: 12
                                                    radius: 6
                                                    color: backend.pixhawkConnected ? appTheme.success : appTheme.error
                                                }
                                                
                                                ColumnLayout {
                                                    spacing: 0
                                                    Text {
                                                        text: "Pixhawk"
                                                        color: Qt.rgba(155, 163, 175, 1)
                                                        font.pixelSize: 9
                                                    }
                                                    Text {
                                                        text: backend.pixhawkConnected ? "Connected" : "Disconnected"
                                                        color: backend.pixhawkConnected ? appTheme.success : appTheme.error
                                                        font.pixelSize: 12
                                                        font.bold: true
                                                    }
                                                }
                                            }

                                            // Joystick Connection
                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 8
                                                
                                                Rectangle {
                                                    width: 12
                                                    height: 12
                                                    radius: 6
                                                    color: backend.joystickConnected ? appTheme.success : appTheme.error
                                                }
                                                
                                                ColumnLayout {
                                                    spacing: 0
                                                    Text {
                                                        text: "Joystick"
                                                        color: Qt.rgba(155, 163, 175, 1)
                                                        font.pixelSize: 9
                                                    }
                                                    Text {
                                                        text: backend.joystickConnected ? "Connected" : "Disconnected"
                                                        color: backend.joystickConnected ? appTheme.success : appTheme.error
                                                        font.pixelSize: 12
                                                        font.bold: true
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        // Bottom Stats Bar
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 70
                            radius: 12
                            color: "#0a0a0a"
                            border.width: 1
                            border.color: Qt.rgba(1,1,1,0.2)

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 16

                                Repeater {
                                    model: [
                                        {icon: "📶", label: "SIGNAL", value: "98%", color: appTheme.success},
                                        {icon: "💾", label: "STORAGE", value: "1.2TB", color: appTheme.primary},
                                        {icon: "⏱", label: "UPTIME", value: "24:36:15", color: appTheme.warning},
                                        {icon: "🔌", label: "POWER", value: "2450W", color: appTheme.error},
                                        {icon: "📡", label: "SENSORS", value: "12/12", color: appTheme.success}
                                    ]

                                    delegate: ColumnLayout {
                                        spacing: 4
                                        Text {
                                            text: modelData.icon
                                            font.pixelSize: 20
                                            Layout.alignment: Qt.AlignHCenter
                                        }
                                        Text {
                                            text: modelData.label
                                            color: appTheme.textDim
                                            font.pixelSize: 8
                                            Layout.alignment: Qt.AlignHCenter
                                        }
                                        Text {
                                            text: modelData.value
                                            color: modelData.color
                                            font.pixelSize: 14
                                            font.bold: true
                                            font.family: "Monospace"
                                            Layout.alignment: Qt.AlignHCenter
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // PAGE 1: THRUSTERS
                    ColumnLayout {
                        spacing: 12
                        Layout.margins: 12

                        Text {
                            text: "THRUSTER CONTROL"
                            color: appTheme.text
                            font.pixelSize: 22
                            font.bold: true
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 100
                            radius: 12
                            color: thrusterArmed ? Qt.rgba(255, 51, 102, 0.1) : Qt.rgba(0, 255, 136, 0.1)
                            border.width: 2
                            border.color: thrusterArmed ? appTheme.error : appTheme.success

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 24
                                spacing: 24

                                ColumnLayout {
                                    spacing: 4
                                    Text {
                                        text: thrusterArmed ? "🔒 THRUSTERS ARMED" : "🔓 THRUSTERS DISARMED"
                                        color: thrusterArmed ? appTheme.error : appTheme.success
                                        font.pixelSize: 16
                                        font.bold: true
                                    }
                                    Text {
                                        text: thrusterArmed ? "Warning: Thrusters are active" : "Thrusters are safe for maintenance"
                                        color: appTheme.textDim
                                        font.pixelSize: 11
                                    }
                                }

                                Item { Layout.fillWidth: true }

                                Rectangle {
                                    width: 120
                                    height: 50
                                    radius: 8
                                    color: thrusterArmed ? appTheme.error : appTheme.success
                                    border.width: 2
                                    border.color: Qt.rgba(0,0,0,0.3)

                                    Text {
                                        anchors.centerIn: parent
                                        text: thrusterArmed ? "DISARM" : "ARM"
                                        color: "#000"
                                        font.pixelSize: 14
                                        font.bold: true
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: {
                                            if (typeof backend !== 'undefined') {
                                                backend.toggleArm()
                                            } else {
                                                thrusterArmed = !thrusterArmed
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            columns: 4
                            rowSpacing: 16
                            columnSpacing: 16

                            ThrusterControl {
                                name: "PORT FORWARD"
                                icon: "↑"
                                id: t1
                                enabled: thrusterArmed
                            }
                            ThrusterControl {
                                name: "PORT AFT"
                                icon: "↓"
                                id: t2
                                enabled: thrusterArmed
                            }
                            ThrusterControl {
                                name: "STBD FORWARD"
                                icon: "↑"
                                id: t3
                                enabled: thrusterArmed
                            }
                            ThrusterControl {
                                name: "STBD AFT"
                                icon: "↓"
                                id: t4
                                enabled: thrusterArmed
                            }
                            ThrusterControl {
                                name: "VERTICAL FWD"
                                icon: "↗"
                                id: t5
                                enabled: thrusterArmed
                            }
                            ThrusterControl {
                                name: "VERTICAL AFT"
                                icon: "↖"
                                id: t6
                                enabled: thrusterArmed
                            }
                            ThrusterControl {
                                name: "ROTATION CW"
                                icon: "⟳"
                                id: t7
                                enabled: thrusterArmed
                            }
                            ThrusterControl {
                                name: "ROTATION CCW"
                                icon: "⟲"
                                id: t8
                                enabled: thrusterArmed
                            }
                        }
                    }

                    // PAGE 2: SENSORS
                    ColumnLayout {
                        spacing: 12
                        Layout.margins: 12

                        Text {
                            text: "SENSOR TELEMETRY"
                            color: appTheme.primary
                            font.pixelSize: 22
                            font.bold: true
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            columns: 3
                            rowSpacing: 16
                            columnSpacing: 16

                            SensorCard {
                                title: "Depth"
                                value: depth.toFixed(1)
                                unit: "m"
                                icon: "🌊"
                                chartColor: appTheme.primary
                                min: 0
                                max: 1000
                                current: depth
                            }
                            SensorCard {
                                title: "Temperature"
                                value: temperature.toFixed(1)
                                unit: "°C"
                                icon: "🌡"
                                chartColor: appTheme.warning
                                min: -5
                                max: 40
                                current: temperature
                            }
                            SensorCard {
                                title: "Pressure"
                                value: "24.5"
                                unit: "bar"
                                icon: "⚡"
                                chartColor: appTheme.error
                                min: 0
                                max: 100
                                current: 24.5
                            }
                            SensorCard {
                                title: "Salinity"
                                value: "35.0"
                                unit: "ppt"
                                icon: "🧂"
                                chartColor: Qt.rgba(0.2, 0.8, 1, 1)
                                min: 0
                                max: 50
                                current: 35
                            }
                            SensorCard {
                                title: "pH Level"
                                value: phLevel.toFixed(1)
                                unit: "pH"
                                icon: "⚗"
                                chartColor: Qt.rgba(1, 0.6, 0.2, 1)
                                min: 0
                                max: 14
                                current: phLevel
                            }
                            SensorCard {
                                title: "Oxygen"
                                value: oxygen.toFixed(1)
                                unit: "mg/L"
                                icon: "💨"
                                chartColor: Qt.rgba(0.4, 0.8, 0.4, 1)
                                min: 0
                                max: 15
                                current: oxygen
                            }
                            SensorCard {
                                title: "Turbidity"
                                value: "15.3"
                                unit: "NTU"
                                icon: "🌫"
                                chartColor: Qt.rgba(0.8, 0.8, 0.8, 1)
                                min: 0
                                max: 100
                                current: 15.3
                            }
                            SensorCard {
                                title: "Conductivity"
                                value: "42.5"
                                unit: "mS/cm"
                                icon: "🔌"
                                chartColor: Qt.rgba(1, 0.8, 0.2, 1)
                                min: 0
                                max: 100
                                current: 42.5
                            }
                            SensorCard {
                                title: "ORP"
                                value: "325"
                                unit: "mV"
                                icon: "📊"
                                chartColor: Qt.rgba(0.8, 0.4, 1, 1)
                                min: -1000
                                max: 1000
                                current: 325
                            }
                        }

                        // Sensor Graph
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 200
                            radius: 12
                            color: "#0a0a0a"
                            border.width: 1
                            border.color: Qt.rgba(1,1,1,0.2)

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 8

                                Text {
                                    text: "SENSOR HISTORY (Last 60s)"
                                    color: appTheme.primary
                                    font.pixelSize: 12
                                    font.bold: true
                                }

                                Item {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    Canvas {
                                        anchors.fill: parent
                                        id: sensorGraph

                                        property var depthData: []
                                        property var tempData: []
                                        property int maxPoints: 60

                                        function addData(depthVal, tempVal) {
                                            depthData.push(depthVal)
                                            tempData.push(tempVal)
                                            
                                            if (depthData.length > maxPoints) {
                                                depthData.shift()
                                                tempData.shift()
                                            }
                                            requestPaint()
                                        }

                                        onPaint: {
                                            var ctx = getContext("2d")
                                            var w = width
                                            var h = height
                                            
                                            ctx.clearRect(0, 0, w, h)
                                            
                                            if (depthData.length < 2) return
                                            
                                            // Draw grid
                                            ctx.strokeStyle = Qt.rgba(1,1,1,0.1)
                                            ctx.lineWidth = 1
                                            
                                            // Vertical lines
                                            for (var i = 0; i <= 10; i++) {
                                                ctx.beginPath()
                                                ctx.moveTo(i * w / 10, 0)
                                                ctx.lineTo(i * w / 10, h)
                                                ctx.stroke()
                                            }
                                            
                                            // Horizontal lines
                                            for (var j = 0; j <= 5; j++) {
                                                ctx.beginPath()
                                                ctx.moveTo(0, j * h / 5)
                                                ctx.lineTo(w, j * h / 5)
                                                ctx.stroke()
                                            }
                                            
                                            // Plot depth data
                                            ctx.strokeStyle = appTheme.primary
                                            ctx.lineWidth = 2
                                            ctx.beginPath()
                                            
                                            var maxDepth = Math.max(...depthData)
                                            var minDepth = Math.min(...depthData)
                                            var depthRange = maxDepth - minDepth || 1
                                            
                                            for (var k = 0; k < depthData.length; k++) {
                                                var x = (k / (depthData.length - 1)) * w
                                                var y = h - ((depthData[k] - minDepth) / depthRange) * h * 0.8 - h * 0.1
                                                
                                                if (k === 0) ctx.moveTo(x, y)
                                                else ctx.lineTo(x, y)
                                            }
                                            ctx.stroke()
                                            
                                            // Plot temperature data
                                            ctx.strokeStyle = appTheme.warning
                                            ctx.lineWidth = 2
                                            ctx.beginPath()
                                            
                                            var maxTemp = Math.max(...tempData)
                                            var minTemp = Math.min(...tempData)
                                            var tempRange = maxTemp - minTemp || 1
                                            
                                            for (var l = 0; l < tempData.length; l++) {
                                                var x = (l / (tempData.length - 1)) * w
                                                var y = h - ((tempData[l] - minTemp) / tempRange) * h * 0.8 - h * 0.1
                                                
                                                if (l === 0) ctx.moveTo(x, y)
                                                else ctx.lineTo(x, y)
                                            }
                                            ctx.stroke()
                                        }
                                    }

                                    Timer {
                                        interval: 1000
                                        running: true
                                        repeat: true
                                        onTriggered: sensorGraph.addData(depth, temperature)
                                    }
                                }
                            }
                        }
                    }

                    // PAGE 3: WATER ANALYSIS
                    ColumnLayout {
                        spacing: 12
                        Layout.margins: 12

                        Text {
                            text: "WATER QUALITY ANALYSIS"
                            color: appTheme.text
                            font.pixelSize: 22
                            font.bold: true
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            spacing: 16

                            // Water Parameter Cards
                            GridLayout {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                columns: 2
                                rowSpacing: 16
                                columnSpacing: 16

                                WaterParamCard {
                                    title: "Chemical Analysis"
                                    parameters: [
                                        {name: "Dissolved Oxygen", value: oxygen.toFixed(1) + " mg/L", status: "Good"},
                                        {name: "pH Level", value: phLevel.toFixed(1), status: "Optimal"},
                                        {name: "Salinity", value: "35.0 ppt", status: "Normal"},
                                        {name: "Conductivity", value: "42.5 mS/cm", status: "High"}
                                    ]
                                    color: appTheme.primary
                                }

                                WaterParamCard {
                                    title: "Physical Properties"
                                    parameters: [
                                        {name: "Turbidity", value: "15.3 NTU", status: "Clear"},
                                        {name: "Temperature", value: temperature.toFixed(1) + " °C", status: "Cold"},
                                        {name: "Pressure", value: "24.5 bar", status: "High"},
                                        {name: "Density", value: "1.025 g/cm³", status: "Normal"}
                                    ]
                                    color: appTheme.warning
                                }

                                WaterParamCard {
                                    title: "Nutrient Levels"
                                    parameters: [
                                        {name: "Nitrate", value: "0.2 mg/L", status: "Low"},
                                        {name: "Phosphate", value: "0.05 mg/L", status: "Normal"},
                                        {name: "Silicate", value: "1.8 mg/L", status: "High"},
                                        {name: "Ammonia", value: "0.01 mg/L", status: "Safe"}
                                    ]
                                    color: appTheme.success
                                }

                                WaterParamCard {
                                    title: "Contaminants"
                                    parameters: [
                                        {name: "Heavy Metals", value: "0.003 mg/L", status: "Safe"},
                                        {name: "Microplastics", value: "12 particles/L", status: "Detected"},
                                        {name: "Oil Content", value: "0.01 ppm", status: "Clean"},
                                        {name: "BOD", value: "2.1 mg/L", status: "Good"}
                                    ]
                                    color: appTheme.error
                                }
                            }

                            // Water Quality Index
                            Rectangle {
                                Layout.preferredWidth: 300
                                Layout.fillHeight: true
                                radius: 12
                                color: "#0a0a0a"
                                border.width: 1
                                border.color: Qt.rgba(1,1,1,0.2)

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 16
                                    spacing: 12

                                    Text {
                                        text: "WATER QUALITY INDEX"
                                        color: appTheme.text
                                        font.pixelSize: 14
                                        font.bold: true
                                        Layout.alignment: Qt.AlignHCenter
                                    }

                                    // Gauge
                                    Item {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 200

                                        Canvas {
                                            anchors.fill: parent
                                            id: qualityGauge

                                            property real quality: 0.82

                                            onPaint: {
                                                var ctx = getContext("2d")
                                                var w = width
                                                var h = height
                                                var cx = w / 2
                                                var cy = h / 2
                                                var radius = Math.min(w, h) / 2 - 10

                                                // Outer arc
                                                ctx.beginPath()
                                                ctx.arc(cx, cy, radius, Math.PI * 0.8, Math.PI * 2.2)
                                                ctx.strokeStyle = Qt.rgba(1,1,1,0.2)
                                                ctx.lineWidth = 15
                                                ctx.stroke()

                                                // Quality arc
                                                ctx.beginPath()
                                                var endAngle = Math.PI * 0.8 + (Math.PI * 1.4) * quality
                                                ctx.arc(cx, cy, radius, Math.PI * 0.8, endAngle)
                                                
                                                var gradient = ctx.createLinearGradient(cx - radius, cy, cx + radius, cy)
                                                gradient.addColorStop(0, appTheme.error)
                                                gradient.addColorStop(0.5, appTheme.warning)
                                                gradient.addColorStop(1, appTheme.success)
                                                
                                                ctx.strokeStyle = gradient
                                                ctx.lineWidth = 15
                                                ctx.stroke()

                                                // Center text
                                                ctx.fillStyle = appTheme.text
                                                ctx.font = "bold 24px Arial"
                                                ctx.textAlign = "center"
                                                ctx.textBaseline = "middle"
                                                ctx.fillText((quality * 100).toFixed(0) + "%", cx, cy)

                                                ctx.fillStyle = appTheme.textDim
                                                ctx.font = "12px Arial"
                                                ctx.fillText("WQI", cx, cy + 30)
                                            }
                                        }
                                    }

                                    ColumnLayout {
                                        spacing: 8
                                        QualityIndicator { label: "Excellent"; range: "90-100%"; active: true }
                                        QualityIndicator { label: "Good"; range: "70-89%"; active: false }
                                        QualityIndicator { label: "Fair"; range: "50-69%"; active: false }
                                        QualityIndicator { label: "Poor"; range: "0-49%"; active: false }
                                    }

                                    Text {
                                        text: "Overall Status: Good Water Quality"
                                        color: appTheme.success
                                        font.pixelSize: 12
                                        font.bold: true
                                        Layout.alignment: Qt.AlignHCenter
                                    }
                                }
                            }
                        }

                        // Sample History
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 200
                            radius: 12
                            color: "#0a0a0a"
                            border.width: 1
                            border.color: Qt.rgba(1,1,1,0.2)

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 8

                                Text {
                                    text: "SAMPLE HISTORY"
                                    color: appTheme.primary
                                    font.pixelSize: 14
                                    font.bold: true
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 12

                                    Repeater {
                                        model: 6
                                        SampleCard {
                                            time: index === 0 ? "NOW" : (5 * (index + 1)) + "m ago"
                                            depth: (245 - index * 10).toFixed(0) + "m"
                                            quality: ["Good", "Good", "Fair", "Good", "Excellent", "Good"][index]
                                            temperature: (12 + index * 0.5).toFixed(1) + "°C"
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // PAGE 4: MEDIA GALLERY
                    ColumnLayout {
                        spacing: 12
                        Layout.margins: 12

                        RowLayout {
                            Layout.fillWidth: true
                            
                            Text {
                                text: "MEDIA GALLERY"
                                color: appTheme.text
                                font.pixelSize: 22
                                font.bold: true
                            }
                            
                            Item { Layout.fillWidth: true }
                            
                            Button {
                                text: "🔄 Refresh"
                                onClicked: {
                                    if (typeof backend !== 'undefined') {
                                        mediaFilesModel.clear()
                                        var files = backend.getMediaFiles()
                                        for (var i = 0; i < files.length; i++) {
                                            mediaFilesModel.append(files[i])
                                        }
                                        
                                        var stats = backend.getMediaStats()
                                        photosCount.text = stats.photos_count.toString()
                                        photosSize.text = (stats.photos_size / (1024*1024*1024)).toFixed(2) + " GB"
                                        videosCount.text = stats.videos_count.toString()
                                        videosSize.text = (stats.videos_size / (1024*1024*1024)).toFixed(2) + " GB"
                                    }
                                }
                            }
                        }

                        RowLayout {
                            spacing: 16

                            MediaStatsCard {
                                icon: "📸"
                                label: "Photos"
                                count: photosCount.text
                                size: photosSize.text
                                color: blackTheme.primary
                                
                                Text { id: photosCount; visible: false; text: "0" }
                                Text { id: photosSize; visible: false; text: "0 GB" }
                            }

                            MediaStatsCard {
                                icon: "📹"
                                label: "Videos"
                                count: videosCount.text
                                size: videosSize.text
                                color: blackTheme.primary
                                
                                Text { id: videosCount; visible: false; text: "0" }
                                Text { id: videosSize; visible: false; text: "0 GB" }
                            }
                        }

                        ListModel {
                            id: mediaFilesModel
                        }

                        GridView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            cellWidth: 200
                            cellHeight: 180
                            clip: true
                            model: mediaFilesModel

                            delegate: MediaTile {
                                type: model.type || "photo"
                                timestamp: {
                                    if (model.timestamp) {
                                        var date = new Date(model.timestamp * 1000)
                                        return date.toLocaleTimeString()
                                    }
                                    return ""
                                }
                                depth: model.name ? model.name.substring(0, 20) : ""
                                filePath: model.path || ""
                                fileUrl: model.url || ""
                                
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        console.log("Opening media:", model.path)
                                        if (typeof backend !== 'undefined' && model.path) {
                                            backend.openMediaFile(model.path)
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Auto-load media on page open
                        Component.onCompleted: {
                            if (typeof backend !== 'undefined') {
                                var files = backend.getMediaFiles()
                                for (var i = 0; i < files.length; i++) {
                                    mediaFilesModel.append(files[i])
                                }
                                
                                var stats = backend.getMediaStats()
                                photosCount.text = stats.photos_count.toString()
                                photosSize.text = (stats.photos_size / (1024*1024*1024)).toFixed(2) + " GB"
                                videosCount.text = stats.videos_count.toString()
                                videosSize.text = (stats.videos_size / (1024*1024*1024)).toFixed(2) + " GB"
                            }
                        }
                    }

                    // PAGE 5: SETTINGS
                    ColumnLayout {
                        spacing: 12
                        Layout.margins: 12

                        Text {
                            text: "SYSTEM SETTINGS"
                            color: appTheme.primary
                            font.pixelSize: 22
                            font.bold: true
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            spacing: 16

                            // Settings Categories
                            ColumnLayout {
                                Layout.preferredWidth: 250
                                Layout.fillHeight: true
                                spacing: 8

                                SettingsCategory {
                                    icon: "📷"; label: "Video"
                                    active: true
                                }
                                SettingsCategory {
                                    icon: "⚡"; label: "Thrusters"
                                }
                                SettingsCategory {
                                    icon: "📡"; label: "Sensors"
                                }
                                SettingsCategory {
                                    icon: "🔧"; label: "System"
                                }
                                SettingsCategory {
                                    icon: "🔒"; label: "Security"
                                }
                                SettingsCategory {
                                    icon: "📶"; label: "Network"
                                }

                                Item { Layout.fillHeight: true }

                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 50
                                    radius: 8
                                    color: Qt.rgba(255, 51, 102, 0.2)
                                    border.width: 1
                                    border.color: appTheme.error

                                    Text {
                                        anchors.centerIn: parent
                                        text: "⚙ SYSTEM REBOOT"
                                        color: appTheme.error
                                        font.pixelSize: 12
                                        font.bold: true
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: console.log("System reboot requested")
                                    }
                                }
                            }

                            // Settings Panel
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                radius: 12
                                color: "#0a0a0a"
                                border.width: 1
                                border.color: Qt.rgba(1,1,1,0.2)

                                ScrollView {
                                    anchors.fill: parent
                                    anchors.margins: 1
                                    clip: true

                                    ColumnLayout {
                                        width: parent.width - 20
                                        spacing: 12
                        Layout.margins: 12

                                        SettingGroup {
                                            title: "Video Settings"
                                            settings: [
                                                {label: "Resolution", value: "1920x1080 @ 60Hz"},
                                                {label: "Bitrate", value: "20 Mbps"},
                                                {label: "Codec", value: "H.265"},
                                                {label: "Recording Format", value: "MP4"}
                                            ]
                                        }

                                        SettingGroup {
                                            title: "Thruster Configuration"
                                            settings: [
                                                {label: "Max Power", value: "100%"},
                                                {label: "Response Curve", value: "Linear"},
                                                {label: "Safety Limit", value: "85%"},
                                                {label: "Deadzone", value: "5%"}
                                            ]
                                        }

                                        SettingGroup {
                                            title: "Sensor Settings"
                                            settings: [
                                                {label: "Sampling Rate", value: "10 Hz"},
                                                {label: "Data Logging", value: "Enabled"},
                                                {label: "Calibration", value: "Auto"},
                                                {label: "Alert Thresholds", value: "Custom"}
                                            ]
                                        }

                                        SettingGroup {
                                            title: "System Information"
                                            settings: [
                                                {label: "Firmware Version", value: "v2.1.0"},
                                                {label: "Serial Number", value: "AURA-2024-001"},
                                                {label: "Uptime", value: "24d 6h 12m"},
                                                {label: "Last Calibration", value: "2024-03-15"}
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // COMPONENTS
    component NavBtn: Rectangle {
        property string icon: ""
        property string label: ""
        property bool active: false
        
        Layout.fillWidth: true
        Layout.preferredHeight: 50
        radius: 8
        color: active ? Qt.rgba(0, 0.83, 1, 0.2) : "transparent"
        border.width: active ? 1 : 0
        border.color: appTheme.primary

        RowLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 12

            Text {
                text: icon
                font.pixelSize: 16
                color: active ? appTheme.primary : appTheme.textDim
            }

            Text {
                text: label
                color: active ? appTheme.primary : appTheme.text
                font.pixelSize: 12
                font.bold: active
            }

            Item { Layout.fillWidth: true }

            Rectangle {
                width: 8
                height: 8
                radius: 4
                color: active ? appTheme.primary : "transparent"
            }
        }

        MouseArea {
            anchors.fill: parent
            onClicked: parent.clicked()
        }
        
        signal clicked()
    }

    component MediaButton: Rectangle {
        property string icon: ""
        property bool active: false
        property string tooltip: ""
        
        width: 48
        height: 48
        radius: 8
        color: active ? Qt.rgba(1,1,1,0.2) : Qt.rgba(1,1,1,0.1)
        border.width: 1
        border.color: active ? appTheme.primary : Qt.rgba(1,1,1,0.2)

        Text {
            anchors.centerIn: parent
            text: icon
            font.pixelSize: 20
            color: active ? appTheme.primary : appTheme.textDim
        }

        MouseArea {
            anchors.fill: parent
            onClicked: parent.clicked()
            hoverEnabled: true
            onEntered: {
                // Tooltip could be implemented here
            }
        }
        
        signal clicked()
    }

    component StatusDot: Rectangle {
        property bool active: false
        property color dotColor: appTheme.success
        
        width: 8
        height: 8
        radius: 4
        color: parent.dotColor
        opacity: active ? 1 : 0.3
    }

    component QuickStat: ColumnLayout {
        property string icon: ""
        property string label: ""
        property string value: ""
        property string unit: ""
        property color color: appTheme.primary
        
        spacing: 2
        Text {
            text: icon
            font.pixelSize: 20
            Layout.alignment: Qt.AlignHCenter
        }
        Text {
            text: label
            color: appTheme.textDim
            font.pixelSize: 9
            Layout.alignment: Qt.AlignHCenter
        }
        Text {
            text: value
            color: color
            font.pixelSize: 16
            font.bold: true
            font.family: "Monospace"
            Layout.alignment: Qt.AlignHCenter
        }
        Text {
            text: unit
            color: appTheme.textDim
            font.pixelSize: 8
            Layout.alignment: Qt.AlignHCenter
        }
    }

    component ThrusterControl: Rectangle {
        property string name: ""
        property string icon: ""
        property string id: ""
        property bool enabled: true
        
        Layout.fillWidth: true
        Layout.fillHeight: true
        radius: 12
        color: "#0a0a0a"
        border.width: 1
        border.color: Qt.rgba(1,1,1,0.2)

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 8

            RowLayout {
                spacing: 8
                Text {
                    text: icon
                    font.pixelSize: 24
                    color: enabled ? appTheme.primary : appTheme.textDim
                }
                ColumnLayout {
                    spacing: 2
                    Text {
                        text: id
                        color: appTheme.textDim
                        font.pixelSize: 10
                        font.bold: true
                    }
                    Text {
                        text: name
                        color: enabled ? appTheme.text : appTheme.textDim
                        font.pixelSize: 9
                        wrapMode: Text.WordWrap
                    }
                }
                Item { Layout.fillWidth: true }
            }

            Slider {
                Layout.fillWidth: true
                from: -100
                to: 100
                value: 0
                enabled: enabled
                
                background: Rectangle {
                    x: parent.leftPadding
                    y: parent.topPadding + parent.availableHeight / 2 - height / 2
                    implicitWidth: 200
                    implicitHeight: 6
                    width: parent.availableWidth
                    height: implicitHeight
                    radius: 3
                    color: Qt.rgba(1,1,1,0.1)
                    
                    Rectangle {
                        x: parent.width / 2
                        width: 1
                        height: parent.height
                        color: Qt.rgba(1,1,1,0.3)
                    }
                    
                    Rectangle {
                        width: Math.abs(parent.visualPosition - 0.5) * parent.width * 2
                        height: parent.height
                        x: parent.visualPosition < 0.5 ? parent.visualPosition * parent.width : parent.width / 2
                        color: parent.visualPosition < 0.5 ? appTheme.error : appTheme.success
                        radius: 3
                    }
                }
                
                handle: Rectangle {
                    x: parent.leftPadding + parent.visualPosition * (parent.availableWidth - width)
                    y: parent.topPadding + parent.availableHeight / 2 - height / 2
                    implicitWidth: 20
                    implicitHeight: 20
                    radius: 10
                    color: enabled ? appTheme.primary : appTheme.textDim
                    border.width: 2
                    border.color: appTheme.bg
                }
            }

            Text {
                text: Math.round(parent.children[1].value) + "%"
                color: Math.round(parent.children[1].value) === 0 ? appTheme.textDim : 
                       Math.round(parent.children[1].value) > 0 ? appTheme.success : appTheme.error
                font.pixelSize: 12
                font.bold: true
                font.family: "Monospace"
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }

    component SensorCard: Rectangle {
        property string title: ""
        property string value: ""
        property string unit: ""
        property string icon: ""
        property color chartColor: appTheme.primary
        property real min: 0
        property real max: 100
        property real current: 50
        
        Layout.fillWidth: true
        Layout.fillHeight: true
        radius: 12
        color: "#0a0a0a"
        border.width: 1
        border.color: Qt.rgba(1,1,1,0.2)

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            RowLayout {
                spacing: 12
                Text {
                    text: icon
                    font.pixelSize: 24
                }
                ColumnLayout {
                    spacing: 2
                    Text {
                        text: title
                        color: appTheme.textDim
                        font.pixelSize: 11
                    }
                    Text {
                        text: value + " " + unit
                        color: chartColor
                        font.pixelSize: 18
                        font.bold: true
                        font.family: "Monospace"
                    }
                }
                Item { Layout.fillWidth: true }
            }

            // Progress bar showing value in range
            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: 8
                
                Rectangle {
                    anchors.fill: parent
                    radius: 4
                    color: Qt.rgba(1,1,1,0.1)
                    
                    Rectangle {
                        width: parent.width * ((current - min) / (max - min))
                        height: parent.height
                        radius: 4
                        color: chartColor
                    }
                }
            }

            RowLayout {
                Text {
                    text: min + " " + unit
                    color: appTheme.textDim
                    font.pixelSize: 8
                }
                Item { Layout.fillWidth: true }
                Text {
                    text: max + " " + unit
                    color: appTheme.textDim
                    font.pixelSize: 8
                }
            }
        }
    }

    component WaterParamCard: Rectangle {
        property string title: ""
        property var parameters: []
        property color cardColor: appTheme.primary
        
        Layout.fillWidth: true
        Layout.fillHeight: true
        radius: 12
        color: "#0a0a0a"
        border.width: 1
        border.color: Qt.rgba(1,1,1,0.2)

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            Text {
                text: title
                color: appTheme.text
                font.pixelSize: 14
                font.bold: true
            }

            ColumnLayout {
                spacing: 8
                Repeater {
                    model: parameters
                    delegate: RowLayout {
                        Layout.fillWidth: true
                        Text {
                            text: modelData.name
                            color: appTheme.text
                            font.pixelSize: 10
                            Layout.preferredWidth: 120
                        }
                        Item { Layout.fillWidth: true }
                        Text {
                            text: modelData.value
                            color: appTheme.text
                            font.pixelSize: 10
                            font.family: "Monospace"
                        }
                        Item { Layout.preferredWidth: 8 }
                        Rectangle {
                            width: 8
                            height: 8
                            radius: 4
                            color: {
                                switch(modelData.status) {
                                case "Good": return appTheme.success;
                                case "Optimal": return appTheme.success;
                                case "Normal": return appTheme.primary;
                                case "High": return appTheme.warning;
                                case "Low": return appTheme.warning;
                                case "Safe": return appTheme.success;
                                case "Detected": return appTheme.warning;
                                case "Clean": return appTheme.success;
                                default: return appTheme.textDim;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    component QualityIndicator: RowLayout {
        property string label: ""
        property string range: ""
        property bool active: false
        
        spacing: 8
        Rectangle {
            width: 12
            height: 12
            radius: 6
            color: active ? appTheme.success : Qt.rgba(1,1,1,0.2)
        }
        Text {
            text: label
            color: active ? appTheme.text : appTheme.textDim
            font.pixelSize: 10
        }
        Item { Layout.fillWidth: true }
        Text {
            text: range
            color: appTheme.textDim
            font.pixelSize: 8
        }
    }

    component SampleCard: Rectangle {
        property string time: ""
        property string depth: ""
        property string quality: ""
        property string temperature: ""
        
        Layout.fillWidth: true
        Layout.preferredHeight: 80
        radius: 8
        color: "#0a0a0a"
        border.width: 1
        border.color: Qt.rgba(1,1,1,0.2)

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 4

            RowLayout {
                Text {
                    text: "⏱ " + time
                    color: appTheme.textDim
                    font.pixelSize: 9
                }
                Item { Layout.fillWidth: true }
                Text {
                    text: depth
                    color: appTheme.primary
                    font.pixelSize: 10
                    font.bold: true
                }
            }

            RowLayout {
                Text {
                    text: "Quality: " + quality
                    color: {
                        switch(quality) {
                        case "Excellent": return appTheme.success;
                        case "Good": return appTheme.primary;
                        case "Fair": return appTheme.warning;
                        default: return appTheme.text;
                        }
                    }
                    font.pixelSize: 10
                }
                Item { Layout.fillWidth: true }
                Text {
                    text: temperature
                    color: appTheme.warning
                    font.pixelSize: 10
                }
            }
        }
    }

    component MediaStatsCard: Rectangle {
        property string icon: ""
        property string label: ""
        property string count: ""
        property string size: ""
        property color accentColor: appTheme.primary
        
        Layout.fillWidth: true
        Layout.preferredHeight: 100
        radius: 12
        color: "#1a1a1a"
        border.width: 1
        border.color: Qt.rgba(1,1,1,0.3)

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 8

            RowLayout {
                spacing: 12
                Text {
                    text: icon
                    font.pixelSize: 24
                    color: accentColor
                }
                ColumnLayout {
                    spacing: 2
                    Text {
                        text: label
                        color: "#909090"
                        font.pixelSize: 11
                    }
                    Text {
                        text: count + " files"
                        color: "#FFFFFF"
                        font.pixelSize: 16
                        font.bold: true
                    }
                }
                Item { Layout.fillWidth: true }
            }

            Text {
                text: size
                color: "#CCCCCC"
                font.pixelSize: 10
            }
        }
    }

    component MediaTile: Rectangle {
        property string type: "photo"
        property string timestamp: ""
        property string depth: ""
        property string filePath: ""
        property string fileUrl: ""
        
        width: 180
        height: 160
        radius: 8
        color: "#1a1a1a"
        border.width: 1
        border.color: Qt.rgba(1,1,1,0.3)

        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: 7
            color: type === "video" ? Qt.rgba(255, 51, 102, 0.15) : 
                   type === "photo" ? Qt.rgba(0, 212, 255, 0.15) : 
                   Qt.rgba(0, 255, 136, 0.15)

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 4

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 4
                    color: Qt.rgba(0,0,0,0.8)
                    clip: true

                    // Image preview for photos
                    Image {
                        anchors.fill: parent
                        source: type === "photo" ? fileUrl : ""
                        fillMode: Image.PreserveAspectCrop
                        smooth: true
                        visible: type === "photo" && status === Image.Ready
                        
                        onStatusChanged: {
                            if (status === Image.Error) {
                                console.log("Error loading image:", fileUrl)
                            }
                        }
                    }
                    
                    // Video icon overlay
                    Rectangle {
                        anchors.centerIn: parent
                        width: 50
                        height: 50
                        radius: 25
                        color: Qt.rgba(0,0,0,0.7)
                        visible: type === "video"
                        
                        Text {
                            anchors.centerIn: parent
                            text: "▶"
                            font.pixelSize: 24
                            color: appTheme.error
                        }
                    }
                    
                    // Fallback icon if image fails to load
                    Text {
                        anchors.centerIn: parent
                        text: type === "video" ? "▶" : type === "photo" ? "📸" : "📊"
                        font.pixelSize: 32
                        color: type === "video" ? appTheme.error : type === "photo" ? appTheme.primary : appTheme.success
                        visible: type !== "photo" || (type === "photo" && parent.children[0].status !== Image.Ready)
                    }
                }

                RowLayout {
                    spacing: 4
                    Text {
                        text: type === "video" ? "Video" : type === "photo" ? "Photo" : "Data"
                        color: "#CCCCCC"
                        font.pixelSize: 8
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: timestamp
                        color: "#999999"
                        font.pixelSize: 7
                    }
                }

                Text {
                    text: depth
                    color: "#FFFFFF"
                    font.pixelSize: 8
                    font.bold: false
                    elide: Text.ElideMiddle
                    Layout.fillWidth: true
                }
            }
        }
    }

    component SettingsCategory: Rectangle {
        property string icon: ""
        property string label: ""
        property bool active: false
        
        Layout.fillWidth: true
        Layout.preferredHeight: 50
        radius: 8
        color: active ? Qt.rgba(0, 0.83, 1, 0.2) : "transparent"
        border.width: active ? 1 : 0
        border.color: appTheme.primary

        RowLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 12

            Text {
                text: icon
                font.pixelSize: 16
                color: active ? appTheme.primary : appTheme.textDim
            }

            Text {
                text: label
                color: active ? appTheme.primary : appTheme.text
                font.pixelSize: 12
            }

            Item { Layout.fillWidth: true }

            Rectangle {
                width: 8
                height: 8
                radius: 4
                color: active ? appTheme.primary : "transparent"
            }
        }

        MouseArea {
            anchors.fill: parent
            onClicked: console.log("Selected:", label)
        }
    }

    component SettingGroup: ColumnLayout {
        property string title: ""
        property var settings: []
        
        Layout.fillWidth: true
        spacing: 8

        Text {
            text: title
            color: appTheme.primary
            font.pixelSize: 14
            font.bold: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: settings.length * 50
            radius: 8
            color: "#0a0a0a"
            border.width: 1
            border.color: Qt.rgba(1,1,1,0.2)

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 1
                spacing: 1

                Repeater {
                    model: settings
                    delegate: Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 49
                        color: index % 2 === 0 ? "transparent" : Qt.rgba(1,1,1,0.02)

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 12

                            Text {
                                text: modelData.label
                                color: appTheme.text
                                font.pixelSize: 11
                            }

                            Item { Layout.fillWidth: true }

                            Text {
                                text: modelData.value
                                color: appTheme.primary
                                font.pixelSize: 11
                                font.bold: true
                            }
                        }
                    }
                }
            }
        }
    }
    
    // Notification Popup
    Popup {
        id: notificationPopup
        x: (parent.width - width) / 2
        y: 80
        width: 400
        height: 100
        modal: false
        focus: false
        closePolicy: Popup.NoAutoClose
        
        background: Rectangle {
            color: appTheme.dark
            border.width: 2
            border.color: appTheme.primary
            radius: 8
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 8
            
            Text {
                id: notificationText
                Layout.fillWidth: true
                color: appTheme.text
                font.pixelSize: 14
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.Wrap
            }
        }
        
        Timer {
            id: notificationTimer
            interval: 3000
            onTriggered: notificationPopup.close()
        }
    }
}





