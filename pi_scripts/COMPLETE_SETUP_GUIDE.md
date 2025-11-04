# 🍓 Complete Raspberry Pi Setup - Camera & Pixhawk Detection

## 📋 Quick Setup Steps

### 1️⃣ Copy Scripts to Raspberry Pi

From Windows:

```powershell
cd "E:\UIU MARINER\mariner-software-1.0"
scp -r pi_scripts pi@raspberrypi.local:~/mariner/
# Password: 1234
```

### 2️⃣ SSH to Raspberry Pi

```bash
ssh pi@raspberrypi.local
# Password: 1234
```

### 3️⃣ Make Scripts Executable

```bash
cd ~/mariner/pi_scripts
chmod +x *.sh *.py
```

---

## 🔍 Step 1: Detect Pixhawk

Run the Pixhawk detection script:

```bash
python3 detect_pixhawk.py
```

### What It Does:

- Scans all serial ports: `/dev/ttyAMA0`, `/dev/serial0`, `/dev/ttyUSB0`, `/dev/ttyACM0`, etc.
- Tests baud rates: 115200, 57600, 38400, 19200, 9600
- Waits for MAVLink HEARTBEAT message
- Shows which port and baud rate works

### Expected Output:

```
✅ PIXHAWK FOUND!
Port: /dev/ttyACM0
Baud Rate: 57600

🔧 Use these settings in your configuration:
   MAVLink Master: /dev/ttyACM0
   Baud Rate: 57600
```

### If Not Found:

1. Check USB cable (must be data cable, not charge-only)
2. Verify Pixhawk is powered on
3. Enable UART:
   ```bash
   sudo raspi-config
   # Interface Options → Serial Port
   # Login shell: NO
   # Hardware enabled: YES
   ```
4. Add user to dialout group:
   ```bash
   sudo usermod -a -G dialout pi
   sudo reboot
   ```

---

## 📹 Step 2: Detect Cameras

Run the camera detection script:

```bash
./detect_cameras.sh
```

### What It Does:

- Detects Raspberry Pi Camera Module (via libcamera)
- Detects USB webcams (/dev/video\*)
- Shows device details and capabilities

### Expected Output:

**For Pi Camera:**

```
✅ Pi Camera Module detected!
0: imx219 [3280x2464] (/base/soc/i2c0mux/i2c@1/imx219@10)
```

**For USB Webcam:**

```
✅ USB webcams detected!
/dev/video0: USB 2.0 Camera
```

### Troubleshooting:

**Pi Camera Not Detected:**

```bash
# 1. Enable camera
sudo raspi-config
# Interface Options → Camera → Enable

# 2. Check cable connection (blue side to camera, metal contacts facing away from ethernet)

# 3. Reboot
sudo reboot

# 4. Test
libcamera-hello --camera 0 -t 5000
```

**USB Webcam Not Detected:**

```bash
# 1. Check device is listed
lsusb

# 2. Check video devices
ls -l /dev/video*

# 3. Install v4l2-utils
sudo apt-get install v4l2-utils

# 4. Test device
v4l2-ctl --device=/dev/video0 --all
```

---

## 🚀 Step 3: Start Streaming

### Option A: Pi Camera Module

**Camera 0:**

```bash
./cam0.sh 192.168.0.104
```

**Camera 1 (if you have 2 Pi cameras):**

```bash
./cam1.sh 192.168.0.104
```

### Option B: USB Webcam

**USB Camera 0:**

```bash
./usb_cam0.sh 192.168.0.104
```

**USB Camera 1:**

```bash
./usb_cam1.sh 192.168.0.104
```

### Option C: Mixed (Pi + USB)

Use Pi Camera for camera 0, USB for camera 1:

```bash
# Terminal 1
./cam0.sh 192.168.0.104

# Terminal 2 (or use screen)
./usb_cam0.sh 192.168.0.104
```

---

## 🎯 Step 4: Start All Services

### Update start_all_services.sh

If you're using USB cameras, edit the start script:

```bash
nano start_all_services.sh
```

**Change camera sections:**

```bash
# For Pi Camera (libcamera)
screen -dmS cam0 bash -c "cd $SCRIPT_DIR && ./cam0.sh $GROUND_STATION_IP"

# For USB Camera
screen -dmS cam0 bash -c "cd $SCRIPT_DIR && ./usb_cam0.sh $GROUND_STATION_IP"
```

### Start All Services:

```bash
./start_all_services.sh 192.168.0.104
```

This starts:

- ✅ Sensor server (BMP388)
- ✅ MAVProxy server (Pixhawk)
- ✅ Camera 0 stream
- ✅ Camera 1 stream

---

## 📊 Step 5: Verify Everything

### Check Services Running:

```bash
screen -ls
```

Should show:

```
4 Sockets in /run/screen/S-pi.
        12345.sensors   (Detached)
        12346.mavproxy  (Detached)
        12347.cam0      (Detached)
        12348.cam1      (Detached)
```

### View Logs:

**Sensor Server:**

```bash
screen -r sensors
# Press Ctrl+A then D to detach
```

**MAVProxy:**

```bash
screen -r mavproxy
# Should show: HEARTBEAT messages from Pixhawk
```

