import cv2
import numpy as np
import os

# ==== Config ====
FRAME_DIM = (1920, 1080)
DOWNLOADS_PATH = os.path.join(os.path.expanduser("~"), "Downloads")
SAVE_FILENAME = "panorama.jpg"

# GStreamer pipeline to receive and decode stream
GSTREAMER_PIPELINE = (
    "udpsrc port=5001 caps=\"application/x-rtp, media=video, encoding-name=H264, payload=96\" ! "
    "rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! appsink"
)
# =================


def capture_frames():
    cap = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        print("❌ Unable to open GStreamer stream.")
        return []

    captured_frames = []
    print("Press 'c' to capture a frame, 'q' to quit and stitch.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to read frame from stream.")
            break

        frame_resized = cv2.resize(frame, FRAME_DIM, interpolation=cv2.INTER_AREA)
        cv2.imshow('Stream Feed', frame_resized)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            captured_frames.append(frame_resized.copy())
            print(f"✅ Captured frame {len(captured_frames)}")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return captured_frames


def stitch_frames(frames):
    print("🔍 Using ORB + BFMatcher for stitching...")

    orb = cv2.ORB_create(3000)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    base_img = frames[0]
    for i in range(1, len(frames)):
        kp1, des1 = orb.detectAndCompute(base_img, None)
        kp2, des2 = orb.detectAndCompute(frames[i], None)

        if des1 is None or des2 is None:
            print(f"❌ No features found between image {i} and base image.")
            return None

        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)

        if len(matches) < 10:
            print(f"❌ Not enough good matches between image {i} and base image.")
            return None

        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

        if H is None:
            print(f"❌ Failed to compute homography between image {i} and base image.")
            return None

        height = max(base_img.shape[0], frames[i].shape[0])
        width = base_img.shape[1] + frames[i].shape[1]
        result = cv2.warpPerspective(frames[i], H, (width, height))
        result[0:base_img.shape[0], 0:base_img.shape[1]] = base_img

        base_img = result

    print("✅ ORB-based stitching completed.")
    return base_img



def save_and_show(panorama):
    if panorama is None:
        return

    output_path = os.path.join(DOWNLOADS_PATH, SAVE_FILENAME)
    cv2.imwrite(output_path, panorama)
    print(f"💾 Panorama saved to: {output_path}")

    cv2.imshow("Panorama", panorama)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    frames = capture_frames()
    panorama = stitch_frames(frames)
    save_and_show(panorama)


if __name__ == "__main__":
    main()
