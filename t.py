from app.routes import *

employee_id = "1111"
if employee_id in registered_faces:
    face_encoding = registered_faces[employee_id]
    print("Face encoding for employee ID 1111:", face_encoding)
else:
    print("Employee ID 1111 not found in registered_faces dictionary")

print(registered_faces)