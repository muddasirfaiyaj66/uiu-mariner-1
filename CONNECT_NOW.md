# 🚀 CONNECT NOW - Your Pixhawk is Ready!

## ✅ Confirmed Hardware Status

```
✅ Pixhawk: Connected to Raspberry Pi
   Port: /dev/ttyACM0
   Baud: 115200
   Status: Heartbeat detected
```

---

## 🔌 Quick Connection Steps

### Option 1: Automated (Recommended) ⚡

```powershell
# Run this ONE command to start everything:
.\start_pi_services_auto.ps1

# This will:
# 1. Detect your PC IP automatically
# 2. SSH to Pi and start all services
# 3. Start sensor server (TCP 5002)
# 4. Start MAVProxy with Pixhawk (/dev/ttyACM0)
# 5. Start camera streams (UDP 5000/5001)
# 6. Verify all connections
# 7. Offer to launch Mariner

# Then press ENTER when prompted to launch Mariner!
```

### Option 2: Manual Steps 📋

#### Step 1: SSH to Raspberry Pi

```powershell
ssh pi@raspberrypi.local
# Password: (your pi password)
```

#### Step 2: On Pi - Start Services

```bash
# Get your PC IP (replace X.X.X.X with your actual IP)
export GS_IP="192.168.1.100"  # Your Ground Station IP

cd ~/pi_scripts

# Start sensor server
python3 sensorServer.py &

# Start MAVProxy with confirmed Pixhawk port
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --out=tcpin:0.0.0.0:7000 &

# Start cameras (if scripts exist)
./cam0.sh &
./cam1.sh &

# Verify services running
ps aux | grep -E "sensor|mavproxy|libcamera"

# Check ports listening
netstat -tuln | grep -E "5002|7000"

# Exit SSH
exit
```

#### Step 3: On Windows - Launch Mariner

```powershell
cd "F:\Web Development\uiu-mariner\uiu-mariner-1"
.\.venv\Scripts\Activate.ps1
python launch_mariner.py
```

---

## 🧪 Verify Connections Before Launch

```powershell
# Test Pi is reachable
ping raspberrypi.local

# Test sensor server
Test-NetConnection -ComputerName raspberrypi.local -Port 5002

# Test MAVProxy
Test-NetConnection -ComputerName raspberrypi.local -Port 7000

# All should show: TcpTestSucceeded : True
```

---

## 📊 Expected Results After Launch

### ✅ What You Should See:

```
[PIXHAWK] ✅ Connected (tcp:raspberrypi.local:7000)
[SENSORS] ✅ Connected (Real data from BMP388)
[JOYSTICK] ✅ Connected: Nintendo Switch Pro Controller
[CAMERAS] ✅ Live streams active
```

### GUI Status Panel:

- **Pixhawk:** 🟢 Connected
- **Sensors:** 🟢 Connected (Real data)
- **Controller:** 🟢 Ready
- **Cameras:** 🟢 Live feeds or ⚠️ Placeholder (if no cameras)

---

## 🔧 Troubleshooting

### Issue: "Connection refused" on port 7000

**Solution:** MAVProxy not started or wrong Pixhawk port

```bash
# On Pi, check Pixhawk connection:
ls -l /dev/ttyACM*
# Should show /dev/ttyACM0

# Restart MAVProxy:
pkill -9 mavproxy
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --out=tcpin:0.0.0.0:7000
```

### Issue: "Connection refused" on port 5002

**Solution:** Sensor server not started

```bash
# On Pi:
pkill -9 python3
cd ~/pi_scripts
python3 sensorServer.py &
```

### Issue: No camera feeds

**Solution:** Camera scripts not running or no cameras connected

```bash
# On Pi, check cameras:
libcamera-hello --list-cameras

# If cameras detected:
cd ~/pi_scripts
./cam0.sh &
./cam1.sh &
```

---

## 🎯 Connection Architecture

```
Ground Station (Windows)
    ↓ WiFi/Ethernet
Raspberry Pi
    ├─ Sensor Server → TCP:5002 (BMP388 data)
    ├─ MAVProxy → TCP:7000 (Pixhawk bridge)
    │   ↓ USB Serial (/dev/ttyACM0 @ 115200)
    ├─ Pixhawk → ArduSub firmware → ESCs → Thrusters
    ├─ Camera 0 → UDP:5000 (Video stream)
    └─ Camera 1 → UDP:5001 (Video stream)
```

---

## 💡 Pro Tips

1. **Use Automated Script** - Fastest and most reliable

   ```powershell
   .\start_pi_services_auto.ps1
   ```

2. **Check Logs on Pi** - If something fails

   ```bash
   tail -f /tmp/sensor.log
   tail -f /tmp/mavproxy.log
   ```

3. **Restart Individual Services** - If one fails

   ```bash
   # Restart MAVProxy only:
   pkill mavproxy
   mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --out=tcpin:0.0.0.0:7000 &
   ```

4. **Monitor Status** - Watch Ground Station console for connection messages

---

## 🚀 Ready to Connect!

### Recommended Flow:

```powershell
# 1. Start Pi services (automated)
.\start_pi_services_auto.ps1

# 2. Press ENTER when prompted

# 3. Application launches automatically!

# 4. Expected result:
#    ✅ All systems connected
#    ✅ Real sensor data flowing
#    ✅ Pixhawk ready for control
#    ✅ Joystick operational
```

---

## 📞 Quick Reference

| Component | Connection            | Port | Status Check                 |
| --------- | --------------------- | ---- | ---------------------------- |
| Pixhawk   | /dev/ttyACM0 @ 115200 | -    | `ls /dev/ttyACM*`            |
| MAVProxy  | TCP Server            | 7000 | `netstat -tuln \| grep 7000` |
| Sensors   | TCP Server            | 5002 | `netstat -tuln \| grep 5002` |
| Camera 0  | UDP Stream            | 5000 | `ps aux \| grep libcamera`   |
| Camera 1  | UDP Stream            | 5001 | `ps aux \| grep libcamera`   |

---

## ✅ You're All Set!

**Hardware Status:**

- ✅ Pixhawk detected and ready
- ✅ Port confirmed: /dev/ttyACM0
- ✅ Baud rate confirmed: 115200
- ✅ Heartbeat verified

**Next Action:**
Run `.\start_pi_services_auto.ps1` and you'll be connected in seconds!

**Everything is ready - let's get your ROV operational!** 🌊🤖
