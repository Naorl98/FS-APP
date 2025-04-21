FROM python:3.10-slim

# Install OS dependencies including OpenGL
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (for Railway)
ENV PORT=5050
EXPOSE 5050

# Start the Flask app
CMD ["python", "app.py"]
