import cv2
import numpy as np

# Set the dictionary for ArUco markers
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

# Create and save 3 ArUco markers
for i in range(30):

    marker_image = np.zeros((400, 400), dtype=np.uint8)
    marker_image = cv2.aruco.generateImageMarker(aruco_dict, i, 400, marker_image, 1)

    # Save the marker to a file
    filename = f"aruco_marker_{i}.png"
    cv2.imwrite(filename, marker_image)
    print(f"Marker {i} saved as {filename}")

    '''# Optionally display the marker
    cv2.imshow(f"Marker {i}", marker_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()'''
