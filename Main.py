import face_recognition
import cv2
import numpy as np
from vector import VectorWriter
import os
import time

def initialize_vector_writer():
    """Initialize and return the vector writer."""
    output_file = os.path.expanduser("~/.local/share/vector_data/vector.json")
    return VectorWriter(output_file)

def load_known_faces():
    """Load known faces and return encodings and names."""
    # Load a sample picture and learn how to recognize it.
    known_image = face_recognition.load_image_file("known.jpg")
    known_face_encoding = face_recognition.face_encodings(known_image)[0]
    
    # Create arrays of known face encodings and their names
    known_face_encodings = [known_face_encoding]
    known_face_names = ["Known"]
    
    return known_face_encodings, known_face_names

def initialize_camera(camera_index=0):
    """Initialize and return camera capture object."""
    video_capture = cv2.VideoCapture(camera_index)
    
    # Get frame dimensions for calculating vectors
    ret, frame = video_capture.read()
    if not ret:
        raise RuntimeError("Failed to read from camera")
    
    frame_height, frame_width = frame.shape[:2]
    frame_center_x = frame_width / 2
    frame_center_y = frame_height / 2
    
    return video_capture, frame_center_x, frame_center_y

def capture_and_recognize_faces(video_capture, known_face_encodings, known_face_names, frame_center_x, frame_center_y):
    """Capture a single frame and perform face recognition.
    
    Returns: 
        tuple: (frame, face_locations, face_names, vectors)
    """
    # Grab a single frame of video
    ret, frame = video_capture.read()
    
    if not ret:
        return None, [], [], []
    
    # Resize frame of video to 1/4 size for faster face recognition processing
    # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25) #Skipped because its only called every 1s
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
        
        # Use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        
        face_names.append(name)
    
    # Calculate vectors for all detected faces
    vectors = []
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        
        # Calculate the center of the face
        face_center_x = (left + right) / 2
        face_center_y = (top + bottom) / 2
        
        # Calculate vector from frame center to face center
        vector_x = face_center_x - frame_center_x
        vector_y = frame_center_y - face_center_y
        
        vectors.append({
            'name': name,
            'x': vector_x,
            'y': vector_y,
        })
    
    return frame, face_locations, face_names, vectors

def cleanup_camera(video_capture):
    """Release the camera resource."""
    video_capture.release()
    cv2.destroyAllWindows()

def main():
    """Main function demonstrating usage of the face recognition functions."""
    # Initialize components
    vector_writer = initialize_vector_writer()
    known_face_encodings, known_face_names = load_known_faces()
    video_capture, frame_center_x, frame_center_y = initialize_camera()
    
    try:
        # Example:  Capture and process a single frame
        frame, face_locations, face_names, vectors = capture_and_recognize_faces(
            video_capture, known_face_encodings, known_face_names, frame_center_x, frame_center_y
        )
        
        if frame is not None:
            print(f"Detected {len(face_names)} face(s)")
            for name, vector in zip(face_names, vectors):
                print(f"Face:  {name}, Vector: ({vector['x']:.2f}, {vector['y']:.2f})")
            
            # Write vectors to file if needed
            if vectors:
                vector_writer.write_vectors(vectors)
        
    finally:
        cleanup_camera(video_capture)

if __name__ == "__main__":
    while True:
        main()
        time.sleep(1)