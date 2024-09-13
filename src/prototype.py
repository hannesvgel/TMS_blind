import cv2
import cv2.aruco as aruco
import numpy as np
import pyttsx3

from audio import play_audio_async
from create_audio import markers

# Load calibrated data
calib_data_path = (
    r"/home/raspberry/Desktop/TMS_blind/camera_calibration/calib_data/MultiMatrix.npz"
)
calib_data = np.load(calib_data_path)


MARKER_SIZE = 14  # centimeters, length of marker in real life
# MARKER_SIZE = 6  # centimeters, length of marker in real life

# Initialise camera matrix and distance coefficient
cam_mat = calib_data["camMatrix"]
dist_coef = calib_data["distCoef"]
r_vectors = calib_data["rVector"]
t_vectors = calib_data["tVector"]

"""# Another initialisation
camera_matrix = cam_mat
dist_coeffs = dist_coef"""

# Initialize the TTS engine
engine = pyttsx3.init()
# engine.setProperty(
#'voice',
# r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'
# )
# engine.setProperty('rate', 60)


engine.setProperty("voice", "english_rp+f3")

last_marker_id = 9999
distance = 0

# Create a lock for thread-safe TTS
# tts_lock = threading.Lock()

# aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50) # old
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

# Start Video capture
# cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)  # Laptop Webcam
cap = cv2.VideoCapture(0)  # USB Webcam


# %%
def speak_text(text):
    """Function to run the TTS in a separate thread."""
    """with tts_lock:
        engine.say(text)
        engine.runAndWait()"""
    engine.say(text)
    engine.runAndWait()


# %%
# Function to display distance
def display_distance(marker_corners, marker_IDs, reject):
    i = 0
    distance = 0
    tVec = [[[0, 0, 0]]]

    # Display distance
    if marker_corners:
        rVec, tVec, _ = aruco.estimatePoseSingleMarkers(
            marker_corners, MARKER_SIZE, cam_mat, dist_coef
        )
        total_markers = range(0, marker_IDs.size)
        for ids, corners, i in zip(marker_IDs, marker_corners, total_markers):
            cv2.polylines(
                frame, [corners.astype(np.int32)], True, (0, 255, 255), 4, cv2.LINE_AA
            )
            corners = corners.reshape(4, 2)
            corners = corners.astype(int)
            top_right = corners[0].ravel()
            top_left = corners[1].ravel()
            bottom_right = corners[2].ravel()
            bottom_left = corners[3].ravel()

            # Calculating the distance
            distance = np.sqrt(
                tVec[i][0][2] ** 2 + tVec[i][0][0] ** 2 + tVec[i][0][1] ** 2
            )

            # Draw the pose of the marker
            point = cv2.drawFrameAxes(frame, cam_mat, dist_coef, rVec[i], tVec[i], 4, 4)
            cv2.putText(
                frame,
                f"id: {ids[0]} Dist: {round(distance, 2)}",
                top_right,
                cv2.FONT_HERSHEY_PLAIN,
                1.3,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame,
                f"x:{round(tVec[i][0][0], 1)} y: {round(tVec[i][0][1], 1)} ",
                bottom_right,
                cv2.FONT_HERSHEY_PLAIN,
                1.0,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )
            # print(ids, "  ", corners)
    # cv2.imshow("frame", frame)
    return distance, tVec[i][0][0]
    # return distance


