FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/requirements.txt .

RUN python -m venv /opt/venv

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
ENV PIP_DEFAULT_TIMEOUT=120

RUN /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install --no-cache-dir --timeout 120 --retries 5 -r requirements.txt

COPY app/ .

EXPOSE 8501

CMD ["/opt/venv/bin/python", "-m", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]