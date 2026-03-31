# -------------------------------
# Stage 1: Build the Reflex Frontend (Heavier)
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

# Install Python dependencies (including Reflex for build)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files for build
COPY . .

# Initialize Reflex and Export the Frontend
# We provide a dummy key during build to prevent GroqError.
RUN GROQ_API_KEY=gsk_build_check_dummy reflex init && \
    GROQ_API_KEY=gsk_build_check_dummy reflex export --frontend-only && \
    mkdir -p /app/static && \
    unzip frontend.zip -d /app/static && \
    rm frontend.zip

# -------------------------------
# Stage 2: Final Production Image (Lean - Under 4GB)
# -------------------------------
FROM python:3.11-slim

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Copy only the necessary Python environment from the builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 2. Copy the pre-built static assets (Frontend) from the builder
COPY --from=builder /app/static ./static

# 3. SURGICAL COPY of the source code (Excludes heavy .web and node_modules)
# This is critical to staying under the 4GB Railway limit.
COPY DOCU_AI/ ./DOCU_AI/
COPY app.py rxconfig.py requirements.txt ./

# 4. Create documents directory for RAG
RUN mkdir -p /app/DOCU_AI/documents

# Railway dynamically assigns $PORT; our app.py listens to it.
EXPOSE 7860

# Launch the unified FastAPI app
# Python 3.11-slim + pruned packages should keep us near 2.5GB.
CMD ["python3", "-m", "uvicorn", "app:api", "--host", "0.0.0.0", "--port", "7860"]
