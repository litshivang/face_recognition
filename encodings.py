import face_recognition

# Load image file containing the user's face
image_path = 'image.jpg'
image = face_recognition.load_image_file(image_path)

# Detect faces in the image
face_locations = face_recognition.face_locations(image)

# Check if exactly one face is detected
if len(face_locations) != 1:
    print('Exactly one face must be present in the image')
    # Handle this case appropriately
else:
    # Extract face encoding data
    face_encoding = face_recognition.face_encodings(image, known_face_locations=face_locations)[0]
    
    # Now you have the face encoding data for the user
    print('Face encoding:', face_encoding)
    # Store the face encoding data for future use, such as authentication
