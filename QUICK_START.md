# Mariner ROV - Quick Start Guide

## On Raspberry Pi (One Time Setup)

```bash
# 1. Copy project to Pi
scp -r /path/to/uiu-mariner-1 pi@raspberrypi.local:/opt/mariner

# 2. SSH into Pi
ssh pi@raspberrypi.local

# 3. Install dependencies
cd /opt/mariner
pip install -r requirements.txt
pip install MAVProxy

# 4. Make scripts executable
chmod +x pi_scripts/pi_autostart_all.sh

# 5. Setup systemd (optional - for autostart on boot)
sudo cp pi_scripts/mariner_autostart.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mariner_autostart.service
```

## Running on Pi

**Start all services:**

```bash
bash /opt/mariner/pi_scripts/pi_autostart_all.sh start
```

**Check status:**

```bash
bash /opt/mariner/pi_scripts/pi_autostart_all.sh status
```

**Stop all services:**

```bash
bash /opt/mariner/pi_scripts/pi_autostart_all.sh stop
```

**View logs:**

```bash
tail -f /opt/mariner/logs/sensor_server.log
tail -f /opt/mariner/logs/camera_server.log
tail -f /opt/mariner/logs/mavproxy_relay.log
```

## On Ground Station (Windows/Mac)

```bash
# Run GUI application
python launch_mariner.py
```

**Expected GUI indicators when Pi is running:**

- Camera feeds: Live video from 2 cameras
- Sensor data: Depth, temperature, pressure
- Connection status: Connected/Disconnected
- Thruster status: Armed/Disarmed indicator

## Troubleshooting

| Issue                 | Solution                                                         |
| --------------------- | ---------------------------------------------------------------- |
| Pi not connecting     | Check: `bash /opt/mariner/pi_scripts/pi_autostart_all.sh status` |
| Cameras not streaming | Restart cameras: Kill process on Pi and run start command again  |
| No sensor data        | Check I2C connection: `i2cdetect -y 1` on Pi                     |
| Pixhawk not detected  | Check serial: `ls -la /dev/ttyAMA0` on Pi                        |

## Port Summary

- **MAVLink TCP**: 7000 (Ground Station ↔ Pi)
- **Sensor TCP**: 5002 (BMP388 telemetry)
- **Camera UDP**: 5000, 5001 (H.264 video streams)

Done! System ready to test. 🚀
