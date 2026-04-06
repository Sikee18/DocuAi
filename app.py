import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from DOCU_AI.DOCU_AI import app

# 1. FORCE state compilation BEFORE we mutate routes
app._compile()

# 2. Extract inner FastAPI framework securely across all Reflex versions
api = getattr(app, "api", getattr(app, "_api", None))
if api is None:
    api = FastAPI()

# 3. STRIP heavy Reflex Server-Side Rendering (React) API Routes from the inner FastAPI structure.
# We do this so the deployed container doesn't try to boot gigabytes of nodejs when serving UI pages.
api.router.routes = [
    route for route in api.router.routes
    if getattr(route, "path", "/").startswith("/_") 
    or getattr(route, "path", "/") == "/ping"
    or not hasattr(route, "path")
]

# 4. Mount CORS for the actual API Routes
PORT = int(os.getenv("PORT", "7860"))
origins = ["*"]
api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Expose the precompiled static payload directly via FastAPI Fallback router!
static_dir = os.path.join(os.getcwd(), ".web", "_static")
if os.path.exists(static_dir):
    # This efficiently serves all our prebuilt HTML/JS statically safely.
    api.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
    print(f"Serving UI Catch-All from {static_dir}")

# We will run this file using `uvicorn app:app` !!
# By using exactly `app:app`, `rx.App.__call__` natively executes its own internal highly-robust socket.io proxy for `/_event`, and effortlessly falls back to `api` for the static site!
