import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import reflex as rx

# Import the main Reflex app object
from DOCU_AI.DOCU_AI import app

# 1. Extract the internal FastAPI instance (Reflex 0.8+ uses _api)
api = getattr(app, "api", getattr(app, "_api", None))

# 2. Dynamic Port Handling (Cloud Agnostic)
# Railway/Render provide the PORT variable dynamically
PORT = int(os.getenv("PORT", "7860"))

# 3. Configure CORS with Wildcard for Migration Safety
origins = [
    "https://localhost:8000",
    "http://localhost:3000",
    "*"  # Wildcard allows early Railway domains to connect without manual config
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Serve Frontend Statics (Consolidating to Port 7860)
# This requires 'reflex export --frontend-only' to have been run
# into the 'static' directory during the Docker build.
static_dir = os.path.join(os.getcwd(), "static")

if os.path.exists(static_dir):
    api.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
    print(f"Serving frontend from {static_dir}")
else:
    print(f"Warning: Static directory {static_dir} not found. Running API only.")

# For local testing, we can run this file directly with uvicorn
# Command: uvicorn app:api --host 0.0.0.0 --port 7860
