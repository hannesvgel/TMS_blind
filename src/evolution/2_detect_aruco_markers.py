import cv2
import os
import numpy as np

arucodict = {
    0: "You are at the entry door of UnternehmerTUM, go straight to enter, second door ahead",
    1: "left: TMS & pitch stage, straight: toilettes",
    2: "prototype room 1 is on the left",
    3: "prototype room 2 is on the left",
    4: "tms room is straight ahead",
    5: "you are in the tms room, pitch stage is through a door on the left in 4 approx. 4 steps"
}

# Load  predefined dictionary for ArUco markers
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
parameters = cv2.aruco.DetectorParameters()


image_folder = "./arucu_pictures_unternehmnerTUM"

# Loop through all images
for filename in os.listdir(image_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        # Read the image
        img_path = os.path.join(image_folder, filename)
        img = cv2.imread(img_path)

        # Detect ArUco markers in the image
        (corners, ids, rejected) = cv2.aruco.detectMarkers(img, aruco_dict, parameters=parameters)

        # Check if any markers are detected
        if ids is not None:
            for i in range(len(ids)):
                marker_id = ids[i][0]  # Extract marker ID
                if marker_id in arucodict:
                    print(f"Image: {filename}, ArUco ID: {marker_id}, Info: {arucodict[marker_id]}\n")
                else:
                    print(f"Image: {filename}, ArUco ID: {marker_id}, Info: Unknown marker\n")
        else:
            print(f"No ArUco markers detected in {filename}\n")

        '''for candidate in rejected:
            for rect in candidate:
                # Draw a rectangle around rejected candidates
                rect = np.array(rect, dtype=np.int32)
                cv2.polylines(img, [rect], isClosed=True, color=(0, 0, 255), thickness=2)

            # Display the image with detected markers and rejected candidates
        cv2.imshow("Detected ArUco Markers", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()'''
