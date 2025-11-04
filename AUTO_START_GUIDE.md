# 🚀 AUTO-START SETUP GUIDE

This guide will set up your ROV system so that **everything connects automatically** when you open the Windows application. One-time setup required on Raspberry Pi.

---

## ✅ What You'll Get

After setup:

1. **Turn on Raspberry Pi** → All services start automatically
2. **Open Windows app** → Everything connects immediately
3. **No manual commands needed** → Zero configuration

Services that auto-start:

- 🌡️ BMP388 Sensor Server (Port 5000)
- 🎮 MAVProxy for Pixhawk (Port 7000)
- 📹 Camera 0 Stream (UDP 5000)
- 📹 Camera 1 Stream (UDP 5001)

---

## 📋 Prerequisites

1. ✅ Raspberry Pi with hostname: `raspberrypi.local`
2. ✅ Windows PC with Python environment
3. ✅ Both on same network
4. ✅ Hardware connected:
   - Pixhawk flight controller
   - BMP388 pressure sensor (I2C)
   - 2x Cameras (Pi Camera or USB webcams)
   - Nintendo Switch Pro Controller (USB/Bluetooth)

---

## 🔧 One-Time Setup (Raspberry Pi)

### Step 1: Copy Scripts to Raspberry Pi

From Windows PowerShell:

```powershell
scp -r pi_scripts pi@raspberrypi.local:~/mariner/
```

**Password:** `1234`

---

### Step 2: SSH to Raspberry Pi

```powershell
ssh pi@raspberrypi.local
```

**Password:** `1234`

---

### Step 3: Make Scripts Executable

```bash
cd ~/mariner/pi_scripts
chmod +x *.sh *.py
```

---

### Step 4: Detect Hardware (Important!)

#### Find Pixhawk Port and Baud Rate:

```bash
python3 detect_pixhawk.py
```

**Example Output:**

```
✅ Found Pixhawk at /dev/ttyUSB0 with baud rate 115200
```

#### Find Cameras:

```bash
./detect_cameras.sh
```

**Example Output:**

```
✅ Found Pi Camera: [0] imx219
✅ Found USB Webcam: /dev/video0 - Logitech HD Webcam
```

**📝 Note down:**

- Pixhawk port (e.g., `/dev/ttyUSB0`)
- Pixhawk baud rate (e.g., `115200`)
- Camera devices (e.g., `/dev/video0`, `/dev/video2`)

---

### Step 5: Install Auto-Start Services

```bash
sudo ./install_autostart.sh
```

**When prompted:**

1. **Ground Station IP:** Enter your Windows PC IP address
   - Find it with `ipconfig` on Windows (look for IPv4 address)
   - Example: `192.168.0.104`

**The script will:**

- ✅ Create 4 systemd services
- ✅ Enable auto-start on boot
- ✅ Start services immediately
- ✅ Configure auto-restart on failure

---

### Step 6: Verify Services Started

```bash
./rov_services.sh status
```

**Expected Output:**

```
📊 ROV Service Status:
====================
✅ Sensors:  Running
✅ MAVProxy: Running
✅ Camera 0: Running
✅ Camera 1: Running
```

---

### Step 7: Reboot to Test Auto-Start

```bash
sudo reboot
```

**After reboot:**
Services should start automatically within 10-15 seconds.

Check with:

```bash
ssh pi@raspberrypi.local
cd ~/mariner/pi_scripts
./rov_services.sh status
```

---

## 🎮 Using the Windows Application

After auto-start setup on Pi:

1. **Connect Nintendo Switch Pro Controller** to Windows PC (USB or Bluetooth)

2. **Launch Application:**

   ```powershell
   cd "e:\UIU MARINER\mariner-software-1.0"
   python launch_mariner.py
   ```

3. **Everything connects automatically:**

   - ✅ Pixhawk via MAVLink (tcp:raspberrypi.local:7000)
   - ✅ BMP388 Sensor (raspberrypi.local:5000)
   - ✅ Camera 0 Stream (UDP port 5000)
   - ✅ Camera 1 Stream (UDP port 5001)
   - ✅ Nintendo Switch Pro Controller (auto-detected)

4. **Test Thrusters:**
   - Move controller joysticks
   - Watch terminal for `[THRUSTER]` logs showing PWM values
   - Example: `[THRUSTER] Forward/Back: 0.75 → Ch1(Pin1)=1675, Ch8(Pin8)=1325`

---

## 🛠️ Service Management Commands

All commands run on Raspberry Pi:

### Start/Stop Services:

```bash
./rov_services.sh start    # Start all services
./rov_services.sh stop     # Stop all services
./rov_services.sh restart  # Restart all services
```

