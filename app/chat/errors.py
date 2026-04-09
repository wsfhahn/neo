from fastapi import Request
from fastapi.responses import JSONResponse

from app.common.errors import AppError
    

class InvalidMessageRequestError(AppError):
    status_code = 422

    def __init__(self, reason: str):
        self.resaon = reason
        super().__init__(f"Invalid message request: {reason}")