from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Import the base class for custom middleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.routers import users, auth, chats
import os

def create_app() -> FastAPI:
    app = FastAPI(title="Fastapi Template")
    from fastapi.staticfiles import StaticFiles
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.include_router(users.router)
    app.include_router(auth.router)
    from app.routers import lostandfound
    app.include_router(lostandfound.router)
    app.include_router(chats.router)
    env_origins = os.getenv("ALLOWED_ORIGINS", "")
    origins = [
    "https://jihc-7777.web.app",
    "https://jihc-777.web.app",
    "http://localhost",
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    @app.get("/health")
    async def health() -> str:
        return "ok"

    return app
