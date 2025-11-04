#!/bin/bash
cd /home/pi/mariner/pi_scripts
pkill -f pi_mavproxy_server.py
sleep 1
nohup python3 pi_mavproxy_server.py > /tmp/mavproxy_server.log 2>&1 &
sleep 2
tail -30 /tmp/mavproxy_server.log
