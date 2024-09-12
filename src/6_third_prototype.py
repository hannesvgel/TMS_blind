'''
Hard-coded to provide audio cue using pre-generated mp3 voice files
'''
import cv2
import cv2.aruco as aruco
import numpy as np
import pyttsx3
import threading
from playsound import playsound
import os
import time

#%%
# Initilisation and setups

arucodict_speech = []

# Location array
locations = {
    0: "{direction} in {distance} {unit} is the entry door to Entrepreneurship Center. A second door is approximately 3 steps after the first one. Go straight to enter the entry hall.",
    1: "You are in the entry hall of of the Entrepreneurship Center. Left are the hallway to Think Make Start and prototype rooms. Straight are the toilets, stairs to TUM Incubator (1st floor), and Venture Labs (2nd floor).",
    2: "Lecture hall 3 is on the {direction} in {distance} {unit}.",
    3: "Lecture hall 2 is on the {direction} in {distance} {unit}.",
    4: "Lecture hall 1 is on the {direction} in {distance} {unit}. The door is probably closed.",
    5: "The entrance of T.M.S. fair is ahead in {distance} {unit}.",
    6: "You are in the T.M.S. fair area. Left is lecture hall 1 including the pitch stage. Right is the further part of the room.",
    7: "Lecture hall 1 is ahead in {distance} {unit}. The pitch stage is in there.",
    8: "The check-in desk is on the {direction} in {distance} {unit}.",
    9: "You are in the middle of the T.M.S. fair area. Continue straight and then right to go to the hallway, where you can find the toilets.",
    10: "You are at the end of the T.M.S. fair area. Right is the hallway with exit and toilets.",
    11: "The hallway is straight ahead in {distance} {unit}. You can find the toilets here.",
    12: "Exit and stairwell are on the {direction} in {distance} {unit}.",
    13: "Women's bathroom is on the {direction} in {distance} {unit}.",
    14: "Disabled bathroom is on the {direction} in {distance} {unit}.",
    15: "Men's bathroom is on the {direction} in {distance} {unit}.",
    16: "You are in the entry hall: Right are the seating area, elevator, main exit, and stairs to the incubator and Venture Labs.",
    17: "The elevator is on the {direction} in {distance} {unit}.",
    18: "You are in the middle of the entry hall: On the right are the elevator, stairs to the incubator and Venture Labs. Straight ahead and slightly left is the main exit.",
    19: "You are in the middle of the entry hall: Straight ahead and then left are the elevator, stairs to incubator and Venture Labs. Straight ahead is the hallway including toilets. Straight ahead and slightly right is the seating area.",
    20: "The hallway is straight ahead in {distance} {unit}. You can find the toilets here.",
    21: "You are at the end of the T.M.S. fair area: Straight and then left you can go deeper in the room, you can find the teams there.",
    22: "You are in the middle of the T.M.S. fair area: Continue straight for lecture hall 1. Continue straight and then left to go to the hallway.",
    23: "You are at the beginning of the T.M.S. fair area: Straight is lecture hall 1 including the pitch stage. Straight and then left is the hallway with lecture halls 1 to 3.",
    24: "The hallway is straight ahead in {distance} {unit}. You can find the lecture halls 1 to 3 here.",
    25: "The entry hall of UnternehmerTUM is ahead in {distance} {unit}: Inside on the left are the seating area, stairs, elevator and hallway with toilets. On the right is the main exit.",
    26: "The main exit is on the {direction} in {distance} {unit}.",
    27: "You are at the entrance of the entry hall. The main exist is straight ahead. Straight and then left is the hallway with lecture halls 1 to 3.",
}

# Load calibrated data
calib_data_path = "C:/Users/hianz/Documents/git/TMS_blind/TMS_blind/camera_calibration/calib_data/MultiMatrix.npz"
calib_data = np.load(calib_data_path)

# Audio files pathways
# audio_clip_folder = "C:/Users/hianz/Documents/git/TMS_blind/TMS_blind/audio_clip"
# audio_clip_folder = "C:/Users/hianz/Documents/git/TMS_blind/TMS_blind/audios"
#audio_clip_folder = r"C:\Users\hianz\Documents\git\TMS_blind\TMS_blind\audios"

