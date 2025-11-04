#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modified for Raspberry Pi Camera Streaming
"""

import cv2
import numpy as np
import os

dim = (1920, 1080)

downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

# Replace webcam capture with GStreamer pipeline to receive UDP stream
gst_pipeline = (
    "udpsrc port=5000 ! application/x-rtp, encoding-name=H264, payload=96 ! "
    "rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! appsink"
)

cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Failed to open video stream. Check GStreamer pipeline and network connection.")
    exit(1)

captured_frames = []

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to receive frame.")
        break

    frame_resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
    cv2.imshow('Raspberry Pi Camera Feed', frame_resized)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        captured_frames.append(frame_resized)
        print("Frame captured for panorama.")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Stitching process
if len(captured_frames) >= 2:
    stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)
    ret, pano = stitcher.stitch(captured_frames)
    
    if ret == cv2.Stitcher_OK:
        panorama_path = os.path.join(downloads_path, 'panorama.jpg')
        cv2.imwrite(panorama_path, pano)
        print(f"Panorama saved at: {panorama_path}")

        cv2.imshow('Panorama', pano)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print(f"Stitching failed with error code: {ret}")
else:
    print("Not enough frames captured for stitching.")
