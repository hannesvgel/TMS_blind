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

#%%
# Initilisation and setups

# Load calibrated data
calib_data_path = "C:/Users/hianz/Documents/git/TMS_blind/TMS_blind/camera_calibration/calib_data/MultiMatrix.npz"
calib_data = np.load(calib_data_path)

# Audio files pathways
audio_clip_folder = "C:/Users/hianz/Documents/git/TMS_blind/TMS_blind/audio_clip"

# MARKER_SIZE = 14  # centimeters, length of marker in real life
MARKER_SIZE = 6  # centimeters, length of marker in real life

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

# aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50) # old
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

# Start Video capture
cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)  # Laptop Webcam
# cap = cv2.VideoCapture(1 + cv2.CAP_DSHOW)  # USB Webcam

# %%
# Initialize the TTS engine
engine = pyttsx3.init()
# engine.setProperty(
#     'voice',
#     r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'
# )

engine.setProperty(
    'voice',
    'english_rp+f3'
)

# %%
def speak_text(text):
    """Function to run the TTS in a separate thread."""
    engine.say(text)
    engine.runAndWait()
    engine.setProperty('rate', 30)


# %%
# Function to play audio files
def audio_play(audio_path):
    playsound(audio_path)

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
                if marker_id != last_marker_id:
                    
                    # Create a separate thread for the TTS so that it doesn't block the camera feed
                    try:
                        if x_pos < 0:  # Camera's POV: Left
                            
                            direction = "left"  # x_pos_orientation
                            
                            if distance < 100: 
                                current_audio_path = os.path.join(audio_clip_folder, str(marker_id) + "_" + direction + "_" + "1" + ".mp3")
                                audio_play(current_audio_path)
                            elif distance < 200:
                                current_audio_path = os.path.join(audio_clip_folder, marker_id + "_" + direction + "_" + "2" + ".mp3")
                                audio_play(current_audio_path)
                            elif distance < 300:
                                current_audio_path = os.path.join(audio_clip_folder, marker_id + "_" + direction + "_" + "3" + ".mp3")
                                audio_play(current_audio_path)
                            elif distance < 400:
                                current_audio_path = os.path.join(audio_clip_folder, marker_id + "_" + direction + "_" + "4" + ".mp3")
                                audio_play(current_audio_path)
                            else: 
                                print("Distance is more than 4 metres.")
                        else:
                            
                            direction = "right"  # x_pos_orientation
                            
                            if distance < 100: 
                                current_audio_path = os.path.join(audio_clip_folder, str(marker_id) + "_" + direction + "_" + "1" + ".mp3")
                                audio_play(current_audio_path)
                            elif distance < 200:
                                current_audio_path = os.path.join(audio_clip_folder, marker_id + "_" + direction + "_" + "2" + ".mp3")
                                audio_play(current_audio_path)
                            elif distance < 300:
                                current_audio_path = os.path.join(audio_clip_folder, marker_id + "_" + direction + "_" + "3" + ".mp3")
                                audio_play(current_audio_path)
                            elif distance < 400:
                                current_audio_path = os.path.join(audio_clip_folder, marker_id + "_" + direction + "_" + "4" + ".mp3")
                                audio_play(current_audio_path)
                            else: 
                                print("Distance is more than 4 metres.")
                                
                    except:
                        print("Error: Distance is not defined.")
                         
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
    
    # Workaround; In 6_third_prototype, it is meant for debugging only - Redefine arucodict_speech using newly generated variable 'distance' and 'x_pos'
    arucodict_speech = {
        
        # Without an artificial '9' in front
        0: "You are at the entry door of UnternehmerTUM, go straight to enter \n"
           "a second door is ahead approx. 3 steps after the first one, \n"
           "go straight to enter",
        1: ("You are in UnternehmerTUM: \n"
            "LEFT: hallway to TMS and prototype rooms\n"
            "STRAIGHT: toilets, stairs to TUM Incubator (1st floor), \n"
            "          Venture Labs (2nd floor)"),
        2: "Prototype room 1 is on the left in xy steps",
        # 3: "Prototype room 2 is on the left in xy steps",
        3: f"Prototype room 2 is on the {x_pos_orientation} in {round(distance/100, 2)} meters",
        # 3: "Prototype room 2 is on the left in " + str(distance) + " steps",
        4: "TMS room 1 is straight ahead",
        5: ("You are in TMS room 1:\n"
            "LEFT: in approx. 4 steps to TMS room 2 (pitch stage)\n"
            "STRAIGHT & RIGHT: enter deeper into the room"),
        6: "Pitch Stage is straight ahead",
        7: "Voon",
        8: "Go straight to find Team 9",
        
        # With an artificial '9' in front
        # Adding a 9 in front of the digits for the opposite direction
        # 92: "Prototype room 1 is on the right in xy steps",
        # 93: "Prototype room 2 is on the right in xy steps",

    }
    
    # Run function detect_aruco & play audio
    detect_aruco(corners, ids, rejected, last_marker_id, distance, x_pos)
    # detect_aruco(corners, ids, rejected, last_marker_id, distance)
    
    # Show the frame
    cv2.imshow('input', frame)
    
    # Esc key to escape
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
