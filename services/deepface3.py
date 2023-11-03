from deepface import DeepFace
import cv2

# Load the video capture
video_path =  "F:\\Ahmed\\lab\\scripts\\NoMusic\\cleanvedio\\final\\الحروب الصيلبية - 1 الصدمة.mp4"
cap = cv2.VideoCapture(video_path)
fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

# Define the video writer
output_path = 'output_video_blurred4.mp4'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

# Process each frame
i=0
while cap.isOpened():
    # i+=1
    # if i>20:
    #     break
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert the frame from BGR to RGB
    # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Analyze faces using DeepFace
    analyzed_faces = DeepFace.analyze(frame, actions=['gender'],enforce_detection=False)
    
    for face in analyzed_faces:
        region=face['region']
        x=region['x']
        y=region['y']
        h=region['h']
        w=region['w']
        gender = face['dominant_gender']
        
        # Blur women's faces
        if gender == 'Man' and x!=0:
            face_roi = frame[y:y+h, x:x+w]
            blurred_face = cv2.GaussianBlur(face_roi, (99, 99), 30)
            frame[y:y+h, x:x+w] = blurred_face
    
    # Convert the frame back from RGB to BGR
    # frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
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