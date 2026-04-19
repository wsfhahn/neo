from app.common.errors import AppError


class InvalidQueriesJobRequest(AppError):
    status_code = 422

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"The queries job request is not valid: {reason}")