# 🌐 Network Auto-Configuration Guide

## Overview

Your UIU MARINER system now has **DYNAMIC IP AUTO-DETECTION**. No more hardcoded IPs! The system automatically discovers devices when connected via Ethernet cable.

---

## ✅ What Changed

### 🔧 **All Hardcoded IPs Removed**

- ❌ No more `192.168.21.126`
- ❌ No more `192.168.0.104`
- ✅ Dynamic mDNS: `raspberrypi.local`
- ✅ Auto-detection on both Pi and Ground Station

### 🎯 **8-Thruster Configuration Confirmed**

- ✅ All 8 thrusters are properly configured
- ✅ Channels 1-8 mapped correctly
- ✅ Forward/Backward: Channels 1, 8
- ✅ Yaw (rotation): Channels 2, 5
- ✅ Vertical (up/down): Channels 3, 4, 6, 7

### 📡 **Auto-Discovery Features**

1. **Pi → Ground Station Detection**

   - Checks SSH client IP
   - Uses default gateway
   - Scans ARP cache
   - Performs network scan if needed

2. **Ground Station → Pi Detection**
   - Uses mDNS: `raspberrypi.local`
   - Falls back to network scan
   - Auto-connects when found

---

## 🚀 How to Use

### **On Raspberry Pi**

#### Method 1: Auto-detect (Recommended)

```bash
ssh pi@raspberrypi.local
cd /home/pi/mariner/pi_scripts
./START_NOW.sh
```

The script will **automatically find your Ground Station IP**!

#### Method 2: Manual IP (if needed)

```bash
./START_NOW.sh 192.168.X.X
```

### **On Ground Station (Windows PC)**

#### Launch the ROV Control Software

```powershell
cd "E:\UIU MARINER\mariner-software-1.0"
python launch_mariner.py
```

The software will **automatically find raspberrypi.local**!

---

## 🔍 How Auto-Detection Works

### **Pi Side (Finding Ground Station)**

The Pi uses multiple methods in priority order:

1. **SSH Client IP** (if you're SSH'd in from Ground Station)

   ```bash
   # Automatically detects the IP you're connecting FROM
   ```

2. **Default Gateway**

   ```bash
   ip route show default
   # Usually your PC's IP on direct Ethernet
   ```

3. **ARP Cache**

   ```bash
   ip neigh show dev eth0
   # Recent network communications
   ```

4. **Network Scan**
   ```bash
   # Pings all IPs in the subnet
   # Finds first responding device
   ```

### **Ground Station Side (Finding Pi)**

1. **mDNS Resolution**

   - Uses `raspberrypi.local` hostname
   - Works via Bonjour/Avahi
   - No IP address needed!

2. **Fallback IP**
   - If mDNS fails, uses fallback
   - Can be configured in `config.json`

---

## ⚙️ Configuration

### **config.json** (Ground Station)

```json
{
  "mavlink_connection": "tcp:raspberrypi.local:7000",
  "sensors": {
    "host": "raspberrypi.local",
    "port": 5000,
    "protocol": "tcp",
    "auto_connect": true
  },
  "network": {
    "auto_detect": true,
    "pi_hostname": "raspberrypi.local",
    "fallback_ip": "192.168.0.100"
  },
  "thrusters": {
    "total_count": 8
  }
}
```

### **Key Settings**

| Setting                 | Description                   | Default             |
| ----------------------- | ----------------------------- | ------------------- |
| `network.auto_detect`   | Enable auto-discovery         | `true`              |
| `network.pi_hostname`   | Pi mDNS hostname              | `raspberrypi.local` |
| `network.fallback_ip`   | Fallback if auto-detect fails | `192.168.0.100`     |
| `sensors.auto_connect`  | Auto-reconnect sensors        | `true`              |
| `thrusters.total_count` | Number of thrusters           | `8`                 |

---

## 🔧 Troubleshooting

### **Problem: Pi can't find Ground Station**

**Solutions:**

1. Specify IP manually:

   ```bash
   ./START_NOW.sh 192.168.X.X
   ```

2. Check Ethernet connection:

   ```bash
   ip addr show eth0
   # Should show IP like 192.168.X.X
   ```

