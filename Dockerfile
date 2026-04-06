# -------------------------------
# Stage 1: Build the Reflex Frontend (Heavier)
# -------------------------------
FROM python:3.11-slim AS builder

# Install Node.js, unzip, git, build-essential, graphics/PDF libs, and extra dev packages for node-gyp and image handling
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    python3-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libjpeg-dev \
    libgif-dev \
    librsvg2-dev \
    libffi-dev \
    libssl-dev \
    libpng-dev \
    libwebp-dev \
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
ARG REFLEX_API_URL
ENV REFLEX_API_URL=$REFLEX_API_URL
ENV TELEMETRY_ENABLED=false
ENV NODE_OPTIONS=--max-old-space-size=4096

RUN GROQ_API_KEY=gsk_build_check_dummy reflex init
RUN GROQ_API_KEY=gsk_build_check_dummy reflex export --frontend-only
RUN mkdir -p /app/static && \
    unzip frontend.zip -d /app/static && \
    rm frontend.zip




# -------------------------------
# Stage 2: Final Production Image (Lean - Under 4GB)
# -------------------------------
FROM python:3.11-slim

# Install minimal runtime dependencies and Node.js for Reflex's internal boot checks
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
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

# 5. Boot Injection Script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Railway dynamically assigns $PORT; our app.py listens to it.
EXPOSE 7860

# Launch through the dynamic environment patch script
CMD ["/app/entrypoint.sh"]
