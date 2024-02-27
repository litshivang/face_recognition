# app/routes.py

import io
import face_recognition  # Import face_recognition library for face recognition tasks
from flask import request, jsonify
from app import app, db
from app.models import User
import os
from werkzeug.utils import secure_filename
import numpy as np

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['POST'])
def register_face():
    # Extract data from the request
    data = request.form
    employee_id = data.get('employee_id')
    name = data.get('name')
    image = request.files['image']  # Get the image file from the request
    
    # Check if the required fields are present in the request body
    if not employee_id or not name or not image:
        return jsonify({'error': 'Employee ID, name, and image are required'}), 400

    # Read the image data as bytes
    image_bytes = image.read()
    
    # Convert the image bytes to a numpy array
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)

    # Load the image and extract face encodings
    try:
        face_image = face_recognition.load_image_file(io.BytesIO(image_array))
        face_locations = face_recognition.face_locations(face_image)
        if len(face_locations) != 1:
            return jsonify({'error': 'Expected one face in the image, found {}'.format(len(face_locations))}), 400
        
        face_encodings = face_recognition.face_encodings(face_image, face_locations)[0]
    except Exception as e:
        return jsonify({'error': 'Failed to extract face encodings. {}'.format(str(e))}), 500

    # Check if a user with the same employee ID already exists
    existing_user = User.query.filter_by(employee_id=employee_id).first()
    if existing_user:
        return jsonify({'error': 'User with the same employee ID already exists'}), 409

    # Check if a user with the same name already exists
    existing_user_name = User.query.filter_by(name=name).first()
    if existing_user_name:
        return jsonify({'error': 'User with the same name already exists'}), 409

    # Check if a user with the same face encoding already exists
    existing_user_face = User.query.filter_by(face_encoding=face_encodings).first()
    if existing_user_face:
        return jsonify({'error': 'User with the same face encoding already exists'}), 409

    # Create a new user
    new_user = User(employee_id=employee_id, name=name, face_encoding=face_encodings)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Face registered successfully'}), 201

@app.route('/authenticate', methods=['POST'])
def authenticate_face():
    # Check if the POST request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']

    # Check if the file is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Check if the file has an allowed extension
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file extension. Allowed extensions: png, jpg, jpeg'}), 400

    # Read the file as bytes
    image_bytes = file.read()

    # Convert the image bytes to a numpy array
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)

    # Load the image and extract face encodings
    try:
        face_image = face_recognition.load_image_file(io.BytesIO(image_array))
        face_locations = face_recognition.face_locations(face_image)
        if len(face_locations) != 1:
            return jsonify({'error': 'Expected one face in the image, found {}'.format(len(face_locations))}), 400
        
        face_encodings = face_recognition.face_encodings(face_image, face_locations)[0]
    except Exception as e:
        return jsonify({'error': 'Failed to extract face encodings. {}'.format(str(e))}), 500

    # Retrieve users from the database
    users = User.query.all()

    # Implement face recognition logic
    authenticated_users = []
    for user in users:
        # Compare face encodings to check for a match
        if match_face_encoding(user.face_encoding, face_encodings):
            authenticated_users.append({'employee_id': user.employee_id, 'name': user.name})

    # Return the authenticated users
    if authenticated_users:
        return jsonify({'authenticated_users': authenticated_users}), 200
    else:
        return jsonify({'message': 'No user found for the provided face encoding'}), 404

def match_face_encoding(saved_encoding, new_encoding):
    # Implement logic to compare face encodings and determine if they match
    # This could be using a face recognition library like face_recognition
    # For simplicity, we assume a match if the encodings are equal
    return (saved_encoding == new_encoding).all()  # Use .all() to compare all elements of the array