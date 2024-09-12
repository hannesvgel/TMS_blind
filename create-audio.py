import os
from pathlib import Path
from openai import OpenAI

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
    10: "You are at th end of the T.M.S. fair area. Right is the hallway with exit and toilets.",
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
directions = ["left", "straight ahead", "right"]
distances = [1, 2, 3, 4, 5]

audio_dir = "audios"
if os.path.exists(audio_dir):
    for file in os.listdir(audio_dir):
        os.remove(os.path.join(audio_dir, file))
    os.rmdir(audio_dir)
os.makedirs(audio_dir, exist_ok=True)

instructions = {}
for location_id, description in locations.items():
    # If both {direction} and {distance} exist in the description
    if "{direction}" in description and "{distance}" in description:
        for direction in directions:
            for distance in distances:
                unit = "meter" if distance == 1 else "meters"
                instruction = description.format(
                    direction=direction, distance=distance, unit=unit
                )
                instructions[f"{location_id}_{direction}_{distance}"] = instruction

    # If only {direction} exists in the description
    elif "{direction}" in description:
        for direction in directions:
            instruction = description.format(direction=direction)
            instructions[f"{location_id}_{direction}_X"] = instruction

    # If only {distance} exists in the description (if applicable)
    elif "{distance}" in description:
        for distance in distances:
            unit = "meter" if distance == 1 else "meters"
            instruction = description.format(distance=distance, unit=unit)
            instructions[f"{location_id}_X:_{distance}"] = instruction

    else:
        instruction = description
        instructions[f"{location_id}_X_X"] = instruction

api_key = "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"
client = OpenAI(api_key=api_key)


def generate_audio_file(text, file_name):
    speech_file_path = Path(__file__).parent / f"{file_name}.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )
    response.stream_to_file(speech_file_path)


for key, instruction in instructions.items():
    print(
        f"({list(instructions.keys()).index(key) + 1}/{len(instructions)}) {key}: {instruction}"
    )
    generate_audio_file(instruction, os.path.join(audio_dir, key))
