FROM python:3.11-slim

# Install system dependencies for Tesseract, OpenCV, PDF libs
RUN apt-get update && apt-get install -y \
    build-essential \
    libsm6 libxext6 libxrender-dev \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model (adjust if you use a larger one)
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
