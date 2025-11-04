#!/usr/bin/env python3
"""
Camera Server for Raspberry Pi
Streams H.264 video from Raspberry Pi cameras to Ground Station via UDP/RTP
Based on tested code from Pi Codes/cam_server.py
"""

import subprocess
import sys
import argparse


def start_camera_stream(
    camera_id, dest_ip, port, payload=96, width=640, height=480, framerate=30
):
    """
    Start streaming from a Raspberry Pi camera using libcamera and GStreamer.

    Args:
        camera_id: Camera index (0 or 1)
        dest_ip: Destination IP address (Ground Station)
        port: UDP port number
        payload: RTP payload type (96 or 97)
        width: Video width
        height: Video height
        framerate: Frames per second
    """
    print(f"[CAMERA {camera_id}] Starting stream → {dest_ip}:{port}")
    print(f"  Resolution: {width}x{height}@{framerate}fps")
    print(f"  Payload: {payload}")

    command = f"""
    libcamera-vid --camera {camera_id} -t 0 --inline -n \
    --width {width} --height {height} --framerate {framerate} \
    --codec h264 --libav-format h264 -o - | \
    gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt={payload} ! \
    udpsink host={dest_ip} port={port}
    """

    return subprocess.Popen(command, shell=True, executable="/bin/bash")


def main():
    parser = argparse.ArgumentParser(
        description="Stream Raspberry Pi camera to Ground Station"
    )
    parser.add_argument(
        "camera_id", type=int, choices=[0, 1], help="Camera ID (0 or 1)"
    )
    parser.add_argument("dest_ip", type=str, help="Destination IP address")
    parser.add_argument("port", type=int, help="UDP port number")
    parser.add_argument(
        "--payload", type=int, default=96, help="RTP payload type (default: 96)"
    )
    parser.add_argument(
        "--width", type=int, default=640, help="Video width (default: 640)"
    )
    parser.add_argument(
        "--height", type=int, default=480, help="Video height (default: 480)"
    )
    parser.add_argument(
        "--framerate", type=int, default=30, help="Framerate (default: 30)"
    )

    args = parser.parse_args()

    proc = start_camera_stream(
        camera_id=args.camera_id,
        dest_ip=args.dest_ip,
        port=args.port,
        payload=args.payload,
        width=args.width,
        height=args.height,
        framerate=args.framerate,
    )

    print(f"[CAMERA {args.camera_id}] Streaming...")
    print("Press Ctrl+C to stop")

    try:
        proc.wait()
    except KeyboardInterrupt:
        print(f"\n[CAMERA {args.camera_id}] Interrupted. Stopping stream.")
        proc.terminate()
        proc.wait()
        print(f"[CAMERA {args.camera_id}] Stopped")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Usage: python3 pi_camera_server.py <camera_id> <dest_ip> <port> [--payload PAYLOAD]"
        )
        print("\nExamples:")
        print("  Camera 0 → 192.168.0.100:5000")
        print("    python3 pi_camera_server.py 0 192.168.0.100 5000 --payload 96")
        print("\n  Camera 1 → 192.168.0.100:5001")
        print("    python3 pi_camera_server.py 1 192.168.0.100 5001 --payload 97")
        sys.exit(1)

    main()
