from app.common.errors import AppError


class JSONLQueriesFileNotFoundError(AppError):
    status_code = 404

    def __init__(self, uuid_str: str):
        self.uuid_str = uuid_str
        super().__init__(f"Queries JSONL file for job '{uuid_str}' not found")