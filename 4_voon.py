import cv2
import cv2.aruco as aruco
import numpy as np
import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()
last_marker_id = 9999

arucodict = {
    0: "You are at the entry door of UnternehmerTUM, go straight to enter \n"
       "a second door is ahead approx. 3 steps after the first one, go straight to enter",
    1: ("You are in UnternehmerTUM: \n"
        "LEFT: hallway to TMS and prototype rooms\n"
        "STRAIGHT: toilets, stairs to TUM Incubator (1st floor), Venture Labs (2nd floor)"),
    2: "Prototype room 1 is on the left in xy steps",
    3: "Prototype room 2 is on the left in xy steps",
    4: "TMS room 1 is straight ahead",
    5: ("You are in TMS room 1:\n"
        "LEFT: in approx. 4 steps to TMS room 2 (pitch stage)\n"
        "STRAIGHT & RIGHT: enter deeper into the room"),
    6: "Pitch Stage is straight ahead",
    7: "Voon",
    8: "Go straight to find Team 9"
}

# aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50) # old
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

# Define the real-world size of the ArUco marker (e.g., 0.05 meters = 5 cm)
marker_size = 0.05  # Size in meters

# Camera calibration parameters (replace with actual values)
fx = 1248
fy = 1248
cx = 640
cy = 480
k1, k2, p1, p2, k3 = 0.5, 0.5, 0.5, 0.5, 0.5
camera_matrix = np.array([[fx, 0, cx],
                          [0, fy, cy],
                          [0, 0, 1]], dtype=float)
dist_coeffs = np.array([k1, k2, p1, p2, k3])

# Start Video capture
cap = cv2.VideoCapture(1 + cv2.CAP_DSHOW)

while True:

    _, frame = cap.read()
    height, width, _ = frame.shape

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect ArUco markers
    (corners, ids, rejected) = aruco.detectMarkers(image=gray, dictionary=aruco_dict, parameters=parameters)

    if ids is not None:
        aruco.drawDetectedMarkers(frame, corners)

        # Estimate the pose of each marker
        # rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_size, camera_matrix, dist_coeffs)

        for i in range(len(ids)):
            # Draw the detected markers
            aruco.drawDetectedMarkers(frame, [corners[i]])

            # Get the message from the dictionary using the marker ID
            marker_id = ids[i][0]
            if marker_id in arucodict:
                # Split the text into multiple lines
                text = arucodict[marker_id].split('\n')

                # Display each line separately
                for j, line in enumerate(text):
                    cv2.putText(frame, line, (10, 30 + (i * 100) + (j * 30)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # Check if the marker has changed before speaking
                if marker_id != last_marker_id:
                    # Speak out the message associated with the current marker
                    engine.say(arucodict[marker_id])
                    engine.runAndWait()
                    # Update the last detected marker ID
                    last_marker_id = marker_id

    # Show the frame
    cv2.imshow('input', frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()
