import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import reflex as rx

from DOCU_AI.DOCU_AI import app

# 1. Force state compilation. This guarantees WebSockets and Upload logic are permanently instantiated.
app._compile()

# 2. Extract inner FastAPI framework
api = getattr(app, "api", getattr(app, "_api", None))

# 3. Strip all Server-Side UI rendering routes! 
# Since we explicitly exported a static frontend.zip, we do not want Reflex crashing Render by attempting to boot Node.js to SSR the UI upon page load.
# We exclusively keep only the backend infrastructure paths (Sockets, Uploads, and Pings).
api.router.routes = [
    route for route in api.router.routes
    if getattr(route, "path", "/").startswith("/_") or getattr(route, "path", "/") == "/ping"
]

# 4. Standard Configuration
PORT = int(os.getenv("PORT", "7860"))

origins = [
    "https://localhost:8000",
    "http://localhost:3000",
    "*"  
]
render_url = os.getenv("RENDER_EXTERNAL_URL", "")
if render_url:
    origins.append(render_url)

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Serve Pre-Compiled UI as Catch-All
static_dir = os.path.join(os.getcwd(), "static")
if os.path.exists(static_dir):
    api.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
    print(f"Serving precompiled frontend directly from {static_dir}")
else:
    print(f"Warning: Static directory {static_dir} not found. Running API only.")
