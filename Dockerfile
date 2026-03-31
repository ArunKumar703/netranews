
# Use Python 3.10 slim for smaller image size
FROM python:3.10-slim

# Install system dependencies for newspaper3k and lxml
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    zlib1g-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data for newspaper3k
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run using uvicorn correctly for Cloud Run (must bind to 0.0.0.0 and PORT env var)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
