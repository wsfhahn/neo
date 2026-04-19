from app.common.errors import AppError


class InvalidDataJobRequest(AppError):
    status_code = 422

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Invalid data job request: {reason}")


class QueriesResponseEmpty(AppError):
    status_code = 400

    def __init__(self, uuid_str: str):
        self.uuid_str = uuid_str
        super().__init__(f"The queries job '{uuid_str}' has no content")


class InvalidJobType(AppError):
    status_code = 400

    def __init__(self, uuid_str: str):
        self.uuid_str = uuid_str
        super().__init__(f"Job '{uuid_str}' is not the correct type")