# %%
# Function to detect ArUco markers & read them out
def detect_aruco(corners, ids, rejected, last_marker_id, distance, x_pos):
    # def detect_aruco(corners, ids, rejected, last_marker_id, distance):
    if ids is not None:
        aruco.drawDetectedMarkers(frame, corners)

        for i in range(len(ids)):
            # Draw the detected markers
            aruco.drawDetectedMarkers(frame, [corners[i]])

            # Get the message from the dictionary using the marker ID
            marker_id = ids[i][0]
            if marker_id != last_marker_id:
                if marker_id in arucodict_speech:
                    # Check if the marker has changed before speaking

                    # Split the text into multiple lines
                    text = arucodict_speech[marker_id].split("\n")

                    # Display each line separately
                    for j, line in enumerate(text):
                        cv2.putText(
                            frame,
                            line,
                            (10, 30 + (i * 100) + (j * 30)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            2,
                        )

                    if distance < 300:
                        if marker_id != last_marker_id:
                            # tts_thread = threading.Thread(target=speak_text, args=(arucodict_speech[marker_id] + "rechts in ZZZZZ",))
                            # tts_thread = threading.Thread(target=speak_text, args=(arucodict_speech[marker_id],))
                            # tts_thread.start()
                            # speak_text(arucodict_speech[marker_id])
                            marker_text = markers[marker_id]
                            play_audio_async(marker_id, marker_text, x_pos, distance)

                    else:
                        print("Distance is too big")
            last_marker_id = marker_id

    return last_marker_id


# %%
while True:
    ret, frame = cap.read()
    height, width, ret = frame.shape

    # Convert picture to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Setup
    if not ret:
        break

    # Initilisation of Variables - Range detection
    (marker_corners, marker_IDs, reject) = aruco.detectMarkers(
        image=gray, dictionary=aruco_dict, parameters=parameters
    )

    # Initilisation of Variables - Detect ArUco markers
    (corners, ids, rejected) = aruco.detectMarkers(
        image=gray, dictionary=aruco_dict, parameters=parameters
    )

    # Run function display_distance
    (distance, x_pos) = display_distance(marker_corners, marker_IDs, reject)
    # (distance) = display_distance(marker_corners, marker_IDs, reject)

    # Check x_pos orientation
    if x_pos > 0:
        x_pos_orientation = "right"
    else:
        x_pos_orientation = "left"

    # Workaround - Redefine arucodict_speech using newly generated variable 'distance' and 'x_pos'
    arucodict_speech = {
        0: "Entry door of UnternehmerTUM, go straight to enter \n"
        "a second door is approximately 3 steps after the first one, \n"
        "go straight to enter the entry hall",
        1: (
            "You are in the entry hall of UnternehmerTUM: \n"
            "LEFT: hallway to TMS and prototype rooms\n"
            "STRAIGHT: toilets, stairs to TUM Incubator (1st floor), \n"
            "          Venture Labs (2nd floor)"
        ),
        2: f"Lecture Hall 3 is on the {x_pos_orientation} in {round(distance / 100, 2)} meters",
        3: f"Lecture Hall 2 is on the {x_pos_orientation} in {round(distance / 100, 2)} meters",
        4: f"Lecture Hall 1 is on the {x_pos_orientation} in {round(distance / 100, 2)} meters, \n"
        f"door is probably closed",
        5: f"Entrance of Prototype Area ahead in {round(distance / 100, 2)} meters",  # todo: change to fair entry, prototype area=fair
        6: f"You are at the beginning of the TMS Prototyping area: \n"
        f"LEFT: Lecture Hall 1 including the pitch stage \n"
        f"RIGHT: go further into the room",
        7: f"Lecture Hall 1 is ahead in {round(distance / 100, 2)} meters. \n"
        f"The pitch Stage is in there",
        8: f"Check-In desk is on the {x_pos_orientation} in {round(distance / 100, 2)} meters",
        9: f"You are in the middle of the prototyping area: \n"
        f"continue straight and then right to go to the hallway, \n"
        f"where you can find the toilets",
        10: f"You are at the end of the prototyping area: \n"
        f"RIGHT: hallway with exit and toilets",
        11: f"The Hallway is straight ahead in {round(distance / 100, 2)} meters.\n"
        f"You can find the toilets here",
        12: f"Exit and stairwell is on the {x_pos_orientation} in {round(distance / 100, 2)} meters",
        13: f"Women's Bathroom is on the {x_pos_orientation} in {round(distance / 100, 2)} meters",
        14: f"Disabled Bathroom is on the {x_pos_orientation} in {round(distance / 100, 2)} meters",
        15: f"Men's Bathroom is on the {x_pos_orientation} in {round(distance / 100, 2)} meters",
        16: f"You are in the entry hall: \n"
        f"RIGHT: seating area, main exit, \n"
        f"       Stairs to Incubator and Venture Labs",
        17: f"The Elevator is on the {x_pos_orientation} in {round(distance / 100, 2)} meters",
        18: f"You are in the middle of the entry hall: \n"
        f"RIGHT: Stairs to Incubator and Venture Labs \n"
        f"LEFT: main exit",
        19: f"You are in the middle of the entry hall: \n"
        f"STRAIGHT AHEAD and then LEFT: Elevator, Stairs to Incubator \n"
        f"                               and Venture Labs \n"
        f"STRAIGHT AHEAD: Hallway including Toilets \n"
        f"RIGHT: Seating Area",
        20: f"The Hallway is straight ahead in {round(distance / 100, 2)} meters.\n"
        f"You can find the toilets here",
        21: f"You are at the end of the prototyping area: \n"
        f"STRAIGHT AHEAD & then LEFT: go deeper in the room, \n"
        f"                             you can find the teams there",
        22: f"You are in the middle of the prototyping area: \n"
        f"continue straight for lecture hall 1 \n"
        f"continue straight and then left to go to the hallway, \n"
        f"where you can find the toilets",
        23: f"You are at the beginning of the TMS Prototyping area: \n"
        f"STRAIGHT: Lecture Hall 1 including the pitch stage \n"
        f"LEFT: Hallway with lecture halls 1-3",
        24: f"The Hallway is straight ahead in {round(distance / 100, 2)} meters.\n"
        f"You can find the lecture halls 1-3 here",
        25: "You are in the entry hall of UnternehmerTUM: \n"  # todo ahead in distance
        "STRAIGHT & then LEFT: Seating Area, Stairs, Elevator and Hallway with Toilets \n"
        "RIGHT: main exit",
        26: f"The main exit is ahead in {round(distance / 100, 2)} meters",
        27: "You are at the entrance of the entry hall. The main exist is straight ahead. \n"
        "Straight and then left is the hallway with lecture halls 1 to 3.",
        28: "You are at the entrance of the entry hall. The main exist is straight ahead. \n"
        "Straight and then left is the hallway with lecture halls 1 to 3.",
        29: "You are at the entrance of the entry hall. The main exist is straight ahead. \n"
        "Straight and then left is the hallway with lecture halls 1 to 3.",
    }

    # Run function detect_aruco
    last_marker_id = detect_aruco(
        corners, ids, rejected, last_marker_id, distance, x_pos
    )
    # detect_aruco(corners, ids, rejected, last_marker_id, distance)

    # Show the frame
    # cv2.imshow('input', frame)

    # Esc key to escape
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
