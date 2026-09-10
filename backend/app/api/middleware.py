import time

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Structure: { ip: {'upload': [timestamps], 'api': [timestamps]} }
        self.ip_records = {}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time.time()

        if ip not in self.ip_records:
            self.ip_records[ip] = {"upload": [], "api": []}

        # Determine if it's an upload endpoint
        is_upload = request.url.path == "/api/scans" and request.method == "POST"
        category = "upload" if is_upload else "api"
        limit = 5 if is_upload else 60

        # Clean up timestamps older than 60 seconds
        self.ip_records[ip][category] = [t for t in self.ip_records[ip][category] if now - t < 60]

        if len(self.ip_records[ip][category]) >= limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {"code": "TOO_MANY_REQUESTS", "message": "Too many requests. Please try again later."}
                },
            )

        self.ip_records[ip][category].append(now)

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response
