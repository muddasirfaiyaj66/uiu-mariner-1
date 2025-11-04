# ROV Control System - Quick Reference

## 🎮 Joystick Controls (Xbox 360)

### Movement

| Input         | Action         | Thrusters  |
| ------------- | -------------- | ---------- |
| Left Stick ↑  | Forward        | 1, 8       |
| Left Stick ↓  | Backward       | 1, 8       |
| Left Stick ←  | Rotate Left    | 2, 5       |
| Left Stick →  | Rotate Right   | 2, 5       |
| Right Stick ↑ | Ascend (Up)    | 3, 4, 6, 7 |
| Right Stick ↓ | Descend (Down) | 3, 4, 6, 7 |

### Buttons

| Button  | Function       |
| ------- | -------------- |
| Start   | Emergency Stop |
| Back    | Reserved       |
| A/B/X/Y | Reserved       |

## 🔌 Connection Strings

### UDP (Ethernet)

```
udp:192.168.0.104:14550
```

### TCP (MAVProxy)

```
tcp:10.42.0.185:5760
```

### Serial (USB)

```
Windows: serial:COM3:57600
Linux:   serial:/dev/ttyUSB0:57600
```

## 🚦 Startup Sequence

1. Power on ROV (Pixhawk + ESCs)
2. Connect joystick to PC
3. Launch application: `python src/ui/rovControlApp.py`
4. Verify green "Pixhawk: Connected" status
5. Select flight mode (MANUAL recommended)
6. Click "ARM THRUSTERS"
7. Test joystick gently
8. Dive!

## ⚠️ Emergency Procedures

### Software Emergency Stop

- Press **Start** button on joystick
- Click **EMERGENCY STOP** in GUI
- Both actions: disarm + neutral all thrusters

### Connection Lost

- System automatically stops sending commands
- Pixhawk failsafe takes over (check ArduSub settings)
- Close application and restart

## 🔧 Thruster PWM Values

| Value | Meaning        |
| ----- | -------------- |
| 1000  | Full Reverse   |
| 1500  | Neutral (Stop) |
| 2000  | Full Forward   |

## 📝 Pre-Flight Checklist

- [ ] ROV powered on
- [ ] Battery charged (LiPo voltage check)
- [ ] All ESCs initialized (beep pattern)
- [ ] Pixhawk LED: Green/Blue (GPS optional)
- [ ] Joystick connected and recognized
- [ ] GUI shows "Pixhawk: Connected" (green)
- [ ] GUI shows "Joystick: [Your Controller]" (green)
- [ ] Thrusters in water (don't run dry!)
- [ ] Tether/cable secured
- [ ] Emergency stop accessible
- [ ] Mode set to MANUAL
- [ ] ARM button ready

## 🐛 Quick Troubleshooting

| Problem               | Solution                                                |
| --------------------- | ------------------------------------------------------- |
| No joystick           | Replug USB, check Device Manager                        |
| Can't connect Pixhawk | Check IP/port, test with QGroundControl                 |
| Thrusters not moving  | Verify ARMED, check ESC connections                     |
| Erratic movement      | Recalibrate joystick in Windows settings                |
| GUI won't start       | Install dependencies: `pip install -r requirements.txt` |

## 📞 Support

Check `README.md` for full documentation.

**Team UIU HYDRA - November 2025**
