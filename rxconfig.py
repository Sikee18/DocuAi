import reflex as rx
import os

# Dynamic API URL for Render deployment
api_url = os.getenv("REFLEX_API_URL", "")
if not api_url:
    api_url = "http://localhost:8000"

config = rx.Config(
    app_name="DOCU_AI",
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    api_url=api_url,
    plugins=[
        rx.plugins.SitemapPlugin(),
        # Removing TailwindV4 plugin if it's causing build bloat or errors
    ]
)