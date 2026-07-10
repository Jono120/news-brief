from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

import uvicorn
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.types import ASGIApp

from brief.certs import ensure_dev_tls_certs

HTTPS_CLIENT_DEFAULTS = {"verify": True, "follow_redirects": True}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        if _request_is_https(request):
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return response


class HttpsRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if not _request_is_https(request):
            target = request.url.replace(scheme="https")
            return RedirectResponse(str(target), status_code=308)
        return await call_next(request)


def _request_is_https(request: Request) -> bool:
    forwarded = request.headers.get("x-forwarded-proto", "")
    if forwarded:
        return forwarded.split(",", 1)[0].strip().lower() == "https"
    return request.url.scheme == "https"


def add_server_middleware(app: FastAPI, *, require_https: bool) -> None:
    app.add_middleware(SecurityHeadersMiddleware)
    if require_https:
        app.add_middleware(HttpsRedirectMiddleware)


def resolve_tls_material(
    *,
    https: bool,
    ssl_certfile: str | None = None,
    ssl_keyfile: str | None = None,
) -> tuple[str | None, str | None]:
    if not https:
        return None, None

    cert = ssl_certfile or os.environ.get("BRIEF_SSL_CERTFILE")
    key = ssl_keyfile or os.environ.get("BRIEF_SSL_KEYFILE")
    if cert and key:
        return cert, key

    dev_cert, dev_key = ensure_dev_tls_certs()
    return str(dev_cert), str(dev_key)


def service_url(host: str, port: int, *, use_tls: bool) -> str:
    scheme = "https" if use_tls else "http"
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    return f"{scheme}://{host}:{port}"


def require_https_url(url: str, *, label: str = "URL") -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"{label} must use HTTPS: {url}")
    return url


def run_uvicorn(
    app: ASGIApp,
    *,
    host: str,
    port: int,
    ssl_certfile: str | None = None,
    ssl_keyfile: str | None = None,
) -> None:
    kwargs: dict[str, Any] = {
        "host": host,
        "port": port,
        "log_level": "info",
        "proxy_headers": True,
        "forwarded_allow_ips": os.environ.get("BRIEF_FORWARDED_ALLOW_IPS", "127.0.0.1"),
    }
    if ssl_certfile and ssl_keyfile:
        kwargs["ssl_certfile"] = ssl_certfile
        kwargs["ssl_keyfile"] = ssl_keyfile
    elif ssl_certfile or ssl_keyfile:
        raise ValueError("Both --ssl-certfile and --ssl-keyfile are required for HTTPS")
    uvicorn.run(app, **kwargs)
