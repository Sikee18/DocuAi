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
    echo "Warning: REFLEX_API_URL environment variable is missing. WebSockets may default to localhost."
fi

# Reflex `_compile()` deeply mandates the physical existence of a package.json file before booting the Python state engine, even when hosting purely backend logic!
# Injecting a dummy file satisfies the sanity checks without triggering a 15 minute React build!
mkdir -p /app/.web
if [ ! -f /app/.web/package.json ]; then
    echo "{}" > /app/.web/package.json
fi

# We use uvicorn to manually host the WebSocket ASGI component alongside our pre-exported static UI payload.
# This prevents the buggy 'reflex run' command from attempting to compile React inside a low-resource Render instance for 15+ minutes!!
echo "Starting Ultra-Lean Uvicorn Bridge Natively on port $PORT..."
exec python3 -m uvicorn app:app --host 0.0.0.0 --port "$PORT" --proxy-headers --forwarded-allow-ips "*"
