from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 500

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class UnreachableHostError(Exception):
    status_code = 500

    def __init__(self, api_host: str):
        self.api_host = api_host
        super().__init__(f"The API host '{api_host}' is not reachable")


class InvalidModelIDError(AppError):
    status_code = 404

    def __init__(self, model_id: str):
        self.model_id = model_id
        super().__init__(f"The model ID '{model_id}' could not be found")


class InvalidAPIKeyError(AppError):
    status_code = 401

    def __init__(self) -> None:
        super().__init__("The API key is not valid")


class InvalidSamplingParameterError(AppError):
    status_code = 422

    def __init__(self, param: str, value: float | int, reason: str):
        self.param = param
        self.value = value
        self.reason = reason
        super().__init__(f"'{value}' is not a valid value for sampling parameter '{param}': {reason}")


class InvalidSaveDir(AppError):
    status_code = 500

    def __init__(self, path_str: str, reason: str):
        self.path_str = path_str
        self.reason = reason
        super().__init__(f"The save dir '{path_str}' is not valid: {reason}")


class GenerationError(AppError):
    status_code = 500

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"An error was encountered during generation: {reason}")


class InvalidMessageContent(AppError):
    status_code = 500

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"The message content is invalid: {reason}")


class InvalidMessageRole(AppError):
    status_code = 500

    def __init__(self, role: str, reason: str):
        self.role = role
        self.reason = reason
        super().__init__(f"The role '{role}' is not valid in this context: {reason}")


class JobNotFoundError(AppError):
    status_code = 404

    def __init__(self, uuid_str: str):
        self.uuid_str = uuid_str
        super().__init__(f"The just '{uuid_str}' does not exist")


class InvalidUUIDError(AppError):
    status_code = 422

    def __init__(self, uuid_str: str):
        self.uuid_str = uuid_str
        super().__init__(f"'{uuid_str}' is not a valid UUID")


class CorrupedSaveFileError(AppError):
    status_code = 500

    def __init__(self, path_str: str):
        self.path_str = path_str
        super().__init__(f"The save file at '{path_str}' is corrupted and could not be loaded")


class SaveFileNotFoundError(AppError):
    status_code = 404

    def __init__(self, path_str: str):
        self.path_str = path_str
        super().__init__(f"The file at '{path_str}' could not be found and thus could not be loaded")


class JobEmptyError(AppError):
    status_code = 400

    def __init__(self, uuid_str: str):
        self.uuid_str = uuid_str
        super().__init__(f"The job '{uuid_str}' has no content")


def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)}
    )