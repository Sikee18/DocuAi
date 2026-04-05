#!/bin/bash

# Ensure PORT is defined (Railway/Render)
export PORT="${PORT:-7860}"

# If REFLEX_API_URL is provided by Render, dynamically patch the static JS bundle
if [ -n "$REFLEX_API_URL" ]; then
    echo "Dynamic Patch: Injecting $REFLEX_API_URL into compiled frontend Javascript..."
    # Replace default hardcoded localhost URL deeply within the bundled Javascript
    find ./static -type f -name "*.js" -exec sed -i "s|http://localhost:8000|$REFLEX_API_URL|g" {} +
else
    echo "Warning: REFLEX_API_URL environment variable is missing. WebSockets may default to localhost."
fi

echo "Starting Uvicorn Backend on port $PORT..."
exec python3 -m uvicorn app:api --host 0.0.0.0 --port "$PORT"
