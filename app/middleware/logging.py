# app/middleware/logging.py
from fastapi import Request
import time
import uuid
from app.core.logging import logger


async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Add request ID to logger
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={"request_id": request_id}
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.4f}s",
            extra={"request_id": request_id}
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        logger.error(
            f"Request failed: {request.method} {request.url.path} - Error: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise
