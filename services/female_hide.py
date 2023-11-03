
from moviepy.editor import *
import os
from deepface import DeepFace
import cv2
import numpy as np
def blur_female_faces(video_path):
    # Load the video clip
    video_clip = VideoFileClip(video_path)

    # Initialize an empty list to store the processed frames
    processed_frames = []
# Define the video writer
    output_path = 'output_video_blurred.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
    # Iterate over the frames of the video
    for frame in video_clip.iter_frames():
        # Use DeepFace to detect faces and their genders in the frame
        
        results = DeepFace.analyze(frame, actions=['gender'], enforce_detection=False)

        # Iterate over the detected faces
        for result in results:
            # If the face is identified as female, blur it
            if result['dominant_gender'] == 'Man':
                frame = blur_face(frame, result['region'])

        # Add the processed frame to the list
        processed_frames.append(frame)

    # Combine the processed frames into a new video
    new_video = concatenate_videoclips(processed_frames)

    # Save the new video to a file and return its path
    new_video_path = video_path.replace('.mp4', '_blurred.mp4')
    new_video.write_videofile(new_video_path)

    return new_video_path
def blur_face(frame, region):
    # Convert the frame to a format suitable for processing with cv2
    frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

    # Extract the region from the frame
    x=region['x']
    y=region['y']
    h=region['h']
    w=region['w']

    face = frame[y:y+h, x:x+w]

    # Apply a blur effect to the face
    blurred_face = cv2.GaussianBlur(face, (99, 99), 30)

    # Replace the original face in the frame with the blurred face
    frame[y:y+h, x:x+w] = blurred_face

    # Convert the frame back to its original format
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    return frame
blur_female_faces("C:\\FFOutput\\مسجل الشاشة\\مصنع الصيغ مسجل الشاشة20230825_081746.mp4")