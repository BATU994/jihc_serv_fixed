from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.routers import users, auth, chats
import os


def create_app() -> FastAPI:
    app = FastAPI(title="Fastapi Template")

    # Serve static files
    from fastapi.staticfiles import StaticFiles
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Include routers
    app.include_router(users.router)
    app.include_router(auth.router)
    from app.routers import lostandfound
    app.include_router(lostandfound.router)
    app.include_router(chats.router)

    # Allowed origins
    origins = [
        "https://jihc-7777.web.app",
        "https://jihc-777.web.app",
        "http://localhost",
        "http://127.0.0.1",
    ]

    # ✅ CORS middleware (inside create_app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=r"http://localhost(:\d+)?",  # allow all localhost ports
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> str:
        return "ok"

    return app
