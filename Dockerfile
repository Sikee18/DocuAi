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
# This creates the static assets for the single-port deployment.
RUN reflex init && \
    reflex export --frontend-only --no-zip && \
    mkdir -p /app/static && \
    mv .web/_static/* /app/static/ || cp -r .web/_static/. /app/static/

# -------------------------------
# Stage 2: Final Production Image
# -------------------------------
FROM python:3.11-slim

# Install runtime dependencies (e.g. system libraries for vector DBs)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create a non-root user for Hugging Face
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /app

# Install production Python dependencies
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the built app.py and project code
COPY --chown=user:user . .
# Copy static files from the builder stage
COPY --chown=user:user --from=builder /app/static ./static

# Ensure the documents directory exists for RAG
RUN mkdir -p /app/DOCU_AI/documents

# Expose the mandatory Hugging Face port
EXPOSE 7860

# Launch the unified FastAPI app on port 7860
# This satisfies Step 3 (Single Service) and Step 4 (Startup Command)
CMD ["python3", "-m", "uvicorn", "app:api", "--host", "0.0.0.0", "--port", "7860"]
