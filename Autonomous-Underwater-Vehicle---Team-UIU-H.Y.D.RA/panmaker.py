import cv2
import numpy as np
import os
import subprocess

# ==== CONFIG ====
VIDEO_PATH = "/home/mdkfahim30/Downloads/Photosphere/recorded_video.avi"
FRAME_DIR = "frames"
PANORAMA_FILE = "panorama.jpg"
EXTRACTION_INTERVAL = 0.3  # seconds
RESIZE_DIM = (1280, 720)
# =================

os.makedirs(FRAME_DIR, exist_ok=True)

def extract_frames():
    print("🎞️ Extracting frames...")
    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps == 0:
        print("❌ ERROR: Could not read video. Check VIDEO_PATH.")
        return

    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = total_frames / fps

    sec = 0
    count = 0
    while sec < duration:
        cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        ret, frame = cap.read()
        if ret:
            filename = os.path.join(FRAME_DIR, f"frame{count:03d}.jpg")
            cv2.imwrite(filename, frame)
            print(f"✅ Saved: {filename}")
            count += 1
        sec += EXTRACTION_INTERVAL
    cap.release()

def stitch_frames():
    print("🧵 Stitching frames using ORB + BFMatcher...")
    images = []
    for file in sorted(os.listdir(FRAME_DIR)):
        path = os.path.join(FRAME_DIR, file)
        img = cv2.imread(path)
        if img is not None:
            resized = cv2.resize(img, RESIZE_DIM)
            images.append(resized)

    if len(images) < 2:
        print("❌ Not enough frames to stitch.")
        return

    orb = cv2.ORB_create(3000)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    base = images[0]

    for i in range(1, len(images)):
        kp1, des1 = orb.detectAndCompute(base, None)
        kp2, des2 = orb.detectAndCompute(images[i], None)

        if des1 is None or des2 is None:
            print(f"⚠️ No descriptors found in image {i}. Skipping...")
            continue

        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)

        if len(matches) < 10:
            print(f"⚠️ Not enough good matches between base and image {i}. Skipping...")
            continue

        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        H, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        if H is None:
            print(f"⚠️ Homography failed at image {i}. Skipping...")
            continue

        height = base.shape[0]
        width = base.shape[1] + images[i].shape[1]

        # New approach: always stitch to the current base and update it
        try:
            result = cv2.warpPerspective(images[i], H, (width, height))
            result[0:base.shape[0], 0:base.shape[1]] = base
            base = result
            print(f"✅ Merged image {i}")
        except Exception as e:
            print(f"⚠️ Warp failed at image {i}: {e}")


    cv2.imwrite(PANORAMA_FILE, base)
    print(f"✅ Panorama saved: {PANORAMA_FILE}")

def tag_as_360():
    if not os.path.exists(PANORAMA_FILE):
        print("⚠️ Panorama image not found. Skipping metadata tagging.")
        return

    print("🏷️ Tagging image as 360°...")
    try:
        subprocess.run(["exiftool", "-ProjectionType=equirectangular", PANORAMA_FILE], check=True)
        print("✅ Metadata added!")
    except FileNotFoundError:
        print("❌ 'exiftool' not found. Install with:")
        print("   sudo apt install libimage-exiftool-perl")
    except subprocess.CalledProcessError:
        print("❌ Failed to tag image as 360°.")

if __name__ == "__main__":
    extract_frames()
    stitch_frames()
    tag_as_360()
