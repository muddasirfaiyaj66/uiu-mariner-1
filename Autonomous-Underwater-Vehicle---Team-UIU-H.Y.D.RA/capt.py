import cv2
import os
import time

# Create a folder to save captured images if it doesn't exist
save_folder = '/home/mdkfahim30/360image/Basic360/img/captured_frames'
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# GStreamer pipeline for PiCamera (PiCam) feed
gst_pipeline = (
    "udpsrc port=5000 ! application/x-rtp, encoding-name=H264, payload=96 ! "
    "rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! appsink"
)

# Initialize the camera using GStreamer
cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Error: Could not open Raspberry Pi Camera stream.")
    exit(1)

print("Press 'c' to capture a frame and 'q' to quit.")

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Failed to capture frame.")
        break
    
    # Display the frame
    cv2.imshow('PiCamera Feed', frame)

    # Wait for key press
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('c'):  # Capture frame whelen 'c' is pressed
        # Get the current timestamp to make unique filenames
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.jpg"
        save_path = os.path.join(save_folder, filename)
        
        # Save the captured frame
        cv2.imwrite(save_path, frame)
        print(f"Frame captured and saved at {save_path}")
    
    elif key == ord('q'):  # Quit the program when 'q' is pressed
        break

cap.release()
cv2.destroyAllWindows()
