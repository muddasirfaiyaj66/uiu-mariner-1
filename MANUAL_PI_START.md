# 🚀 MANUAL PI SETUP - Simple Steps

Since the automated script had issues, let's do it manually (it's actually easier!):

## Step 1: SSH to Raspberry Pi

```powershell
ssh pi@raspberrypi.local
# Enter password when prompted
```

## Step 2: Start Services on Pi

Copy and paste these commands **one by one** on the Pi:

### A. Stop any existing services

```bash
pkill -9 python3
pkill -9 mavproxy
pkill -9 libcamera-vid
```

### B. Start Sensor Server

```bash
cd ~/pi_scripts
python3 sensorServer.py &
```

### C. Start MAVProxy (with your confirmed Pixhawk port)

```bash
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --out=tcpin:0.0.0.0:7000 &
```

### D. Start Cameras (if available)

```bash
# Camera 0
export GS_IP="192.168.56.1"  # Your Ground Station IP
./cam0.sh &

# Camera 1
./cam1.sh &
```

### E. Verify Services Running

```bash
# Check processes
ps aux | grep -E "sensor|mavproxy|libcamera"

# Check listening ports
netstat -tuln | grep -E "5002|7000"
```

**You should see:**

- `python3 sensorServer.py` process
- `mavproxy.py` process
- Port 5002 listening (LISTEN)
- Port 7000 listening (LISTEN)

## Step 3: Keep SSH Open and Launch Mariner

Leave the SSH terminal open and in another PowerShell window:

```powershell
cd "F:\Web Development\uiu-mariner\uiu-mariner-1"
.\.venv\Scripts\Activate.ps1
python launch_mariner.py
```

## Expected Result

You should see:

```
[SENSORS] ✅ Connected (Real BMP388 data)
[PIXHAWK] ✅ Connected (tcp:raspberrypi.local:7000)
[JOYSTICK] ✅ Connected: Nintendo Switch Pro Controller
```

---

## 🔧 Troubleshooting

### If Sensor Server Fails:

```bash
# Check if BMP388 is connected
i2cdetect -y 1
# Should show device at address 0x77

# Check sensor script exists
ls -l ~/pi_scripts/sensorServer.py

# Run manually to see errors
python3 ~/pi_scripts/sensorServer.py
```

### If MAVProxy Fails:

```bash
# Check Pixhawk connection
ls -l /dev/ttyACM0

# Check permissions
sudo usermod -a -G dialout pi
sudo chmod 666 /dev/ttyACM0

# Test connection
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200
```

### View Logs:

```bash
# If services were started in background, check:
tail -f /tmp/sensor.log
tail -f /tmp/mavproxy.log
```

---

## Quick Reference Commands

| Action          | Command                                 |
| --------------- | --------------------------------------- |
| SSH to Pi       | `ssh pi@raspberrypi.local`              |
| Check processes | `ps aux \| grep -E "sensor\|mavproxy"`  |
| Check ports     | `netstat -tuln \| grep -E "5002\|7000"` |
| Stop all        | `pkill -9 python3; pkill -9 mavproxy`   |
| View logs       | `tail -f /tmp/*.log`                    |

---

## ⚡ Even Simpler: One-Line Start

If your Pi scripts are set up, just run this ONE command on Pi:

```bash
cd ~/pi_scripts && python3 sensorServer.py & mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --out=tcpin:0.0.0.0:7000 & ./cam0.sh & ./cam1.sh &
```

Then check it worked:

```bash
ps aux | grep -E "sensor|mavproxy"
```

---

**Ready to try? SSH to your Pi and start running these commands!** 🚀
