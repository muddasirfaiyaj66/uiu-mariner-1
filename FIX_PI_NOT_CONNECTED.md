# 🚨 PI NOT CONNECTED - FIX GUIDE

## Current Problem

Your Windows PC can't connect to the Raspberry Pi services. The error shows:

- ❌ Port 5000 (Sensors) - Connection refused
- ❌ Port 7000 (Pixhawk/MAVProxy) - Connection refused
- ❌ Port 5000/5001 (Cameras) - No streams

**This means: The services are NOT running on the Raspberry Pi**

---

## ✅ QUICK FIX (Do This Now)

### Step 1: Run Diagnostics

```powershell
.\diagnose_pi_connection.ps1
```

This will tell you:

- ✅ If Pi is on the network
- ✅ Your PC's IP address
- ❌ Which services are missing

### Step 2: Connect to Pi

**Option A - Using PowerShell script:**

```powershell
.\ssh_pi.ps1
```

**Option B - Direct SSH:**

```powershell
ssh pi@raspberrypi.local
```

Default password: `raspberry`

### Step 3: Start Services on Pi

Once connected to the Pi, run **ONE** of these:

#### 🚀 Quick Start (Recommended)

```bash
cd ~/mariner/pi_scripts
./start_all_services.sh 192.168.X.X
```

Replace `192.168.X.X` with your Windows PC IP from diagnostics

#### 🎯 Auto-Detect Method

```bash
cd ~/mariner/pi_scripts
./START_NOW.sh
```

#### 📋 View Running Services

```bash
screen -ls
```

You should see:

- `sensors` - BMP388 pressure sensor
- `mavproxy` - Pixhawk connection
- `cam0` - Camera stream 0
- `cam1` - Camera stream 1

---

## 🔍 Troubleshooting

### Can't Find Pi on Network?

**Check 1: Is Pi powered on and connected?**

```powershell
ping raspberrypi.local
```

If ping fails:

- Check Pi is powered on (green LED)
- Check Ethernet cable or WiFi connection
- On Windows, install Bonjour Print Services (for .local names)

**Check 2: Find Pi's actual IP**

```powershell
# Scan your network
arp -a | findstr "b8-27-eb"  # Pi 3/Zero
arp -a | findstr "dc-a6-32"  # Pi 4
```

### Pixhawk Not Detected on Pi?

**Check Pixhawk Connection:**

```bash
# On Pi - check USB devices
ls /dev/ttyACM*
# Should show: /dev/ttyACM0

# Or run detection script
python3 ~/mariner/pi_scripts/detect_pixhawk.py
```

If not found:

- Check USB cable from Pixhawk to Pi
- Try different USB port on Pi
- Check Pixhawk is powered (LED lights)
- Try rebooting Pixhawk (disconnect/reconnect)

### Services Keep Stopping?

**View service logs:**

```bash
# On Pi - attach to service screens
screen -r sensors    # View sensor logs
screen -r mavproxy   # View MAVProxy logs
screen -r cam0       # View camera 0 logs
screen -r cam1       # View camera 1 logs

# Detach: Press Ctrl+A then D
```

**Stop and restart:**

```bash
# Stop all
./stop_all_services.sh

# Start all
./start_all_services.sh YOUR_PC_IP
```

### Wrong PC IP Address?

**Update ground station IP:**

```bash
# On Pi
./update_ground_station_ip.sh NEW_IP_ADDRESS
```

---

## 🎯 Complete Workflow

### First Time Setup:

1. ✅ Run diagnostics on Windows: `.\diagnose_pi_connection.ps1`
2. ✅ SSH to Pi: `ssh pi@raspberrypi.local`
3. ✅ Run setup: `cd ~/mariner/pi_scripts && ./SETUP_AND_START.sh`
4. ✅ Choose auto-start option for future

### Daily Use:

