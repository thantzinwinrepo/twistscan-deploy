# TwistScan — multi-stage Docker image
# Stage 1: base dependencies
FROM python:3.12-slim AS base

# System deps for dnstwist (needs libldns for DNS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libldns3 \
    libpcap0.8 \
    whois \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir flask python-dotenv

# Copy application files
COPY twistscan.py .
COPY twistscan-streamlit.py .
COPY app.py .
COPY dictionary-dnstwist.dict .
COPY tld-list.dict .

# Create output directories
RUN mkdir -p screenshots

# Runtime env vars (override with -e or docker-compose)
ENV URLSCAN_API=""
ENV PYTHONUNBUFFERED=1

# Expose Flask dashboard port
EXPOSE 5000

# Default: start the Flask dashboard
# Override CMD to run a scan instead
CMD ["python", "app.py"]
