from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Import the base class for custom middleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.routers import users, auth, chats
import os

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "upgrade-insecure-requests"
        return response


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
    origins = ["https://jihc-lostandfound.web.app"]
    app.add_middleware(CSPMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Generic health route to sanity check the API
    @app.get("/health")
    async def health() -> str:
        return "ok"

    return app