# 🔌 HARDWARE CONNECTION GUIDE

## ✅ Current Status (From Last Run)

### Working ✅

- **GUI:** Fully responsive and functional
- **Joystick:** ✅ Nintendo Switch Pro Controller detected
- **Sensor Data:** ✅ Mock mode active (auto-fallback working)
- **Camera Placeholders:** ✅ Showing "Camera Unavailable"

### Not Connected (Hardware Missing) ⚠️

- **Raspberry Pi:** No connection (target refused)
- **Pixhawk:** No connection (expected without Pi bridge)
- **Camera Streams:** No streams (Pi cameras not broadcasting)
- **Real Sensors:** No connection (Pi sensor server not running)

---

## 📋 Connection Checklist

### Step 1: Verify Network Setup

#### Check if Raspberry Pi is powered on

```powershell
# Test Pi connectivity
ping raspberrypi.local

# Or try direct IP if you know it
ping 192.168.0.100
```

**Expected:**

- ✅ Reply from raspberrypi.local
- ❌ "Request timed out" → Pi is off or not on network

#### Check your Windows firewall

```powershell
# Allow UDP ports for camera streams
New-NetFirewallRule -DisplayName "ROV Camera Port 5000" -Direction Inbound -LocalPort 5000 -Protocol UDP -Action Allow
New-NetFirewallRule -DisplayName "ROV Camera Port 5001" -Direction Inbound -LocalPort 5001 -Protocol UDP -Action Allow

# Allow TCP ports for sensors and Pixhawk
New-NetFirewallRule -DisplayName "ROV Sensors Port 5002" -Direction Inbound -LocalPort 5002 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "ROV MAVLink Port 7000" -Direction Inbound -LocalPort 7000 -Protocol TCP -Action Allow
```

### Step 2: Start Raspberry Pi Services

#### Option A: Using PowerShell Script (Automated)

```powershell
# From Windows
.\start_pi_services.ps1
```

#### Option B: Manual SSH Connection

```powershell
# SSH to Pi
ssh pi@raspberrypi.local

# Once logged in:
cd ~/pi_scripts

# Start sensor server
python3 sensorServer.py &

# Start camera streams (both)
./cam0.sh &
./cam1.sh &

# Start MAVProxy (Pixhawk bridge)
mavproxy.py --master=/dev/ttyACM0 --out=tcpin:0.0.0.0:7000 &

# Check what's running
ps aux | grep -E "sensor|camera|mavproxy"

# Exit SSH
exit
```

### Step 3: Verify Services Running on Pi

```powershell
# Test sensor server (TCP port 5002)
Test-NetConnection -ComputerName raspberrypi.local -Port 5002

# Test MAVLink server (TCP port 7000)
Test-NetConnection -Computerpi.local -Port 7000
```

**Expected Output:**

```
TcpTestSucceeded : True  ← Good! Service is listening
```

### Step 4: Test Camera Streams

```powershell
# Check if Pi is sending UDP streams
# You can use VLC to test:
# 1. Open VLC
# 2. Media → Open Network Stream
# 3. Enter: udp://@:5000
# 4. Should see video feed if working
```

### Step 5: Launch Mariner

```powershell
cd "F:\Web Development\uiu-mariner\uiu-mariner-1"
.\.venv\Scripts\Activate.ps1
python launch_mariner.py
```

---

## 🔧 Troubleshooting Common Issues

### Issue 1: "Target machine actively refused connection"

**Symptoms:**

```
[WinError 10061] No connection could be made because the target machine actively refused it
```

**Causes:**

1. Service not running on Pi
2. Firewall blocking connection
3. Wrong port number
4. Pi not on network

**Solutions:**

```powershell
# 1. Check if Pi is reachable
ping raspberrypi.local

# 2. Check if service is listening
Test-NetConnection -ComputerName raspberrypi.local -Port 5002

# 3. SSH to Pi and check services
ssh pi@raspberrypi.local "ps aux | grep sensor"

# 4. Restart services on Pi
.\start_pi_services.ps1
```

### Issue 2: Camera Streams Not Appearing

**Symptoms:**

```
[CAM0] ❌ Failed to open: udpsrc port=5000 ...
```

**Causes:**

1. GStreamer not installed/configured on Windows
2. Pi camera streams not started
3. Firewall blocking UDP ports
4. Network issue

**Solutions:**

#### A. Install GStreamer on Windows

1. Download: https://gstreamer.freedesktop.org/download/
2. Install "Complete" version (not Runtime-only)
3. Add to PATH:
   ```powershell
   $env:PATH += ";C:\gstreamer\1.0\msvc_x86_64\bin"
   ```
4. Verify:
   ```powershell
   gst-launch-1.0 --version
   ```

#### B. Check Pi Camera Services

```bash
# SSH to Pi
ssh pi@raspberrypi.local

# Check if camera scripts exist
ls ~/pi_scripts/cam*.sh

# Test camera manually
libcamera-vid -t 0 --width 640 --height 480 --framerate 30

# Start camera stream
./pi_scripts/cam0.sh
```

#### C. Test UDP Reception

```powershell
# Use gst-launch to test direct stream
gst-launch-1.0 udpsrc port=5000 ! fakesink

# Should show data if Pi is streaming
# Ctrl+C to stop
```

### Issue 3: Pixhawk Not Connecting

**Symptoms:**

