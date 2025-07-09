from fastapi import FastAPI 
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware 
from logger import logger
from routes import auth, users, locations, hobbies, posts

import asyncio
from utils.clean_up import delete_expired_posts


# Lifespan handler for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("HobbyMatch App Backend Server is starting up!")
    asyncio.create_task(delete_expired_posts()) # Delete expired posts
    yield
    logger.info("HobbyMatch App Backend Server is shutting down!")
  
app = FastAPI(lifespan=lifespan)

# CORS config (adjust for frontend origin)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to set COOP/COEP headers
class CORPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        return response

app.add_middleware(CORPMiddleware)

# Register routes
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(locations.router)
app.include_router(hobbies.router)
app.include_router(posts.router)

# Health check route
@app.get("/")
def read_root():
    return {"message": "HobbyMatch App Backend Server is running!"}

# Run the app if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
