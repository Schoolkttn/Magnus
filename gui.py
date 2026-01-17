import face_recognition
import cv2
import numpy as np
from vector import VectorWriter
import os

# Initialize vector writer
output_file = os.path.expanduser("~/.local/share/vector_data/vector.json")
vector_writer = VectorWriter(output_file)

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
known_image = face_recognition.load_image_file("known.jpg")
known_face_encoding = face_recognition.face_encodings(known_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    known_face_encoding,
]
known_face_names = [
    "Known"
]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# Get frame dimensions for calculating vectors (calculated once)
ret, frame = video_capture.read()
frame_height, frame_width = frame.shape[:2]
frame_center_x = frame_width / 2
frame_center_y = frame_height / 2

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Only process every other frame of video to save time
    if process_this_frame:
        # Resize frame of video to 1/4 size for faster face recognition processing
        # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        small_frame = frame

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)
    process_this_frame = not process_this_frame

        # Output vectors towards known faces (only when face detection runs)
    # Collect all vectors for JSON output
    vectors = []
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 1
        right *= 1
        bottom *= 1
        left *= 1

        # Calculate the center of the face
        face_center_x = (left + right) / 2
        face_center_y = (top + bottom) / 2

        # Calculate vector from frame center to face center
        vector_x = frame_center_x - face_center_x
        vector_y = frame_center_y - face_center_y

        # Calculate magnitude (distance)
        magnitude = np.sqrt(vector_x**2 + vector_y**2)
        
        # Add vector to list
        vectors.append({
            "x": float(-vector_x),
            "y": float(vector_y),
            "name": name,
            "magnitude": float(magnitude),
        })

        # Output the vector information
        print(f"Face '{name}' detected:")
        print(f"  Position: ({face_center_x:.1f}, {face_center_y:.1f})")
        print(f"  Vector from center: ({vector_x:.1f}, {vector_y:.1f})")
        print(f"  Center: ({frame_center_x:.1f}, {frame_center_y:.1f})")
        print(f"  Distance from center: {magnitude:.1f} pixels")
        print()
        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    
    # Write all vectors to JSON file
    if vectors:
        vector_writer.write_vectors(vectors)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()