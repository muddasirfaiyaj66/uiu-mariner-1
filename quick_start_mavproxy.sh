#!/bin/bash
pkill -f pi_mavproxy
sleep 2
cd /home/pi/mariner/pi_scripts
python3 pi_mavproxy_server.py --master /dev/ttyACM1 --baudrate 115200 --port 7000 > /tmp/rov_mavproxy.log 2>&1 &
echo "Started MAVProxy"
sleep 2
ps aux | grep pi_mavproxy | grep -v grep
