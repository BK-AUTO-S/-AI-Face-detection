FROM python:3.9-slim

# Install system dependencies required for face_recognition
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libx11-dev \
    libatlas-base-dev \
    libgtk-3-dev \
    libboost-python-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/data /app/static

# Copy the rest of the application
COPY . .

# Set permissions
RUN chmod -R 755 /app

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"] 