import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.utils.logger import logger


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Starlette middleware that logs every HTTP request with method, path,
    status code, and duration. This creates an access log separate from
    the per-action audit trail in AuditLog.
    Why: provides visibility into API usage patterns and helps diagnose
    performance issues without querying the database.
    """
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)"
        )
        return response
