from app.common.errors import AppError
    

class InvalidMessageRequestError(AppError):
    """The message request is invalid and could not be processed."""

    status_code = 422

    def __init__(self, reason: str):
        self.resaon = reason
        super().__init__(f"Invalid message request: {reason}")