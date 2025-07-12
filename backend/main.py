from fastapi import FastAPI 
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware 
from logger import logger
from routes import auth, users, locations, hobbies, posts, websocket
from datetime import datetime
import asyncio
from utils.clean_up import delete_expired_posts_loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for handling app startup and shutdown tasks.

    Behavior:
    - On startup: logs a message and starts the background task to clean up expired posts.
    - On shutdown: cancels the background task and logs the app uptime.
    """

    start_time = datetime.utcnow()
    task = asyncio.create_task(delete_expired_posts_loop()) # Start background cleanup loop
    try:
        logger.info("HobbyMatch Backend Server is starting up!")
        yield
    finally:
        task.cancel() # Gracefully cancel cleanup task on shutdown
        try:
            await task
        except asyncio.CancelledError:
            pass
        uptime = datetime.utcnow() - start_time
        logger.info(f"HobbyMatch Backend Server is shutting down! Uptime: {uptime}")

# Create FastAPI app instance with custom lifespan handling
app = FastAPI(lifespan=lifespan)

# CORS configuration for frontend communication
origins = [
    "http://localhost:5173", # Vite dev server
    "http://127.0.0.1:5173", # Alternative localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow frontend dev URLs
    allow_credentials=True,
    allow_methods=["*"],    # Allow all HTTP methods
    allow_headers=["*"],    # Allow all custom headers
)

class CORPMiddleware(BaseHTTPMiddleware):
    """
    Custom middleware to enforce Cross-Origin policies for secure browser contexts.

    Headers added:
    - Cross-Origin-Opener-Policy: Ensures same-origin isolation.
    - Cross-Origin-Embedder-Policy: Blocks loading cross-origin resources without CORS.
    """

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        return response

# Add COOP/COEP middleware for secure context
app.add_middleware(CORPMiddleware)

# Register application routers for various modules
app.include_router(auth.router)        # Auth endpoints
app.include_router(users.router)       # User-related endpoints
app.include_router(locations.router)   # Location data
app.include_router(hobbies.router)     # Hobby interests
app.include_router(posts.router)       # Post/feed system
app.include_router(websocket.router)   # WebSocket for real-time feed

@app.get("/")
def read_root():
    """
    Health check route for backend availability.

    Returns:
    - JSON message indicating the server is running.
    """

    return {"message": "HobbyMatch App Backend Server is running!"}

# Local development entry point
if __name__ == "__main__":
    import uvicorn
    # Run the app locally with auto-reload enabled
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
