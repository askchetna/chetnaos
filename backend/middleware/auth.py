"""Optional API auth — disabled by default (pass-through)."""
from __future__ import annotations

import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


def _auth_enabled() -> bool:
    return bool(os.getenv("CHETNA_API_KEY", "").strip())


def optional_auth_middleware() -> type[BaseHTTPMiddleware]:
    """Return middleware class; enforces CHETNA_API_KEY only when set."""

    class OptionalAuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next) -> Response:
            if not _auth_enabled():
                return await call_next(request)
            if request.url.path in ("/health", "/"):
                return await call_next(request)
            expected = os.getenv("CHETNA_API_KEY", "")
            provided = request.headers.get("X-API-Key", "")
            if provided != expected:
                return JSONResponse({"error": "Unauthorized"}, status_code=401)
            return await call_next(request)

    return OptionalAuthMiddleware