```
[PIXHAWK] ❌ Connection failed
[❌] Connection failed: [WinError 10061] No connection could be made
```

**Causes:**

1. Pixhawk not connected to Pi
2. MAVProxy not running on Pi
3. Wrong connection string

**Solutions:**

#### A. Check Pixhawk-to-Pi USB Connection

```bash
# SSH to Pi
ssh pi@raspberrypi.local

# Check USB devices
ls /dev/tty*
# Look for: /dev/ttyACM0 or /dev/ttyUSB0

# Check if Pixhawk detected
dmesg | grep -i tty
```

#### B. Start MAVProxy on Pi

```bash
# Kill any existing MAVProxy
pkill -9 mavproxy

# Start new instance
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --out=tcpin:0.0.0.0:7000
```

#### C. Test MAVLink Connection

```powershell
# From Windows
Test-NetConnection -ComputerName raspberrypi.local -Port 7000

# Or use MAVProxy to test
mavproxy.py --master=tcp:raspberrypi.local:7000
```

### Issue 4: Joystick Not Detected

**Symptoms:**

```
❌ No joystick detected
```

**Solutions:**

1. Ensure controller is connected via USB or Bluetooth
2. Test controller in Windows:
   - Run `joy.cpl` to open Game Controllers
   - Verify controller appears and responds
3. Restart application after connecting controller

---

## 🎯 Quick Connection Sequence

### For Full System Connection:

```powershell
# 1. Power on Raspberry Pi (wait 30 seconds for boot)

# 2. Test Pi connection
ping raspberrypi.local

# 3. Start Pi services (automated)
.\start_pi_services.ps1

# 4. Verify services running
Test-NetConnection -ComputerName raspberrypi.local -Port 5002
Test-NetConnection -ComputerName raspberrypi.local -Port 7000

# 5. Connect joystick/controller

# 6. Launch Mariner
.\.venv\Scripts\Activate.ps1
python launch_mariner.py
```

### Expected Results:

```
[PIXHAWK] ✅ Connected
[JOYSTICK] ✅ Connected: Nintendo Switch Pro Controller
[SENSORS] ✅ Connected (Real data from Pi)
[CAMERAS] ✅ Live streams active
```

---

## 📊 Connection Status Table

| Component    | Status          | Port | Protocol | Fix If Failing         |
| ------------ | --------------- | ---- | -------- | ---------------------- |
| **Sensors**  | 🟢 Mock Mode    | 5002 | TCP      | Start Pi sensor server |
| **Camera 0** | ⚠️ Placeholder  | 5000 | UDP      | Start Pi camera stream |
| **Camera 1** | ⚠️ Placeholder  | 5001 | UDP      | Start Pi camera stream |
| **Pixhawk**  | 🔴 Disconnected | 7000 | TCP      | Start MAVProxy on Pi   |
| **Joystick** | ✅ Connected    | -    | USB      | Already working!       |

---

## 🔄 Restart All Services Script

Create this file: `restart_all.ps1`

```powershell
# Stop all services on Pi
ssh pi@raspberrypi.local "pkill -9 python3; pkill -9 mavproxy; pkill -9 libcamera"

# Wait a moment
Start-Sleep -Seconds 2

# Start all services
.\start_pi_services.ps1

# Wait for services to start
Start-Sleep -Seconds 5

# Test connections
Write-Host "Testing connections..." -ForegroundColor Yellow
Test-NetConnection -ComputerName raspberrypi.local -Port 5002
Test-NetConnection -ComputerName raspberrypi.local -Port 7000

# Launch Mariner
Write-Host "Launching Mariner..." -ForegroundColor Green
python launch_mariner.py
```

---

## 💡 Pro Tips

1. **Start with Mock Mode**

   - Test GUI and controls without hardware
   - Verify joystick works
   - Check all UI elements

2. **Connect Hardware Gradually**

   - First: Sensors (TCP 5002)
   - Second: Pixhawk (TCP 7000)
   - Last: Cameras (UDP 5000/5001)

3. **Use Auto-Fallback**

   - App automatically switches to mock if sensors fail
   - Can operate without all hardware
   - Graceful degradation

4. **Monitor Console Output**

   - Watch for connection attempts
   - Check for error messages
   - Verify auto-fallback activates

5. **Test Network First**
   - Always ping Pi before launching
   - Verify firewall rules
   - Check service ports with Test-NetConnection

---

## 📞 Quick Reference Commands

### Windows Side

```powershell
# Test Pi
ping raspberrypi.local

# Test TCP ports
Test-NetConnection -ComputerName raspberrypi.local -Port 5002  # Sensors
Test-NetConnection -ComputerName raspberrypi.local -Port 7000  # Pixhawk

# Launch app
python launch_mariner.py
```

### Raspberry Pi Side

```bash
# Check services
ps aux | grep -E "sensor|camera|mavproxy"

# Start sensor server
python3 ~/pi_scripts/sensorServer.py &

# Start cameras
~/pi_scripts/cam0.sh &
~/pi_scripts/cam1.sh &

# Start MAVProxy
mavproxy.py --master=/dev/ttyACM0 --out=tcpin:0.0.0.0:7000 &

# Check ports
netstat -tuln | grep -E "5000|5001|5002|7000"
```

---

**Status:** ✅ GUI RESPONSIVE - Ready to connect hardware
**Next:** Follow steps above to connect real hardware
**Alternative:** Continue testing in mock mode (already working!)
