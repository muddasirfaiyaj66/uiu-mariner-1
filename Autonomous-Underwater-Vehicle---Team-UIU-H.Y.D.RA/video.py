import cv2
import numpy as np
import os
import time

# CONFIGURATION
NUM_FRAMES = 10
FRAME_DELAY_SEC = 2
FRAME_DIM = (1920, 1080)
SAVE_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "final_panorama.jpg")

GSTREAMER_PIPELINE = (
    "udpsrc port=5001 caps=\"application/x-rtp, media=video, encoding-name=H264, payload=96\" ! "
    "rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! appsink"
)

def preprocess_image(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    return sharpened

def detect_and_match_features(img1, img2):
    orb = cv2.ORB_create(4000)
    img1 = preprocess_image(img1)
    img2 = preprocess_image(img2)
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    if des1 is None or des2 is None:
        return None, None, None
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bf.knnMatch(des1, des2, k=2)
    good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]
    if len(good_matches) < 10:
        return None, None, None
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    return src_pts, dst_pts, good_matches

def stitch_two_images(img1, img2):
    src_pts, dst_pts, matches = detect_and_match_features(img1, img2)
    if src_pts is None:
        return None
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    if H is None:
        return None
    height = max(img1.shape[0], img2.shape[0])
    width = img1.shape[1] + img2.shape[1]
    result = cv2.warpPerspective(img1, H, (width, height))
    result[0:img2.shape[0], 0:img2.shape[1]] = img2
    return result

def crop_black_borders(panorama):
    gray = cv2.cvtColor(panorama, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return panorama
    x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
    return panorama[y:y+h, x:x+w]

def stitch_center_out(frames):
    if len(frames) < 2:
        return None
    center_idx = len(frames) // 2
    result = frames[center_idx]
    for i in range(center_idx - 1, -1, -1):
        result = stitch_two_images(frames[i], result)
        if result is None:
            return None
    for i in range(center_idx + 1, len(frames)):
        result = stitch_two_images(result, frames[i])
        if result is None:
            return None
    return crop_black_borders(result)

def auto_capture_and_stitch():
    cap = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        print("❌ Could not open GStreamer stream.")
        return

    captured = []
    print(f"📷 Capturing {NUM_FRAMES} frames every {FRAME_DELAY_SEC}s...")

    while len(captured) < NUM_FRAMES:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame read failed.")
            continue

        resized = cv2.resize(frame, FRAME_DIM)
        captured.append(resized.copy())
        print(f"✅ Captured frame {len(captured)}/{NUM_FRAMES}")
        time.sleep(FRAME_DELAY_SEC)

    cap.release()
    print("🔄 Stitching in progress...")
    stitched = stitch_center_out(captured)

    if stitched is not None:
        cv2.imwrite(SAVE_PATH, stitched)
        print(f"✅ Panorama saved to: {SAVE_PATH}")
        cv2.imshow("Final Panorama", stitched)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("❌ Stitching failed.")

if __name__ == "__main__":
    auto_capture_and_stitch()
