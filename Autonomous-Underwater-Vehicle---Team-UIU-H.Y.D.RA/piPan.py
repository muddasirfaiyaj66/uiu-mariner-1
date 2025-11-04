#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Updated to capture frames from PiCamera using GStreamer UDP Stream
"""

import cv2
import numpy as np
import os

# Set the resolution
dim = (1920, 1080)

# Get the Downloads folder path
downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

# GStreamer pipeline to receive the PiCamera stream
gst_pipeline = (
    "udpsrc port=5000 ! application/x-rtp, encoding-name=H264, payload=96 ! "
    "rtph264depay ! avdec_h264 ! videoconvert ! appsink"
)

# OpenCV VideoCapture using GStreamer
cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Error: Could not open camera stream. Check GStreamer and network settings.")
    exit()

captured_frames = []

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Frame not received.")
        break

    frame_resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
    cv2.imshow('PiCamera Feed', frame_resized)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        captured_frames.append(frame_resized)
        print("Frame captured for panorama.")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Stitching the images
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