MARKER_SIZE = 14  # centimeters, length of marker in real life
# MARKER_SIZE = 6  # centimeters, length of marker in real life

# Initialise camera matrix and distance coefficient
cam_mat = calib_data["camMatrix"]
dist_coef = calib_data["distCoef"]
r_vectors = calib_data["rVector"]
t_vectors = calib_data["tVector"]

# Another initialisation
camera_matrix = cam_mat
dist_coeffs = dist_coef

last_marker_id = 9999
distance = 0
x_pos_orientation = "left"  # default
delay_time = 1  # in seconds; delay after playing every audio

# Wegweise marker_id
#global wegweise_marker_id
#wegweise_marker_id = []
# wegweise_marker_id = [0,1,6,9,10,16,18,19,21,22,23,25,27]

# aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50) # old
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

# Start Video capture
# cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)  # Laptop Webcam
cap = cv2.VideoCapture(1 + cv2.CAP_DSHOW)  # USB Webcam

# %%
# Initialize the TTS engine
#engine = pyttsx3.init()
# engine.setProperty(
#     'voice',
#     r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'
# )

#engine.setProperty(
    #'voice',
    #'english_rp+f3'
#)

# %%
# def speak_text(text):
    # """Function to run the TTS in a separate thread."""
    # engine.say(text)
    # engine.runAndWait()
    # engine.setProperty('rate', 30)


# %%
# Function to play audio files
# def audio_play(audio_path):
#     playsound(audio_path)

# %%
# Function to display distance
def display_distance(marker_corners, marker_IDs, reject):
   i = 0
   distance = 0 
   tVec = [[[0,0,0]]]
   
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
               f"x:{round(tVec[i][0][0],1)} y: {round(tVec[i][0][1],1)} ",
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
    print("detect_aruco")
# def detect_aruco(corners, ids, rejected, last_marker_id, distance):
    
    if ids is not None:
        aruco.drawDetectedMarkers(frame, corners)
        
        '''# Estimate the pose of each marker
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_size, camera_matrix, dist_coeffs)'''
        
        for i in range(len(ids)):
            # Draw the detected markers
            aruco.drawDetectedMarkers(frame, [corners[i]])
    
            # Get the message from the dictionary using the marker ID
            marker_id = ids[i][0]
            if marker_id in arucodict_speech:
                # Split the text into multiple lines
                text = arucodict_speech[marker_id].split('\n')
    
                # Display each line separately
                for j, line in enumerate(text):
                    cv2.putText(frame, line, (10, 30 + (i * 100) + (j * 30)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                (255, 255, 255), 2)
    
                # Check if the marker has changed before speaking
                # if marker_id == last_marker_id:
                if marker_id != last_marker_id:  # old
                        
                    try:
                        print("test")
                        directionStr = "X"
                        distanceStr = "X"
                        
                        if marker_id in locations:
                            description = locations[marker_id]
                            print(description)
                            if "{direction}" in description:
                                directionStr = "left" if x_pos < 0 else "right"
                            if "{distance}" in description:
                                if distance < 300:
                                    distanceStr = 3
                                if distance < 200:
                                    distanceStr = 2
                                if distance < 100:
                                    distanceStr = 1
                            print(directionStr, distanceStr)
                            print(f"{str(marker_id)}_{directionStr}_{distanceStr}.mp3")
                            audio_clip_folder = os.path.join(os.getcwd(), "../audios")
                            print(audio_clip_folder)
                            current_audio_path = os.path.join(audio_clip_folder, f"{str(marker_id)}_{directionStr}_{distanceStr}.mp3")
                            playsound(current_audio_path)
                            time.sleep(delay_time)
                                    
                    except:
                        print("Error: Distance is not defined or audio file does not exist!")

#%%
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
    
    # Run function detect_aruco & play audio
    # last_marker_id_temp = detect_aruco(corners, ids, rejected, last_marker_id, distance, x_pos)
    detect_aruco(corners, ids, rejected, last_marker_id, distance, x_pos)
    # detect_aruco(corners, ids, rejected, last_marker_id, distance)
    
    # last_marker_id = last_marker_id_temp
    
    # Show the frame
    cv2.imshow('input', frame)
    
    # Esc key to escape
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
