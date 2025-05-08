# Face Recognition Service

A CPU-optimized face recognition service with a modern web interface. This service allows you to register faces and recognize them in new images.

## Features

- Face registration with name association
- Face recognition with confidence scores
- Modern web interface
- CPU-optimized face recognition
- SQLite database for face storage
- RESTful API endpoints
- Docker support for easy deployment

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Docker and Docker Compose (for containerized deployment)

## Installation

### Option 1: Local Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

### Option 2: Docker Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Build and start the containers:
```bash
docker-compose up --build
```

## Usage

### Local Installation

1. Start the backend server:
```bash
python app.py
```
The server will start on `http://localhost:8000`

2. Open the web interface:
- Open `static/index.html` in your web browser
- Or serve it using a simple HTTP server:
```bash
python -m http.server 8080
```
Then visit `http://localhost:8080/static/index.html`

### Docker Installation

The service will be available at:
- Backend API: `http://localhost:8000`
- Web Interface: `http://localhost:8080`

To stop the service:
```bash
docker-compose down
```

## API Endpoints

### Register a Face
- **URL**: `/register`
- **Method**: `POST`
- **Parameters**:
  - `name`: Person's name (string)
  - `file`: Image file containing the face
- **Response**: JSON with status and message

### Recognize a Face
- **URL**: `/recognize`
- **Method**: `POST`
- **Parameters**:
  - `file`: Image file containing the face to recognize
- **Response**: JSON with status, name, and confidence score

## Technical Details

- Uses `face_recognition` library for face detection and recognition
- Optimized for CPU-only operation
- Uses SQLite for face data storage
- Implements a confidence threshold for face matching
- Supports various image formats (JPEG, PNG, etc.)
- Containerized with Docker for easy deployment

## Notes

- The face recognition threshold is set to 0.6 (can be adjusted in the code)
- The service stores face encodings in a SQLite database
- The web interface is built with HTML, JavaScript, and Tailwind CSS
- CORS is enabled for all origins (can be restricted in production)
- Docker volumes are used to persist the database and static files

## License

MIT License 