**Camera 0:**

```bash
screen -r cam0
# Should show: GStreamer pipeline running
```

### Test from Windows:

```powershell
# Test sensor port
Test-NetConnection raspberrypi.local -Port 5000

# Test MAVProxy port
Test-NetConnection raspberrypi.local -Port 7000

# Launch application
python launch_mariner.py
```

---

## 🎮 Step 6: Test Joystick Control

Once application launches:

1. **Move left joystick** - See thruster output in logs:

   ```
   [THRUSTER] Forward/Back: -0.85 → Ch1(Pin1)=1300, Ch8(Pin8)=1700
   ```

2. **Move right joystick** - See up/down thruster output:

   ```
   [THRUSTER] Up/Down: 0.65 → Ch3(Pin3)=1650, Ch4(Pin4)=1650, Ch6(Pin6)=1350, Ch7(Pin7)=1350
   ```

3. **Press buttons** - See button actions logged

---

## 📋 Common Device Configurations

### Configuration 1: Pi Camera Module + Pixhawk USB

```bash
# Pixhawk: /dev/ttyACM0 @ 57600 baud
# Camera: libcamera (CSI connector)

./detect_pixhawk.py        # Find: /dev/ttyACM0
./detect_cameras.sh         # Find: Pi Camera
./start_all_services.sh 192.168.0.104
```

### Configuration 2: USB Webcam + Pixhawk UART

```bash
# Pixhawk: /dev/serial0 @ 57600 baud (GPIO pins)
# Camera: /dev/video0 (USB)

./detect_pixhawk.py        # Find: /dev/serial0
./detect_cameras.sh         # Find: /dev/video0
# Edit start_all_services.sh to use usb_cam0.sh
./start_all_services.sh 192.168.0.104
```

### Configuration 3: Dual USB Cameras + Pixhawk USB

```bash
# Pixhawk: /dev/ttyACM0 @ 115200 baud
# Camera 0: /dev/video0
# Camera 1: /dev/video1

./detect_pixhawk.py        # Find: /dev/ttyACM0
./detect_cameras.sh         # Find: /dev/video0, /dev/video1
# Edit start_all_services.sh for both USB cameras
./start_all_services.sh 192.168.0.104
```

---

## 🔧 Troubleshooting

### Pixhawk Not Connecting

**Symptom:** `[WinError 10061] No connection could be made`

**Solution:**

```bash
# 1. Run detection script
python3 detect_pixhawk.py

# 2. Update pi_mavproxy_server.py with correct port/baud
nano pi_mavproxy_server.py
# Change --master and --baudrate values

# 3. Restart MAVProxy
screen -X -S mavproxy quit
screen -dmS mavproxy python3 pi_mavproxy_server.py --master /dev/ttyACM0 --baudrate 57600 --port 7000
```

### Camera Not Streaming

**Symptom:** `[CAM0] ❌ Failed to open`

**Solution:**

```bash
# 1. Run detection script
./detect_cameras.sh

# 2. For Pi Camera: Check libcamera works
libcamera-hello --camera 0 -t 5000

# 3. For USB: Check device exists
ls -l /dev/video0

# 4. Test GStreamer pipeline manually
gst-launch-1.0 v4l2src device=/dev/video0 ! videoconvert ! autovideosink
```

### No Thruster Logs

**Symptom:** Joystick moves but no `[THRUSTER]` logs

**Solution:**

- Pixhawk must be connected first!
- Check MAVProxy is running: `screen -r mavproxy`
- Verify heartbeat messages appearing
- ARM the system before thrusters activate

---

## ✅ Success Checklist

- [ ] Pixhawk detected: `python3 detect_pixhawk.py` shows port/baud
- [ ] Camera detected: `./detect_cameras.sh` finds devices
- [ ] Scripts executable: `chmod +x *.sh *.py`
- [ ] All services started: `./start_all_services.sh 192.168.0.104`
- [ ] Services running: `screen -ls` shows 4 sessions
- [ ] Application connects: No `[WinError 10061]` errors
- [ ] Camera feeds working: Video displays in GUI
- [ ] Sensors updating: Depth/temp/pressure changing
- [ ] Joystick logged: `[THRUSTER]` messages appear
- [ ] Pixhawk responds: Can ARM system

---

## 📞 Quick Commands Reference

```bash
# Detection
python3 detect_pixhawk.py                # Find Pixhawk port/baud
./detect_cameras.sh                      # Find cameras

# Start Services
./start_all_services.sh 192.168.0.104   # Start everything

# View Services
screen -ls                               # List running services
screen -r sensors                        # View sensor logs
screen -r mavproxy                       # View Pixhawk logs
screen -r cam0                           # View camera logs

# Stop Services
./stop_all_services.sh                   # Stop everything
screen -X -S sensors quit                # Stop one service

# Camera Tests
libcamera-hello --camera 0 -t 5000      # Test Pi camera
v4l2-ctl --device=/dev/video0 --all     # Test USB camera

# Pixhawk Tests
python3 -m pymavlink.mavproxy --master=/dev/ttyACM0 --baudrate=57600
```

---

**🎉 Now you're ready for full ROV operation!** 🌊🤖
