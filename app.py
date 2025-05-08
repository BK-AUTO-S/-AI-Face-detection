from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import face_recognition
import numpy as np
from PIL import Image
import io
import json
import os
from typing import Optional
import sqlite3
from datetime import datetime

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
def init_db():
    conn = sqlite3.connect('face_database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faces
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  encoding TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def get_face_encoding(image_data):
    try:
        # Convert image data to numpy array
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        
        # Detect face locations
        face_locations = face_recognition.face_locations(image_array)
        
        if not face_locations:
            return None
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        
        if not face_encodings:
            return None
            
        return face_encodings[0]  # Return the first face encoding
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None

@app.post("/recognize")
async def recognize_face(file: UploadFile = File(...)):
    try:
        # Read image data
        contents = await file.read()
        
        # Get face encoding from uploaded image
        face_encoding = get_face_encoding(contents)
        
        if face_encoding is None:
            return JSONResponse(
                content={"status": "error", "message": "No face detected in the image"},
                status_code=400
            )
        
        # Compare with database
        conn = sqlite3.connect('face_database.db')
        c = conn.cursor()
        c.execute("SELECT name, encoding FROM faces")
        known_faces = c.fetchall()
        conn.close()
        
        best_match = None
        best_match_distance = float('inf')
        
        for name, stored_encoding in known_faces:
            stored_encoding = np.array(json.loads(stored_encoding))
            distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
            
            if distance < best_match_distance:
                best_match_distance = distance
                best_match = name
        
        # If the best match is too different, consider it unknown
        if best_match_distance > 0.6:  # Threshold can be adjusted
            return JSONResponse(
                content={"status": "success", "name": "Unknown", "confidence": float(1 - best_match_distance)}
            )
        
        return JSONResponse(
            content={"status": "success", "name": best_match, "confidence": float(1 - best_match_distance)}
        )
        
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )

@app.post("/register")
async def register_face(name: str = Form(...), file: UploadFile = File(...)):
    try:
        contents = await file.read()
        face_encoding = get_face_encoding(contents)
        
        if face_encoding is None:
            return JSONResponse(
                content={"status": "error", "message": "No face detected in the image"},
                status_code=400
            )
        
        # Store in database
        conn = sqlite3.connect('face_database.db')
        c = conn.cursor()
        c.execute("INSERT INTO faces (name, encoding) VALUES (?, ?)",
                 (name, json.dumps(face_encoding.tolist())))
        conn.commit()
        conn.close()
        
        return JSONResponse(
            content={"status": "success", "message": f"Face registered for {name}"}
        )
        
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 