### Check Status:

```bash
./rov_services.sh status   # Quick status check
```

### View Logs:

```bash
./rov_services.sh logs rov-sensors   # Sensor logs
./rov_services.sh logs rov-mavproxy  # MAVProxy logs
./rov_services.sh logs rov-camera0   # Camera 0 logs
./rov_services.sh logs rov-camera1   # Camera 1 logs
```

### Enable/Disable Auto-Start:

```bash
./rov_services.sh enable   # Enable auto-start on boot
./rov_services.sh disable  # Disable auto-start
```

---

## 🔄 Updating Ground Station IP

If your Windows PC IP address changes:

```bash
ssh pi@raspberrypi.local
cd ~/mariner/pi_scripts
sudo ./update_ground_station_ip.sh
```

**When prompted:**

- Current IP will be shown
- Enter new IP address
- Camera services will restart automatically

---

## 🐛 Troubleshooting

### Services Not Starting:

```bash
# Check individual service logs
sudo journalctl -u rov-sensors -n 50
sudo journalctl -u rov-mavproxy -n 50
sudo journalctl -u rov-camera0 -n 50
sudo journalctl -u rov-camera1 -n 50
```

### Restart Individual Service:

```bash
sudo systemctl restart rov-sensors
sudo systemctl restart rov-mavproxy
sudo systemctl restart rov-camera0
sudo systemctl restart rov-camera1
```

### Check Service Status:

```bash
systemctl status rov-sensors
systemctl status rov-mavproxy
systemctl status rov-camera0
systemctl status rov-camera1
```

### Windows App Shows Connection Errors:

1. **Verify Pi services running:**

   ```bash
   ./rov_services.sh status
   ```

2. **Ping Raspberry Pi from Windows:**

   ```powershell
   ping raspberrypi.local
   ```

3. **Check firewall on Windows:**

   - Allow Python through Windows Firewall
   - Allow UDP ports 5000 and 5001

4. **Verify Ground Station IP:**
   ```bash
   sudo ./update_ground_station_ip.sh
   ```

### Pixhawk Not Detected:

1. **Re-run detection:**

   ```bash
   python3 detect_pixhawk.py
   ```

2. **Check USB connection:**

   ```bash
   ls -l /dev/ttyUSB* /dev/ttyACM*
   ```

3. **Edit MAVProxy service manually:**
   ```bash
   sudo nano /etc/systemd/system/rov-mavproxy.service
   # Update ExecStart line with correct port/baud
   sudo systemctl daemon-reload
   sudo systemctl restart rov-mavproxy
   ```

### Cameras Not Streaming:

1. **Re-run camera detection:**

   ```bash
   ./detect_cameras.sh
   ```

2. **Test camera manually:**

   ```bash
   # Pi Camera
   libcamera-hello --list-cameras

   # USB Camera
   python3 usb_camera_server.py /dev/video0 YOUR_PC_IP 5000
   ```

3. **Edit camera service manually:**
   ```bash
   sudo nano /etc/systemd/system/rov-camera0.service
   # Update ExecStart line with correct device
   sudo systemctl daemon-reload
   sudo systemctl restart rov-camera0
   ```

---

## 📁 Service File Locations

All service files stored in: `/etc/systemd/system/`

- `rov-sensors.service` - BMP388 sensor server
- `rov-mavproxy.service` - Pixhawk MAVProxy
- `rov-camera0.service` - Camera 0 stream
- `rov-camera1.service` - Camera 1 stream

**View service file:**

```bash
cat /etc/systemd/system/rov-sensors.service
```

**Edit service file:**

```bash
sudo nano /etc/systemd/system/rov-sensors.service
sudo systemctl daemon-reload
sudo systemctl restart rov-sensors
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Raspberry Pi boots and services start automatically
- [ ] `./rov_services.sh status` shows all services running
- [ ] Windows app launches without errors
- [ ] Camera feeds display in UI
- [ ] Sensor data updates (depth, temperature)
- [ ] MAVLink status shows "Connected"
- [ ] Controller joystick movements show thruster logs
- [ ] Thruster PWM values between 1100-1900

---

## 🎉 Success!

You're all set! Now just:

1. **Power on Raspberry Pi** → Services auto-start
2. **Open Windows app** → Everything connects
3. **Start piloting** → No manual setup needed

---

## 📞 Support

If issues persist:

1. Check logs: `./rov_services.sh logs [service-name]`
2. Review hardware connections
3. Verify network connectivity
4. Check service configurations in `/etc/systemd/system/`

**Enjoy your seamless ROV experience! 🚀🌊**
