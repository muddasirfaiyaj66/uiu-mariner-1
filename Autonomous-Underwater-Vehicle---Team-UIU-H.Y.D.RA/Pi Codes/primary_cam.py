import subprocess
import sys

def start_stream(camera_id, dest_ip, port, payload=96):
    print(f"Starting camera {camera_id} → {dest_ip}:{port}")

    command = f"""
    libcamera-vid --camera {camera_id} -t 0 --inline -n \
    --width 1280 --height 720 --framerate 30 \
    --codec h264 --libav-format h264 -o - | \
    gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt={payload} ! \
    udpsink host={dest_ip} port={port}
    """

    return subprocess.Popen(command, shell=True, executable="/bin/bash")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 camera_server.py <camera_id> <dest_ip> <port>")
        sys.exit(1)

    camera_id = sys.argv[1]
    dest_ip = sys.argv[2]
    port = sys.argv[3]

    proc = start_stream(camera_id, dest_ip, port)

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("Interrupted. Stopping stream.")
        proc.terminate()
