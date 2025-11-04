# import cv2
# import numpy as np

# # Define your known scale factor (update this after calibration)
# PIXEL_TO_MM = 0.5  # Example: 1 pixel = 0.5 mm (You must calibrate this!)

# # Global variables
# start_point = None
# end_point = None
# measuring = False

# def click_event(event, x, y, flags, param):
#     """ Capture mouse clicks for distance measurement. """
#     global start_point, end_point, measuring

#     if event == cv2.EVENT_LBUTTONDOWN:
#         if not measuring:  
#             start_point = (x, y)
#             measuring = True
#             print("Start Point:", start_point)
#         else:
#             end_point = (x, y)
#             measuring = False
#             print("End Point:", end_point)

# # Open video capture
# cap = cv2.VideoCapture(0)
# cv2.namedWindow("Distance Measurement")
# cv2.setMouseCallback("Distance Measurement", click_event)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Draw start point
#     if start_point:
#         cv2.circle(frame, start_point, 5, (0, 255, 0), -1)  # Green dot

#     # Draw end point and calculate distance
#     if end_point:
#         cv2.circle(frame, end_point, 5, (0, 0, 255), -1)  # Red dot
#         cv2.line(frame, start_point, end_point, (255, 0, 0), 2)  # Blue line

#         # Calculate distance in pixels
#         pixel_distance = np.linalg.norm(np.array(start_point) - np.array(end_point))
#         mm_distance = pixel_distance * PIXEL_TO_MM  # Convert pixels to mm

#         # Display distance
#         cv2.putText(frame, f"Distance: {mm_distance:.2f} mm", (50, 50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

#     cv2.imshow("Distance Measurement", frame)

#     key = cv2.waitKey(1) & 0xFF
#     if key == ord('s'):  # Press 'S' to start measurement
#         measuring = True

#     elif key == ord('e') and start_point:  # Press 'E' to finish measurement
#         measuring = False

#     elif key == ord('r'):  # Reset with 'R'
#         start_point = None
#         end_point = None
#         measuring = False
#         print("Reset!")

#     elif key == ord('q'):  # Quit with 'Q'
#         break

# cap.release()
# cv2.destroyAllWindows()
import cv2
import numpy as np

# Define your known scale factor (update after calibration)
PIXEL_TO_MM = 0.5  # Example: 1 pixel = 0.5 mm (Calibrate this!)

# GStreamer pipeline to receive the video stream
GST_PIPELINE = (
    "udpsrc port=5001 caps=\"application/x-rtp, media=video, encoding-name=H264, payload=96\" ! "
    "rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! appsink"
)

# Open GStreamer video stream
# cap = cv2.VideoCapture(GST_PIPELINE, cv2.CAP_GSTREAMER)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Unable to open GStreamer video stream")
    exit(1)

# Global variables
start_point = None
end_point = None
measuring = False

def click_event(event, x, y, flags, param):
    """ Capture mouse clicks for distance measurement. """
    global start_point, end_point, measuring

    if event == cv2.EVENT_LBUTTONDOWN:
        if not measuring:
            start_point = (x, y)
            measuring = True
            print("Start Point:", start_point)
        else:
            end_point = (x, y)
            measuring = False
            print("End Point:", end_point)

cv2.namedWindow("Distance Measurement")
cv2.setMouseCallback("Distance Measurement", click_event)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: No frame received")
        break

    # Draw start point
    if start_point:
        cv2.circle(frame, start_point, 5, (0, 255, 0), -1)  # Green dot

    # Draw end point and calculate distance
    if end_point:
        cv2.circle(frame, end_point, 5, (0, 0, 255), -1)  # Red dot
        cv2.line(frame, start_point, end_point, (255, 0, 0), 2)  # Blue line

        # Calculate distance in pixels
        pixel_distance = np.linalg.norm(np.array(start_point) - np.array(end_point))
        mm_distance = pixel_distance * PIXEL_TO_MM  # Convert pixels to mm

        # Display distance
        cv2.putText(frame, f"Distance: {mm_distance:.2f} mm", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    cv2.imshow("Distance Measurement", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):  # Start measurement
        measuring = True

    elif key == ord('e') and start_point:  # Finish measurement
        measuring = False

    elif key == ord('r'):  # Reset
        start_point = None
        end_point = None
        measuring = False
        print("Reset!")

    elif key == ord('q'):  # Quit
        break

cap.release()
cv2.destroyAllWindows()
