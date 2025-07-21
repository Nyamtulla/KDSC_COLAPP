FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
# Install system dependencies: tesseract-ocr and curl (for Ollama)
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python", "-m", "rq.cli", "worker", "-w", "rq.SimpleWorker"] 