3. Find your PC's IP:
   ```powershell
   # On Windows
   ipconfig
   # Look for "Ethernet adapter" → "IPv4 Address"
   ```

### **Problem: Ground Station can't find Pi**

**Solutions:**

1. Check if `raspberrypi.local` resolves:

   ```powershell
   ping raspberrypi.local
   ```

2. If ping fails, find Pi's IP:

   ```bash
   # On Pi
   hostname -I
   ```

3. Manually set Pi IP in `config.json`:
   ```json
   {
     "sensors": {
       "host": "192.168.X.X" // Use Pi's actual IP
     }
   }
   ```

### **Problem: Only 4 thrusters working**

**Fix:** All 8 channels are already configured! Check:

1. **Pixhawk Configuration**

   - Ensure all 8 ESCs are connected
   - Verify SERVO1-SERVO8 outputs are enabled
   - Check ArduSub frame type matches your ROV

2. **Physical Connections**

   ```
   Pixhawk MAIN OUT:
   1 → ESC 1 (Forward Left)
   2 → ESC 2 (Yaw Left)
   3 → ESC 3 (Vertical Front Left)
   4 → ESC 4 (Vertical Front Right)
   5 → ESC 5 (Yaw Right)
   6 → ESC 6 (Vertical Rear Left)
   7 → ESC 7 (Vertical Rear Right)
   8 → ESC 8 (Forward Right)
   ```

3. **Test Each Thruster**
   - Arm the ROV
   - Move joystick in each direction
   - All 8 should respond

---

## 📊 Network Status Display

The UI shows real-time network status:

```
● Network: raspberrypi.local (Connected)   ← Green when connected
● Network: Disconnected                     ← Red when disconnected
```

Bottom bar also displays:

```
UIU MARINER v1.0 | ArduSub Compatible | 8-Thruster ROV
```

---

## 🎮 Thruster Control Mapping

**All 8 thrusters are actively controlled:**

### Left Stick (Movement)

- **Y-axis**: Forward/Backward
  - Forward: Ch1 (1000μs), Ch8 (2000μs)
  - Backward: Ch1 (2000μs), Ch8 (1000μs)
- **X-axis**: Yaw (Rotation)
  - Right: Ch2 (2000μs), Ch5 (1000μs)
  - Left: Ch2 (1000μs), Ch5 (2000μs)

### Right Stick (Vertical)

- **Y-axis**: Up/Down
  - Up: Ch3 (1000μs), Ch4 (1000μs), Ch6 (2000μs), Ch7 (2000μs)
  - Down: Ch3 (2000μs), Ch4 (2000μs), Ch6 (1000μs), Ch7 (1000μs)

All values are **1500μs** (neutral) when stick is centered.

---

## 🔬 Testing Auto-Detection

### **Test 1: Check Auto-Detection Script**

```bash
# On Pi
python3 /home/pi/mariner/pi_scripts/get_ground_station_ip.py
```

Expected output:

```
===========================================================
AUTO-DETECTING GROUND STATION IP
===========================================================
[NETWORK] SSH client IP: 192.168.X.X
✅ Ground Station IP: 192.168.X.X (from SSH)
192.168.X.X
```

### **Test 2: Verify Services Start**

```bash
./START_NOW.sh
```

Expected output:

```
🚀 STARTING ALL ROV SERVICES...
📡 Auto-detecting Ground Station IP...
✅ Detected Ground Station: 192.168.X.X
...
✅ Sensor Server:  RUNNING (PID: XXXX)
✅ MAVProxy:       RUNNING (PID: XXXX)
✅ Camera 0:       RUNNING (PID: XXXX)
✅ Camera 1:       RUNNING (PID: XXXX)
```

### **Test 3: Check Sensor Connection**

```bash
# On Ground Station
telnet raspberrypi.local 5000
```

Should receive sensor data:

```
25.3,101325.0,0.0
25.4,101326.0,0.0
```

---

## 📝 Summary

✅ **No more hardcoded IPs** - fully dynamic
✅ **Auto-detection on both sides** - plug and play
✅ **8 thrusters fully configured** - all channels working
✅ **Real-time network status** - see connection in UI
✅ **Fallback mechanisms** - works even if auto-detect fails

**Just connect the Ethernet cable and start the services!** 🚀
