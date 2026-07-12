from __future__ import annotations

import os
import secrets

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

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


class BearerTokenMiddleware(BaseHTTPMiddleware):
    """Require `Authorization: Bearer <token>` on every request.

    Enabled only when BRIEF_API_TOKEN is set. CORS preflights and the health
    probe stay open so browsers and monitors keep working.
    """

    def __init__(self, app, token: str) -> None:
        super().__init__(app)
        self._token = token

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method == "OPTIONS" or request.url.path == "/api/health":
            return await call_next(request)
        header = request.headers.get("authorization", "")
        expected = f"Bearer {self._token}"
        if not secrets.compare_digest(header, expected):
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)
        return await call_next(request)


def create_api_app(*, require_https: bool = False) -> FastAPI:
    app = FastAPI(title="Brief APAC API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    token = os.environ.get("BRIEF_API_TOKEN", "").strip()
    if token:
        app.add_middleware(BearerTokenMiddleware, token=token)
    app.include_router(router)
    add_server_middleware(app, require_https=require_https)
    return app


app = create_api_app()
