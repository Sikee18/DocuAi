# Stage 1: Build environment
FROM python:3.11-slim

# Install system dependencies including Caddy for Reverse Proxy
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    build-essential \
    debian-keyring debian-archive-keyring apt-transport-https \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list \
    && apt-get update && apt-get install caddy -y \
    && rm -rf /var/lib/apt/lists/*

# Fix Hugging Face root permission constraint (runs as user 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY --chown=user . $HOME/app

# Fix for AST compilation: Provides a dummy key to bypass LangChain checks during build
ENV GROQ_API_KEY="dummy_key_to_pass_build"
# Inform the React App to connect websocket securely to the Hugging Face Public URL
ENV API_URL="https://sikee18-docuai.hf.space"

# Export the Reflex frontend asynchronously to pre-build the NextJS cluster
# Doing this during Docker Build ensures the container boots instantly 
# without timing out the 30-min health check payload!
RUN reflex init
RUN reflex export --frontend-only --no-zip

# Expose single port required by Hugging Face Spaces
EXPOSE 7860

# Default execution startup command for production deployment
CMD ["bash", "run.sh"]
