# 🚀 QUICK START - Connect to Your Raspberry Pi

## ⚡ Fast Setup (5 Minutes)

### 1️⃣ Connect to Pi

```bash
ssh pi@raspberrypi.local
# Password: 1234
```

### 2️⃣ Copy Scripts to Pi

```powershell
# From Windows PowerShell:
cd "E:\UIU MARINER\mariner-software-1.0"
scp -r pi_scripts pi@raspberrypi.local:~/mariner/
```

### 3️⃣ Make Scripts Executable

```bash
# On Raspberry Pi:
cd ~/mariner/pi_scripts
chmod +x *.sh *.py
```

### 4️⃣ Get Your PC's IP Address

```powershell
# On Windows:
ipconfig
# Look for "IPv4 Address" (e.g., 192.168.1.100)
```

### 5️⃣ Start All Services

```bash
# Replace 192.168.1.100 with YOUR PC's IP from step 4
./start_all_services.sh 192.168.1.100
```

### 6️⃣ Launch Application on Windows

```powershell
cd "E:\UIU MARINER\mariner-software-1.0"
.\venv\Scripts\Activate.ps1
python launch_mariner.py
```

---

## ✅ What You Should See

### On Raspberry Pi Terminal:

```
🚀 Starting UIU MARINER ROV Services...
========================================
📡 Ground Station IP: 192.168.1.100

1️⃣  Starting Sensor Server (BMP388)...
   ✅ Sensor server started

2️⃣  Starting MAVProxy Server (Pixhawk)...
   ✅ MAVProxy started

3️⃣  Starting Camera 0 Stream...
   ✅ Camera 0 started

4️⃣  Starting Camera 1 Stream...
   ✅ Camera 1 started

✅ Service Startup Complete!
```

### On Windows Application:

- ✅ **Pixhawk:** Connected
- ✅ **Sensors:** Temperature, Pressure, Depth updating
- ✅ **Cameras:** Live video feeds
- ✅ **Controller:** Nintendo Switch Pro Controller detected

---

## 🔍 View Service Logs

```bash
screen -ls                # List all running services
screen -r sensors         # View sensor logs
screen -r mavproxy        # View MAVProxy logs
screen -r cam0           # View camera 0 logs
screen -r cam1           # View camera 1 logs

# Press Ctrl+A then D to detach (keep service running)
```

---

## 🛑 Stop All Services

```bash
./stop_all_services.sh
```

---

## 🧪 Test Individual Components

```bash
# Test sensor
python3 test_bmp388.py

# Test camera 0
libcamera-hello --camera 0 -t 5000

# Test Pixhawk connection
python3 -m pymavlink.mavproxy --master=/dev/serial0 --baudrate=57600
```

---

## ❓ Troubleshooting

### Pi Not Reachable

```powershell
# From Windows:
ping raspberrypi.local
```

### Sensor Not Working

```bash
sudo i2cdetect -y 1
# Should show device at 0x77
```

### Pixhawk Not Connecting

```bash
ls -l /dev/serial0
# Should exist and point to ttyAMA0
```

### Cameras Not Working

```bash
libcamera-hello --list-cameras
# Should list available cameras
```

---

## 📋 Network Ports

| Service  | Protocol | Port | Purpose          |
| -------- | -------- | ---- | ---------------- |
| Sensors  | TCP      | 5000 | BMP388 data      |
| MAVProxy | TCP      | 7000 | Pixhawk commands |
| Camera 0 | UDP      | 5000 | Video stream     |
| Camera 1 | UDP      | 5001 | Video stream     |

---

## 🎯 Next Steps

1. ✅ **Start services on Pi** → `./start_all_services.sh YOUR_PC_IP`
2. ✅ **Launch app on Windows** → `python launch_mariner.py`
3. ✅ **Test with thrusters DISARMED** → Use Nintendo Switch Pro Controller
4. ✅ **ARM system** → Press ARM button or controller button
5. ✅ **Start mission** → Control ROV with joysticks

---

**📖 Full Documentation:** See `SETUP_RASPBERRY_PI.md` for detailed instructions

**🆘 Need Help?** Check the troubleshooting section in `SETUP_RASPBERRY_PI.md`
