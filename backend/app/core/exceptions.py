from fastapi import Request
from fastapi.responses import JSONResponse
import uuid
import datetime

class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}

async def app_exception_handler(request: Request, exc: AppException):
    req_id = request.headers.get("x-request-id", f"req_{uuid.uuid4().hex[:8]}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            },
            "meta": {
                "request_id": req_id,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
        }
    )
