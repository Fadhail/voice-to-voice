FROM python:3.9-slim

# Install dependencies sistem (FFmpeg tetap perlu di-install)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- KUNCI OPTIMASI ---
# Salin hanya requirements dulu
COPY app/requirements.txt .

# Install requirements. Docker akan menyimpan (cache) layer ini.
# Selama isi file requirements.txt tidak berubah, Docker tidak akan download ulang.
RUN pip install --no-cache-dir -r requirements.txt

# Baru salin sisa file codingan (main.py, dll)
COPY app/ .

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]