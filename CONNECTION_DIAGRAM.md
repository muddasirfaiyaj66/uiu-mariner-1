# Connection Diagram 📡

## Complete System Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         GROUND STATION (Your PC)                            │
│                              Windows 10/11                                  │
│                                                                             │
│  ┌─────────────────┐         ┌──────────────────────────────────┐         │
│  │  Xbox Controller│         │     marinerApp.py                │         │
│  │                 │         │  - PyQt6 GUI                     │         │
│  │  USB/Bluetooth ─┼────────▶│  - Camera display                │         │
│  │                 │         │  - Sensor display                │         │
│  │  Axes & Buttons │         │  - Joystick reading              │         │
│  └─────────────────┘         │  - MAVLink sending               │         │
│                               └──────────────┬───────────────────┘         │
│                                              │                             │
│                                              │ Network Interface           │
│                                              │ IP: 192.168.0.100          │
└──────────────────────────────────────────────┼─────────────────────────────┘
                                               │
                                               │
                            WiFi/Ethernet Tether (Network Cable)
                            UDP Packets with MAVLink commands
                            Video streams (H.264)
                            Sensor data (TCP)
                                               │
                                               │
┌──────────────────────────────────────────────┼─────────────────────────────┐
│                                              │                             │
│                     ROV (Underwater Vehicle) │                             │
│                                              ▼                             │
│                               ┌──────────────────────────┐                 │
│                               │   Raspberry Pi 4         │                 │
│                               │   IP: 192.168.0.104      │                 │
│                               │                          │                 │
│    ┌────────────┐             │  Services Running:       │                 │
│    │ Pi Camera 0│────────────▶│  - GStreamer (5000)      │                 │
│    │ (Front)    │ CSI-0       │  - GStreamer (5001)      │                 │
│    └────────────┘             │  - Sensor TCP (5000)     │                 │
│                               │  - MAVProxy (14550)      │                 │
│    ┌────────────┐             │                          │                 │
│    │ Pi Camera 1│────────────▶│  Forwards MAVLink to     │                 │
│    │ (Bottom)   │ CSI-1       │  Pixhawk via serial      │                 │
│    └────────────┘             └──────────┬───────────────┘                 │
│                                          │                                 │
│    ┌────────────┐                        │ Serial                          │
│    │  Sensors   │                        │ /dev/ttyUSB0:115200             │
│    │ Temp/Press │──────────────────┐     │                                 │
│    │  /Depth    │ GPIO/I2C         │     ▼                                 │
│    └────────────┘                  │  ┌──────────────────────────┐        │
│                                    │  │      Pixhawk              │        │
│                                    │  │   (ArduSub Firmware)      │        │
│                                    │  │                           │        │
│                                    │  │  Receives:                │        │
│                                    └─▶│  - RC_CHANNELS_OVERRIDE   │        │
│                                       │                           │        │
│                                       │  Controls:                │        │
│                                       │  - 8 x Thrusters (ESCs)   │        │
│                                       │  - Lights, servos, etc.   │        │
│                                       └──────┬────────────────────┘        │
│                                              │                             │
│                                              │ PWM Signals                 │
│                                              │ (1000-2000 µs)              │
│                                              ▼                             │
│                                    ┌──────────────────┐                    │
│                                    │   8 x Thrusters  │                    │
│                                    │   via ESCs       │                    │
│                                    └──────────────────┘                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Joystick to Thrusters

### Step-by-Step Flow When You Move the Controller

```
1. GROUND STATION (Your PC)
   ┌─────────────────────────────────────────┐
   │ Xbox Controller moved                   │
   │ - Left stick forward                    │
   │ - Right stick up                        │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ pygame library reads:                   │
   │ - Axis 0: Left X = 0.0 (centered)       │
   │ - Axis 1: Left Y = -0.8 (forward 80%)   │
   │ - Axis 3: Right Y = -0.5 (up 50%)       │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ joystickController.py converts to:      │
   │ - Forward: +0.8                         │
   │ - Strafe: 0.0                           │
   │ - Vertical: +0.5                        │
   │ - Yaw: 0.0                              │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Computes 8 thruster PWM values:         │
   │ Thruster 1: 1640 (forward-left)         │
   │ Thruster 2: 1640 (forward-right)        │
   │ Thruster 3: 1550 (vertical-FL)          │
   │ Thruster 4: 1550 (vertical-FR)          │
   │ Thruster 5: 1550 (vertical-RL)          │
   │ Thruster 6: 1550 (vertical-RR)          │
   │ Thruster 7: 1360 (backward-left)        │
   │ Thruster 8: 1360 (backward-right)       │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ mavlinkConnection.py creates:           │
   │ RC_CHANNELS_OVERRIDE message            │
   │ - chan1_raw = 1640                      │
   │ - chan2_raw = 1640                      │
   │ - chan3_raw = 1550                      │
   │ ... (8 channels total)                  │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Sends UDP packet to:                    │
   │ 192.168.0.104:14550                     │
   └───────────────┬─────────────────────────┘
                   │
                   │ Network (WiFi/Ethernet)
                   │
2. ROV (Raspberry Pi)  ▼
   ┌─────────────────────────────────────────┐
   │ Receives UDP packet on port 14550       │
   │ MAVProxy forwards to serial             │
   └───────────────┬─────────────────────────┘
                   │
                   │ Serial: /dev/ttyUSB0
                   │
3. ROV (Pixhawk)       ▼
   ┌─────────────────────────────────────────┐
   │ ArduSub receives RC_CHANNELS_OVERRIDE   │
   │ Applies motor mixing algorithm          │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Sends PWM signals to ESCs:              │
   │ Motor 1: 1640µs                         │
   │ Motor 2: 1640µs                         │
   │ Motor 3: 1550µs                         │
   │ ... etc                                 │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Thrusters spin!                         │
   │ - Forward thrusters: Forward            │
   │ - Vertical thrusters: Upward            │
   │ ROV moves forward and up                │
   └─────────────────────────────────────────┘

Total latency: ~50-150ms (USB joystick to thruster response)
```

