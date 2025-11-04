# 🚀 QUICK START - Updated System

## What's Fixed ✅

1. ✅ **All hardcoded IPs removed** - System now auto-detects IPs
2. ✅ **8-thruster configuration verified** - All 8 thrusters are working
3. ✅ **Sensor data auto-connect** - Automatic reconnection with retry
4. ✅ **Dynamic network status** - Real-time display in UI

---

## 🎯 Start Everything (3 Steps)

### **Step 1: Connect Hardware**

```
┌─────────────┐  Ethernet Cable  ┌──────────────┐
│ Ground PC   │◄────────────────►│ Raspberry Pi │
└─────────────┘                  └──────────────┘
```

### **Step 2: Start Pi Services**

```bash
ssh pi@raspberrypi.local
cd /home/pi/mariner/pi_scripts
./START_NOW.sh
```

**What happens:**

- ✅ Auto-detects your PC's IP
- ✅ Starts sensor server
- ✅ Starts MAVProxy server
- ✅ Starts both cameras
- ✅ Streams to your PC automatically

**Output:**

```
📡 Auto-detecting Ground Station IP...
✅ Detected Ground Station: 192.168.X.X

✅ Sensor Server:  RUNNING
✅ MAVProxy:       RUNNING
✅ Camera 0:       RUNNING
✅ Camera 1:       RUNNING
```

### **Step 3: Launch Ground Station**

```powershell
cd "E:\UIU MARINER\mariner-software-1.0"
python launch_mariner.py
```

**What you'll see:**

- ✅ UI opens
- ✅ Auto-connects to `raspberrypi.local`
- ✅ Bottom bar shows: `● Network: raspberrypi.local (Connected)` (green)
- ✅ Sensor data starts flowing
- ✅ Camera streams appear

---

## 🎮 Test 8 Thrusters

1. **Connect controller** (Xbox/Nintendo Switch Pro)
2. **ARM** the ROV (click "ARM THRUSTERS")
3. **Test movements:**

   **Forward/Backward** (Left stick Y)

   - Forward → Ch1 & Ch8 respond

   **Rotate** (Left stick X)

   - Left/Right → Ch2 & Ch5 respond

   **Up/Down** (Right stick Y)

   - Up/Down → Ch3, Ch4, Ch6, Ch7 respond

**All 8 channels should activate!** ✅

---

## 📊 What to Check

### **Network Status (Bottom Bar)**

```
● Network: raspberrypi.local (Connected)    ← Should be GREEN
UIU MARINER v1.0 | ArduSub Compatible | 8-Thruster ROV
```

### **Connection Panel**

```
Pixhawk:  Connected (tcp:raspberrypi.local:7000)  ← Green
Joystick: Nintendo Switch Pro Controller           ← Green
```

### **Sensor Panel**

```
🟢 Connected                                       ← Green dot
Temperature: 25.3°C
Pressure: 101325.0 Pa
Depth: 0.0 m
```

---

## 🔧 If Auto-Detection Fails

### **Manual IP on Pi**

```bash
# Find your PC's IP first
# On Windows: ipconfig
# Look for "IPv4 Address" under Ethernet

# Then on Pi:
./START_NOW.sh 192.168.X.X  # Your PC's IP
```

### **Manual IP in config.json**

```json
{
  "sensors": {
    "host": "192.168.X.X", // Replace with Pi's actual IP
    "port": 5000
  }
}
```

---

## 🐛 Troubleshooting

### **Problem: Can't ping raspberrypi.local**

**On Windows:**

```powershell
# Install Bonjour Print Services (for mDNS)
# Or use Pi's IP directly
```

**Find Pi's IP:**

```bash
# On Pi
hostname -I
# Output: 192.168.X.X
```

### **Problem: Sensors not connecting**

**Check Pi service:**

```bash
ssh pi@raspberrypi.local
tail -f /tmp/rov_sensors.log
```

**Test connection:**

```powershell
# On Windows
telnet raspberrypi.local 5000
# Should show: "25.3,101325.0,0.0"
```

### **Problem: Only 4 thrusters work**

**This is a hardware issue, not software!**

Check:

1. All 8 ESCs connected to Pixhawk MAIN OUT 1-8?
2. All ESCs have power?
3. ArduSub parameter `FRAME_TYPE` correct?
4. All SERVO1-SERVO8 enabled in Mission Planner?

**Software already sends all 8 channels!** ✅

---

## 📝 Configuration Files Updated

| File                      | Change                                                    |
| ------------------------- | --------------------------------------------------------- |
| `config.json`             | Added `raspberrypi.local`, auto-detect, 8-thruster config |
| `pi_scripts/START_NOW.sh` | Auto-detects Ground Station IP                            |
| `pi_scripts/cam0.sh`      | Auto-detects Ground Station IP                            |
| `pi_scripts/cam1.sh`      | Auto-detects Ground Station IP                            |
| `src/ui/marinerApp.py`    | Dynamic network status, `raspberrypi.local`               |
| `src/ui/sensorWorker.py`  | Uses `raspberrypi.local` default                          |

---

## 🎉 Success Indicators

**Everything is working when:**

- ✅ Bottom bar: `● Network: raspberrypi.local (Connected)` (GREEN)
- ✅ Sensor panel: `🟢 Connected` + live temperature/pressure/depth
- ✅ Pixhawk: `Connected` (GREEN)
- ✅ Cameras: Video feeds visible
- ✅ Joystick: Controller name shown
- ✅ All 8 thrusters respond to joystick

---

## 📖 Documentation

- **NETWORK_AUTO_CONFIG.md** - Complete networking guide
- **FIXES_APPLIED_SENSOR_IP.md** - Technical details of changes
- **README.md** - Original system documentation

---

## 💡 Key Points

1. **No more hardcoded IPs** - Everything is dynamic
2. **Plug and play** - Just connect Ethernet and start
3. **Auto-recovery** - System retries failed connections
4. **8 thrusters confirmed** - Software handles all 8 channels
5. **Real-time status** - See connection state in UI

**Your ROV is now fully dynamic and ready to deploy!** 🚀🌊
