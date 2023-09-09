
import cv2
import numpy as np

<<<< UPDATED
import cv2
import numpy as np

def blur_faces_in_video(input_video_path, output_video_path):
    # Load the face detector
    face_cascade = cv2.CascadeClassifier('path/to/new_model.xml')

    # Open the input video file
    input_video = cv2.VideoCapture(input_video_path)

    # Get the video's width, height, and frames per second (fps)
    width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = input_video.get(cv2.CAP_PROP_FPS)

    # Create the output video file
    output_video = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    while True:
        # Read the next frame from the input video
        ret, frame = input_video.read()

        # If the frame was not read correctly, then we have reached the end of the video
        if not ret:
            break

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the grayscale frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # For each detected face
        for (x, y, w, h) in faces:
            # Extract the face region from the frame
            face_region = frame[y:y+h, x:x+w]

            # Apply a blur effect to the face region
            blurred_face = cv2.blur(face_region, (99, 99))

            # Replace the face region in the frame with the blurred face
            frame[y:y+h, x:x+w] = blurred_face

        # Write the modified frame to the output video
        output_video.write(frame)

    # Release the input and output video files
    input_video.release()
    output_video.release()
