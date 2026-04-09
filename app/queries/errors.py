from app.common.errors import AppError


class InvalidQueriesRequestError(AppError):
    """The queries request is not valid, unprocessable entity"""

    status_code = 422

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Invalid queries request: {reason}")


class ResponseEmptyError(AppError):
    """The QueriesGenerationJob cannot be saved to disk because it has not been completed."""

    status_code = 400

    def __init__(self, uuid_str: str):
        self.uuid_str = uuid_str
        super().__init__(f"Job '{uuid_str}' does not have a response")