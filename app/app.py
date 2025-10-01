from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, auth, chats


def create_app() -> FastAPI:
    app = FastAPI(title="Fastapi Template")
    from fastapi.staticfiles import StaticFiles
    import os
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.include_router(users.router)
    app.include_router(auth.router)
    from app.routers import lostandfound
    app.include_router(lostandfound.router)
    app.include_router(chats.router)
    import os
    # Allow overriding CORS origins via env var: ALLOWED_ORIGINS=url1,url2
    env_origins = os.getenv("ALLOWED_ORIGINS", "")
    origins = ["https://jihc-lostandfound.web.app"]

    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        # Default: allow Firebase Hosting domains and localhost dev ports
        app.add_middleware(
            CORSMiddleware,
            allow_origin_regex=r"https://.*\\.web\\.app$|https://.*\\.firebaseapp\\.com$|http://localhost(:\\d+)?$",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Generic health route to sanity check the API
    @app.get("/health")
    async def health() -> str:
        return "ok"

    return app
