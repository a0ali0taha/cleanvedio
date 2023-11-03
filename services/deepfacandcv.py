from deepface import DeepFace
import cv2

# Load the pre-trained face detection model from OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load the video capture
video_path =  "C:\\FFOutput\\مسجل الشاشة\\مصنع الصيغ مسجل الشاشة20230825_081746.mp4"
cap = cv2.VideoCapture(video_path)
fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

# Define the video writer
output_path = 'output_video_blurred.mp4'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

# Process each frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces using OpenCV
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    for r in faces:
        x=r[0]
        y=r[1]
        w=r[2]
        h=r[3]
        face_roi = frame[y:y+h, x:x+w]
        
        # Convert the face region from BGR to RGB
        face_rgb = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
        
        # Analyze face attributes using DeepFace
        analyzed_face = DeepFace.analyze(face_rgb, actions=['gender'],enforce_detection=False)
        gender = analyzed_face['gender']
        
        # Blur women's faces
        if gender == 'Woman':
            blurred_face = cv2.GaussianBlur(face_roi, (99, 99), 30)
            frame[y:y+h, x:x+w] = blurred_face
    
    # Write the frame with processed faces
    out.write(frame)
    
    # Display the processed frame
    cv2.imshow('Processed Video', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and writer
cap.release()
out.release()
cv2.destroyAllWindows()
