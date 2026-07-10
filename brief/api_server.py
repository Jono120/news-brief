from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from brief.api.routes import router
from brief.server import add_server_middleware


def _cors_origins() -> list[str]:
    defaults = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "https://127.0.0.1:5173",
        "https://localhost:5173",
        "https://127.0.0.1:8080",
        "https://localhost:8080",
    ]
    extra = os.environ.get("BRIEF_CORS_ORIGINS", "")
    if extra:
        defaults.extend(origin.strip() for origin in extra.split(",") if origin.strip())
    return defaults


def create_api_app(*, require_https: bool = False) -> FastAPI:
    app = FastAPI(title="Brief APAC API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    add_server_middleware(app, require_https=require_https)
    return app


app = create_api_app()