1. ✅ Power on Pi
2. ⏱️ Wait 30-60 seconds for boot
3. ✅ Run diagnostics: `.\diagnose_pi_connection.ps1`
4. ✅ Start Windows app: `python launch_mariner.py`

### If Services Not Running:

1. ✅ SSH to Pi
2. ✅ Run: `./start_all_services.sh YOUR_PC_IP`
3. ✅ Verify: `screen -ls`
4. ✅ Try Windows app again

---

## 📊 Port Reference

| Port | Service  | Description                      |
| ---- | -------- | -------------------------------- |
| 5000 | Sensors  | BMP388 depth/pressure data (TCP) |
| 7000 | MAVProxy | Pixhawk telemetry/control (TCP)  |
| 5000 | Camera 0 | Front camera stream (UDP)        |
| 5001 | Camera 1 | Bottom camera stream (UDP)       |

---

## 🆘 Still Not Working?

### Check This Checklist:

- [ ] Pi is powered on and network connected
- [ ] Can ping `raspberrypi.local` from Windows
- [ ] Diagnostics script shows Pi IP address
- [ ] SSH connection works
- [ ] Services running on Pi (`screen -ls` shows all 4)
- [ ] Pixhawk connected to Pi via USB
- [ ] `/dev/ttyACM0` exists on Pi
- [ ] Correct Windows PC IP used in Pi startup

### Manual Service Check:

```bash
# On Pi - check if services are listening
sudo netstat -tulpn | grep -E "5000|7000|5001"
```

Should show:

```
tcp    0.0.0.0:5000    LISTEN    python3
tcp    0.0.0.0:7000    LISTEN    python3
```

### Need Help?

1. Post diagnostics output: `.\diagnose_pi_connection.ps1`
2. Post Pi screen list: SSH to Pi, run `screen -ls`
3. Post service logs: `screen -r mavproxy` (Ctrl+A then D to detach)

---

## 🎓 Understanding the System

```
┌─────────────────┐         Network          ┌─────────────────┐
│  Windows PC     │◄─────────────────────────►│  Raspberry Pi   │
│                 │                            │                 │
│  Mariner App    │                            │  Pi Services:   │
│  - Controller   │  TCP 7000 (MAVLink)       │  - MAVProxy     │
│  - UI Display   │◄──────────────────────────┤  - Sensors      │
│  - Video decode │  TCP 5000 (Sensors)       │  - Cameras      │
│                 │◄──────────────────────────┤                 │
│                 │  UDP 5000/5001 (Video)    │                 │
│                 │◄──────────────────────────┤                 │
└─────────────────┘                            └────────┬────────┘
                                                       │ USB
                                                       ▼
                                               ┌─────────────────┐
                                               │    Pixhawk      │
                                               │   (Autopilot)   │
                                               │                 │
                                               │  - Motors       │
                                               │  - ESCs         │
                                               │  - Sensors      │
                                               └─────────────────┘
```

**Key Points:**

1. **Pi is the bridge** between Windows and Pixhawk
2. **Services must run on Pi** before Windows can connect
3. **Check Pi first** when connection fails
4. **USB connection** is Pi-to-Pixhawk (not Windows-to-Pixhawk)

---

## 📝 Quick Command Reference

### Windows Commands:

```powershell
# Diagnose connection
.\diagnose_pi_connection.ps1

# Connect to Pi
.\ssh_pi.ps1

# Start main app
python launch_mariner.py
```

### Pi Commands:

```bash
# Start all services
cd ~/mariner/pi_scripts
./start_all_services.sh YOUR_PC_IP

# View running services
screen -ls

# View specific log
screen -r mavproxy  # (Ctrl+A then D to exit)

# Stop all services
./stop_all_services.sh

# Check Pixhawk
python3 detect_pixhawk.py
ls /dev/ttyACM*

# Check cameras
./detect_cameras.sh
```

---

**Remember: Pi services MUST be running before starting Windows app!**
