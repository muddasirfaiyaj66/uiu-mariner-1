import cv2
import os

# Folder where the captured images are stored
input_folder = '/home/mdkfahim30/360image/Basic360/img/captured_frames'
output_folder = '/home/mdkfahim30/360image/Basic360/img'

# Get all the image filenames in the folder
image_files = [f for f in os.listdir(input_folder) if f.endswith('.jpg')]

# Sort the image filenames (optional, but helps if you want to preserve the order)
image_files.sort()

# List to store the images
images = []

# Load all images
for filename in image_files:
    img_path = os.path.join(input_folder, filename)
    image = cv2.imread(img_path)
    
    if image is None:
        print(f"Failed to load image: {img_path}")
        continue
    
    images.append(image)

# Check if there are enough images to stitch
if len(images) < 2:
    print("Error: At least 2 images are required for stitching.")
    exit(1)

# Initialize the OpenCV stitcher
stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)

# Perform the stitching
status, pano = stitcher.stitch(images)

# Check if stitching was successful
if status == cv2.Stitcher_OK:
    # Save the panorama
    pano_path = os.path.join(output_folder, 'stitched_panorama.jpg')
    cv2.imwrite(pano_path, pano)
    print(f"Panorama saved at: {pano_path}")
    
    # Display the panorama
    cv2.imshow('Panorama', pano)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print(f"Stitching failed with error code: {status}")
