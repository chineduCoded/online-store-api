from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", "N/A")
        client_ip = request.client.host
        logger.info(f"Incoming request: {request.method} {request.url} | Request ID: {request_id} | Client IP: {client_ip}")

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(f"Response: {response.status_code} | Process Time: {process_time:.2f}s")

        return response
        