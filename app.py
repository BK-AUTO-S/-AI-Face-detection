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
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL connection - using existing system database
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "PlLcIne8Syc9e28KSioAeA/Vzz8="
POSTGRES_DB = "postgres"
POSTGRES_HOST = "host.docker.internal"  # This allows Docker to connect to host machine's PostgreSQL

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Face model
class Face(Base):
    __tablename__ = "faces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    encoding = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
        db = SessionLocal()
        known_faces = db.query(Face).all()
        
        best_match = None
        best_match_distance = float('inf')
        
        for face in known_faces:
            stored_encoding = np.array(json.loads(face.encoding))
            distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
            
            if distance < best_match_distance:
                best_match_distance = distance
                best_match = face.name
        
        db.close()
        
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
        db = SessionLocal()
        new_face = Face(
            name=name,
            encoding=json.dumps(face_encoding.tolist())
        )
        db.add(new_face)
        db.commit()
        db.close()
        
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