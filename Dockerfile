FROM python:3.11-slim

# Install system dependencies required for Reflex, Node/Bun, and DB Compilation
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project source code
COPY . .

# Fix for AST compilation: Provides a dummy key to bypass LangChain checks during build
ENV GROQ_API_KEY="dummy_key_to_pass_build"

# Export the Reflex frontend asynchronously to pre-build the NextJS cluster
# Doing this during Docker Build ensures the container boots quickly without runtime compilation
RUN reflex export --frontend-only --no-zip

# Define exposed ports for the backend and frontend
EXPOSE 8000
EXPOSE 3000

# Default execution startup command for production deployment
CMD reflex run --env prod
