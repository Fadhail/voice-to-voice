FROM python:3.9-slim

# Install dependencies sistem (FFmpeg sangat penting untuk Whisper)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements dan install library python
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh file aplikasi
COPY app/ .

# Ekspos port Streamlit
EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]