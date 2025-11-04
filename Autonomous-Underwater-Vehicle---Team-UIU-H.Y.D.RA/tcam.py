import cv2

pipeline = "appsrc ! video/x-raw,format=BGR,width=1280,height=720,framerate=30/1 ! videoconvert ! appsink"
cap = cv2.VideoCapture("udp://192.168.184.159:7000", cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break
    # Process frame here
cap.release()
