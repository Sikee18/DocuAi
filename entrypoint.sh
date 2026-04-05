#!/bin/bash

# Ensure PORT is defined (Railway/Render)
export PORT="${PORT:-7860}"

# Auto-detect Render's live URL organically if the user didn't explicitly set REFLEX_API_URL
if [ -z "$REFLEX_API_URL" ] && [ -n "$RENDER_EXTERNAL_URL" ]; then
    export REFLEX_API_URL="$RENDER_EXTERNAL_URL"
fi

# If a valid URL is constructed, dynamically patch the static JS bundle
if [ -n "$REFLEX_API_URL" ]; then
    echo "Dynamic Patch: Injecting $REFLEX_API_URL into compiled frontend Javascript..."
    
    # Calculate WebSocket URL (replace http/https with ws/wss)
    WSS_URL="${REFLEX_API_URL/https:\/\//wss:\/\/}"
    WSS_URL="${WSS_URL/http:\/\//ws:\/\/}"

    # Sweep entire workspace logic for JS maps and Replace BOTH API and WebSocket endpoints
    find /app -type f -name "*.js" -exec sed -i "s|http://localhost:8000|$REFLEX_API_URL|g" {} +
    find /app -type f -name "*.js" -exec sed -i "s|ws://localhost:8000|$WSS_URL|g" {} +
else
    echo "Warning: REFLEX_API_URL environment variable is missing. WebSockets may default to localhost."
fi

echo "Starting Uvicorn Backend on port $PORT..."
exec python3 -m uvicorn app:api --host 0.0.0.0 --port "$PORT"
