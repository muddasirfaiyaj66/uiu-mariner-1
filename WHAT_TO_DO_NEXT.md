# 🚀 QUICK START - What to Do Next

## ✅ **Current Status:**

- ✅ **Controller:** Nintendo Switch Pro Controller connected and working
- ❌ **Raspberry Pi Services:** Not running (need to start)
- ❌ **Pixhawk:** Not connected (Pi services needed)
- ❌ **Cameras:** Not streaming (Pi services needed)
- ❌ **Sensors:** Not connected (Pi services needed)

---

## 📋 **What You Need to Do:**

### **The Main Issue:** Raspberry Pi services are not running!

The error `[WinError 10061] No connection could be made` means:

- Raspberry Pi is reachable (ping works)
- But NO services are running on the Pi

---

## 🍓 **Step-by-Step: Start Raspberry Pi Services**

### **1. Copy Scripts to Raspberry Pi** (From Windows)

```powershell
cd "E:\UIU MARINER\mariner-software-1.0"
scp -r pi_scripts pi@raspberrypi.local:~/mariner/
```

**Password when asked:** `1234`

---

### **2. SSH to Raspberry Pi**

```powershell
ssh pi@raspberrypi.local
```

**Password:** `1234`

---

### **3. Make Scripts Executable** (On Raspberry Pi)

```bash
cd ~/mariner/pi_scripts
chmod +x *.sh *.py
```

---

### **4. Detect Your Hardware** (On Raspberry Pi)

**Find Pixhawk:**

```bash
python3 detect_pixhawk.py
```

This will show you:

```
✅ PIXHAWK FOUND!
Port: /dev/ttyACM0
Baud Rate: 57600
```

**Find Cameras:**

```bash
./detect_cameras.sh
```

This will show:

```
✅ Pi Camera Module detected!
OR
✅ USB webcams detected: /dev/video0
```

---

### **5. Start ALL Services** (On Raspberry Pi)

```bash
./start_all_services.sh 192.168.0.104
```

This starts:

- ✅ Sensor Server (BMP388) on port 5000
- ✅ MAVProxy Server (Pixhawk) on port 7000
- ✅ Camera 0 stream on port 5000 (UDP)
- ✅ Camera 1 stream on port 5001 (UDP)

**Expected output:**

```
🚀 Starting UIU MARINER ROV Services...
1️⃣  Starting Sensor Server...
   ✅ Sensor server started
2️⃣  Starting MAVProxy Server...
   ✅ MAVProxy started
3️⃣  Starting Camera 0...
   ✅ Camera 0 started
4️⃣  Starting Camera 1...
   ✅ Camera 1 started
```

---

### **6. Launch Application** (Back on Windows)

```powershell
cd "E:\UIU MARINER\mariner-software-1.0"
.\venv\Scripts\Activate.ps1
python launch_mariner.py
```

---

## ✅ **What You Should See:**

### **On Raspberry Pi:**

```bash
screen -ls
# Shows: sensors, mavproxy, cam0, cam1
```

### **On Windows Application:**

```
[PIXHAWK] ✅ Connected via tcp:raspberrypi.local:7000
[SENSORS] ✅ Connected - Depth: 0.5m, Temp: 24.3°C
[CAM0] ✅ Stream started
[CAM1] ✅ Stream started
[JOYSTICK] ✅ Connected: Nintendo Switch Pro Controller
```

### **When You Move Joystick:**

```
[THRUSTER] Forward/Back: -0.85 → Ch1(Pin1)=1300, Ch8(Pin8)=1700
[THRUSTER] Left/Right: 0.42 → Ch2(Pin2)=1600, Ch5(Pin5)=1400
[THRUSTER] Up/Down: 0.65 → Ch3(Pin3)=1650, Ch4(Pin4)=1650, Ch6(Pin6)=1350, Ch7(Pin7)=1350
```

---

## ❓ **Common Questions:**

### **Q: Why can't I run detect_pixhawk.py on Windows?**

**A:** That script checks Raspberry Pi hardware (serial ports like `/dev/ttyACM0`). It only works on the Raspberry Pi where Pixhawk is physically connected.

### **Q: Why can't I run ./detect_cameras.sh on Windows?**

**A:** That's a bash script for Linux/Raspberry Pi. It checks for Pi Camera Module and USB webcams connected to the Pi.

### **Q: My controller keeps disconnecting?**

**A:** Keep it connected via Bluetooth. If it disconnects, just reconnect it through Windows Bluetooth settings.

### **Q: I don't have a BMP388 sensor yet?**

**A:** The sensor server will fail to start, but other services (Pixhawk, cameras) will still work. Just ignore sensor errors for now.

---

## 🔍 **Troubleshooting on Raspberry Pi:**

### **Check if services are running:**

```bash
screen -ls
```

### **View service logs:**

```bash
screen -r mavproxy      # View Pixhawk connection
screen -r sensors       # View sensor data
screen -r cam0          # View camera 0 stream
# Press Ctrl+A then D to detach (keep running)
```

### **Stop all services:**

```bash
./stop_all_services.sh
```

### **Restart services:**

```bash
./stop_all_services.sh
./start_all_services.sh 192.168.0.104
```

---

## 📞 **Need Help?**

See these guides:

- `pi_scripts/COMPLETE_SETUP_GUIDE.md` - Full detailed guide
- `UPDATES_APPLIED.md` - What was changed
- `CONTROLLER_AND_PI_STATUS.md` - Controller status

---

## 🎯 **Your Next Action:**

**Run this command NOW:**

```powershell
scp -r pi_scripts pi@raspberrypi.local:~/mariner/
```

Then follow steps 2-6 above! 🚀
