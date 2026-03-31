# -------------------------------
# Stage 1: Build the Reflex Frontend
# -------------------------------
FROM python:3.11-slim AS builder

# Install Node.js, unzip, and other build tools
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Initialize Reflex and Export the Frontend
# We provide a dummy key during build to prevent GroqError.
# We use the standard zip-based export to ensure all assets are captured.
RUN GROQ_API_KEY=gsk_build_check_dummy reflex init && \
    GROQ_API_KEY=gsk_build_check_dummy reflex export --frontend-only && \
    mkdir -p /app/static && \
    unzip frontend.zip -d /app/static && \
    rm frontend.zip

# -------------------------------
# Stage 2: Final Production Image
# -------------------------------
FROM python:3.11-slim

# Install runtime dependencies for PDF/VectorDB processing
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install production Python dependencies
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
# Copy built static assets from Stage 1
COPY --from=builder /app/static ./static

# Ensure common doc directory exists
RUN mkdir -p /app/DOCU_AI/documents

# Railway will provide the $PORT env var dynamically.
# Our app.py already detects this.
EXPOSE 7860

# Launch unified FastAPI app with dynamic port detection
# This satisfies the single-port requirement and build-time resilience.
CMD ["python3", "-m", "uvicorn", "app:api", "--host", "0.0.0.0", "--port", "7860"]
