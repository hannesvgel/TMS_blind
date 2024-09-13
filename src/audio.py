import os
from subprocess import Popen


def play_audio_async(marker_id, marker_text, direction, distance):
    print("play_audio_async")
    directionStr = "X"
    distanceStr = "X"
    if "{direction}" in marker_text:
        directionStr = "left" if direction < 0 else "right"
    if "{distance}" in marker_text:
        if distance < 350:
            distanceStr = 3
        if distance < 250:
            distanceStr = 2
        if distance < 150:
            distanceStr = 1
    file_name = f"{str(marker_id)}_{directionStr}_{distanceStr}.mp3"
    print(file_name)

    audios_folder_path = "/home/raspberry/Desktop/TMS_blind/audios"
    print(audios_folder_path)

    file_path = os.path.join(audios_folder_path, file_name)
    print(file_path)

    # p = Popen(["mpg321", file_path]) # async / non-blocking
    os.system(f"mpg321 {file_path}")  # sync / blocking
    print("play_audio_async done")
