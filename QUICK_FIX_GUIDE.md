# 🚀 Quick Fix - Start ROV System

## ❌ Current Problem

You're running from **Windows**, but trying to connect to `/dev/ttyACM0` which is a **Linux device path**.

The config was set for direct serial connection (Pi → Pixhawk), but you're controlling from Windows!

## ✅ Solution

**Fixed:** Changed config back to TCP connection through Raspberry Pi

```json
"mavlink_connection": "tcp:raspberrypi.local:7000"
```

---

## 🔧 What You Need to Do

### On Raspberry Pi (SSH required):

```bash
# 1. SSH into Pi
ssh pi@raspberrypi.local

# 2. Go to mariner directory
cd /home/pi/mariner

# 3. Run the startup script
./START_NOW.sh 192.168.0.100
# Replace 192.168.0.100 with your Windows PC IP
```

**Or run services individually:**

```bash
# Start MAVProxy (Pixhawk bridge)
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --out=tcpin:0.0.0.0:7000 &

# Start Camera 0
libcamera-vid --camera 0 -t 0 --inline -n --width 640 --height 480 --framerate 30 --codec h264 --libav-format h264 -o - | gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.0.100 port=5000 &

# Start Sensor Server (if exists)
python3 /home/pi/mariner/pi_sensor_server.py &
```

---

## 🎯 What Each Service Does

| Service      | Purpose                              | Port | Protocol |
| ------------ | ------------------------------------ | ---- | -------- |
| **MAVProxy** | Bridges Pixhawk USB → Network        | 7000 | TCP      |
| **Camera 0** | Streams video from Pi Camera         | 5000 | UDP      |
| **Camera 1** | Streams second camera (if available) | 5001 | UDP      |
| **Sensors**  | Sends depth/temp/pressure data       | 5000 | TCP      |

---

## 📋 Quick Checklist

### On Raspberry Pi:

- [ ] Pixhawk USB cable connected
- [ ] Check `/dev/ttyACM0` exists: `ls -l /dev/ttyACM0`
- [ ] Camera(s) connected
- [ ] MAVProxy running: `ps aux | grep mavproxy`
- [ ] Cameras streaming: `ps aux | grep libcamera`
- [ ] Sensors running: `ps aux | grep sensor`

### On Windows:

- [ ] Config set to `tcp:raspberrypi.local:7000`
- [ ] Can ping Pi: `ping raspberrypi.local`
- [ ] Launch app: `python launch_mariner.py`

---

## 🐛 Troubleshooting

### Problem: "No such file or directory: /dev/ttyACM0"

**Check Pixhawk connection:**

```bash
ls -l /dev/ttyACM* /dev/ttyUSB*
```

If it's `/dev/ttyUSB0` instead, use:

```bash
mavproxy.py --master=/dev/ttyUSB0 --baudrate=115200 --out=tcpin:0.0.0.0:7000
```

---

### Problem: Cameras not streaming

**Check if libcamera works:**

```bash
libcamera-hello --list-cameras
# Should show available cameras
```

**Test camera manually:**

```bash
libcamera-hello --timeout 5000
# Should show camera preview for 5 seconds
```

---

### Problem: "Connection refused" on Windows

**Check MAVProxy is listening:**

```bash
# On Pi
netstat -an | grep 7000
# Should show: tcp 0 0 0.0.0.0:7000 LISTEN
```

**Check firewall on Pi:**

```bash
sudo ufw status
# If active, allow port:
sudo ufw allow 7000/tcp
```

---

## 💡 Understanding the Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Raspberry Pi                        │
│                                                     │
│  Pixhawk USB ──► MAVProxy ──► TCP:7000 ────────┐   │
│  (115200)        (bridge)     (network)        │   │
│                                                 │   │
│  Pi Camera ──► libcamera-vid ──► UDP:5000 ────┼───┼──► Windows PC
│                (H.264)           (stream)       │   │    (MARINER GUI)
│                                                 │   │
│  Sensors ──► pi_sensor_server ──► TCP:5000 ───┘   │
│  (BMP388)    (Python)            (data)            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Key Point:** Windows can't directly access `/dev/ttyACM0` - it needs the Pi to act as a network bridge!

---

## 🚀 Simple Start Command

### On Pi (all-in-one):

```bash
ssh pi@raspberrypi.local
cd /home/pi/mariner
./START_NOW.sh 192.168.0.100
```

### On Windows:

```powershell
python launch_mariner.py
```

**Expected Output:**

```
[CONNECT] Attempting to connect → tcp:raspberrypi.local:7000
[✅] Heartbeat received — Pixhawk Connected!
[CAMERAS] ✅ Dual camera feeds started
[SENSORS] ✅ Connected to sensor server
```

---

## 📝 Summary

1. ✅ **Config fixed** - Now uses TCP connection
2. 🔧 **Run START_NOW.sh on Pi** - Starts all services
3. 🖥️ **Run launch_mariner.py on Windows** - Connects to Pi
4. 🎥 **Use Camera Settings button** - Configure cameras from GUI

---

Need help? Check the log files on Pi:

- `/tmp/mavproxy.log`
- `/tmp/camera0.log`
- `/tmp/sensors.log`
