import os
import socketio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
import reflex as rx
from DOCU_AI.DOCU_AI import app

# FORCE compilation of backend routes (/_event, /_upload, etc.) NOW.
# This gathers the Python UI states natively!
app._compile()

# 2. Extract inner FastAPI framework
api = getattr(app, "api", getattr(app, "_api", None))
if api is None:
    api = FastAPI()

# VERY IMPORTANT: Strip all Server-Side UI rendering routes! 
api.router.routes = [
    route for route in api.router.routes
    if getattr(route, "path", "/").startswith("/_") 
    or getattr(route, "path", "/") == "/ping"
    or not hasattr(route, "path")
]

# 3. Standard Configuration
PORT = int(os.getenv("PORT", "7860"))
origins = ["*"]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Expose Pre-Compiled UI as Catch-All Root
static_dir = os.path.join(os.getcwd(), ".web", "_static")
if os.path.exists(static_dir):
    api.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
    print(f"Serving precompiled frontend directly from {static_dir}")
else:
    print(f"Warning: Static directory {static_dir} not found. UI will 404.")

# 5. Expose Socket.IO natively using ASGI Wrapper!
# This officially exposes the Reflex WebSocket engine without triggering compilation!!
if hasattr(app, "sio"):
    app_wrapper = socketio.ASGIApp(
        socketio_server=app.sio,
        other_asgi_app=api,
        socketio_path="/_event"
    )
else:
    app_wrapper = api

# Execution command for uvicorn: `uvicorn app:app_wrapper`
