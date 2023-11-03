import cv2
from deepface import DeepFace
import numpy as np
# Load the video capture
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


video_path = "C:\\FFOutput\\مسجل الشاشة\\مصنع الصيغ مسجل الشاشة20230825_081746.mp4"
cap = cv2.VideoCapture(video_path)
fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

# Define the video writer
output_path = 'output_video_blurred2.mp4'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

# Process each frame
i = 0
while cap.isOpened():
    i+=1
    if i>50:
        break
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detect faces using DeepFace
    results = DeepFace.analyze(frame, actions=['gender'], enforce_detection=False)
    # results = DeepFace.detectFace(frame, detector_backend='opencv',enforce_detection=False)
    
    for face in results:
        if face['dominant_gender'] == 'Man':
            frame= blur_face(frame,face['region'])




    
    # Write the frame with processed faces
    out.write(frame)
    
    # Display the processed frame
    # cv2.imshow('Processed Video', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and writer
cap.release()
out.release()
cv2.destroyAllWindows()