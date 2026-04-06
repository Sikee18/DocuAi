#!/bin/bash

# Ensure PORT is defined (Railway/Render)
export PORT="${PORT:-7860}"

# Auto-detect Render's live URL natively
if [ -z "$REFLEX_API_URL" ] && [ -n "$RENDER_EXTERNAL_URL" ]; then
    export REFLEX_API_URL="$RENDER_EXTERNAL_URL"
fi

# Dynamically patch the bundled frontend javascript to target our live endpoints
if [ -n "$REFLEX_API_URL" ]; then
    echo "Dynamic Patch: Injecting $REFLEX_API_URL into compiled frontend Javascript..."
    
    # Calculate WebSocket URL (replace http/https with ws/wss)
    WSS_URL="${REFLEX_API_URL/https:\/\//wss:\/\/}"
    WSS_URL="${WSS_URL/http:\/\//ws:\/\/}"

    find /app/.web/_static -type f -name "*.js" -exec sed -i "s|ws://localhost:8000|$WSS_URL|g" {} +
    find /app/.web/_static -type f -name "*.js" -exec sed -i "s|http://localhost:8000|$REFLEX_API_URL|g" {} +
else
# Create dummy package.json BEFORE calling reflex run, so Reflex's engine checks bypass the node_modules verification cleanly cleanly!
mkdir -p /app/.web
if [ ! -f /app/.web/package.json ]; then
    echo "{}" > /app/.web/package.json
fi

# Removing '--backend-only' because we WANT Reflex to serve the static frontend UI on '/'!!
echo "Starting Reflex Natively on port $PORT..."
exec reflex run --env prod