---

## Network Ports Reference

### From Ground Station → ROV

| Port  | Protocol | Purpose          | Data                                           |
| ----- | -------- | ---------------- | ---------------------------------------------- |
| 14550 | UDP      | MAVLink Commands | RC_CHANNELS_OVERRIDE, arm/disarm, mode changes |
| 5000  | UDP      | Camera 0 Video   | H.264 encoded video stream (front camera)      |
| 5001  | UDP      | Camera 1 Video   | H.264 encoded video stream (bottom camera)     |
| 5000  | TCP      | Sensor Data      | Temperature, pressure, depth (JSON/CSV)        |

**Note:** Yes, port 5000 is used for both camera UDP and sensor TCP. This is OK because they use different protocols!

---

## IP Address Configuration

### Ground Station (Your PC)

```
IP Address:  192.168.0.100
Subnet Mask: 255.255.255.0
Gateway:     192.168.0.1 (if using router)
             (none if direct tether)
```

### ROV (Raspberry Pi)

```
IP Address:  192.168.0.104
Subnet Mask: 255.255.255.0
Gateway:     192.168.0.1 (if using router)
             (none if direct tether)
```

### Testing

```powershell
# From Ground Station, test each service:

# Test basic connectivity
ping 192.168.0.104

# Test MAVLink port (if netcat installed)
nc -u 192.168.0.104 14550

# Or use PowerShell
Test-NetConnection -ComputerName 192.168.0.104 -Port 14550
```

---

## Physical Connections Checklist

### Ground Station Side

- [ ] Xbox Controller → PC via USB or Bluetooth
- [ ] PC → Network Router/Switch via Ethernet
- [ ] OR PC → Tether cable directly to ROV

### ROV Side

- [ ] Raspberry Pi → Pixhawk via UART (GPIO pins 8,10) or USB
- [ ] Pi Camera 0 → Pi CSI port 0
- [ ] Pi Camera 1 → Pi CSI port 1
- [ ] Sensors → Pi GPIO pins (I2C/SPI)
- [ ] Raspberry Pi → Network Router or Tether
- [ ] Pixhawk → 8x ESCs via PWM outputs
- [ ] ESCs → 8x Thrusters
- [ ] Power supply → All components

---

## Common Connection Mistakes

### ❌ Wrong: Joystick to ROV

```
Xbox Controller → ROV Raspberry Pi  [WRONG!]
```

**Why wrong:** ROV is underwater, can't connect wirelessly

### ✅ Correct: Joystick to Ground Station

```
Xbox Controller → Ground Station PC → Network → ROV  [CORRECT!]
```

---

### ❌ Wrong: Ground Station to Pixhawk directly

```
Ground Station PC → Pixhawk Serial  [WRONG!]
```

**Why wrong:** Pixhawk is on ROV, no direct serial connection

### ✅ Correct: Ground Station → Pi → Pixhawk

```
Ground Station PC → Network → Raspberry Pi → Serial → Pixhawk  [CORRECT!]
```

---

### ❌ Wrong: Running find_pixhawk.py on Ground Station

```
Ground Station PC> python find_pixhawk.py  [WRONG!]
```

**Why wrong:** Ground Station has no serial connection to Pixhawk

### ✅ Correct: Run on Raspberry Pi

```
ssh pi@192.168.0.104
pi@rov:~$ python find_pixhawk.py  [CORRECT!]
```

---

## Quick Reference Card

Print this and keep near your computer!

```
┌─────────────────────────────────────────────────────────┐
│           UIU MARINER CONNECTION GUIDE                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  GROUND STATION (Windows PC)                            │
│  • Xbox Controller: USB or Bluetooth to THIS PC         │
│  • IP Address: 192.168.0.100                            │
│  • Software: marinerApp.py                              │
│  • Connects to ROV via: UDP 192.168.0.104:14550         │
│                                                         │
│  ROV (Underwater)                                       │
│  • Raspberry Pi IP: 192.168.0.104                       │
│  • Pi → Pixhawk: Serial /dev/ttyUSB0:115200            │
│  • Services: Camera (5000,5001), Sensors (5000 TCP)     │
│                                                         │
│  CONTROLS                                               │
│  • Left Stick: Forward/Back/Strafe                      │
│  • Right Stick: Up/Down/Rotate                          │
│  • Triggers: Roll                                       │
│  • A Button: Arm/Disarm                                 │
│  • B Button: Emergency Stop                             │
│                                                         │
│  TESTING                                                │
│  • Joystick: joy.cpl (Windows)                          │
│  • Network: ping 192.168.0.104                          │
│  • MAVLink: Test-NetConnection -Port 14550              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

_Connection Diagram v1.0_  
_UIU MARINER ROV Control System_
