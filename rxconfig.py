import reflex as rx
import os

# Dynamic API URL for Render deployment
api_url = os.getenv("REFLEX_API_URL", "")
if not api_url:
    api_url = "http://localhost:8000"

# Dynamic Origins for WebSocket CORS
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Explicitly add Render's environment URL to avoid Python-SocketIO string wildcard bug
render_url = os.getenv("RENDER_EXTERNAL_URL", "")
if render_url:
    cors_origins.append(render_url)
    
# Fallback to appending REFLEX_API_URL if set but different
if api_url and "://" in api_url:
    base_origin = api_url.split("/")[0] + "//" + api_url.split("/")[2]
    if base_origin not in cors_origins:
        cors_origins.append(base_origin)

config = rx.Config(
    app_name="DOCU_AI",
    cors_allowed_origins=cors_origins,
    api_url=api_url,
    plugins=[
        rx.plugins.SitemapPlugin(),
        # Removing TailwindV4 plugin if it's causing build bloat or errors
    ]
)