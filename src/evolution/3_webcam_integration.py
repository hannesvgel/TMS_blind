import cv2


def capture_from_webcam():
    # Open a connection to the first webcam (usually index 0)
    cap = cv2.VideoCapture(1)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Press 'q' to quit the video feed.")

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # If frame is read correctly, display it
        if ret:
            cv2.imshow('Webcam Feed', frame)
        else:
            print("Error: Could not read frame.")
            break

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close the window
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    capture_from_webcam()
