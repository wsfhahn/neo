from app.common.errors import AppError


class InvalidQueriesRequestError(AppError):
    """The queries request is not valid, unprocessable entity"""

    status_code = 422

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Invalid queries request: {reason}")