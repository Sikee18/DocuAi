import reflex as rx
import os

# Dynamic API URL for Render deployment
api_url = os.getenv("REFLEX_API_URL", "")
if not api_url:
    api_url = "http://localhost:8000"

# COMPLETELY wildcard CORS!
# This strictly resolves 'python-socketio' 400 Bad Request handshake filtering blocks natively when accessed via proxy load-balancers like Render!
cors_origins = ["*"]

config = rx.Config(
    app_name="DOCU_AI",
    cors_allowed_origins=cors_origins,
    api_url=api_url,
    plugins=[
        rx.plugins.SitemapPlugin(),
    ]
)