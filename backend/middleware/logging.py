"""Request logging middleware."""
from __future__ import annotations

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        path = request.url.path
        if path.startswith("/api") or path in ("/health", "/chetna"):
            print(
                f"[HTTP] {request.method} {path} "
                f"-> {response.status_code} ({elapsed_ms:.1f}ms)"
            )
        return response
