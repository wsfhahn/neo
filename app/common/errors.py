from __future__ import annotations
from fastapi import Request
from fastapi.responses import JSONResponse

class InvalidSamplingParameterError(Exception):
    def __init__(self, param: str, reason: str):
        self.param = param
        self.reason = reason
        super().__init__(f"Invalid config for sampling parameter '{param}': {reason}")


class InvalidAPIHostError(Exception):
    def __init__(self, api_host: str, reason: str):
        self.api_host = api_host
        self.reason = reason
        super().__init__(f"Invalid API host '{api_host}': {reason}")


class InvalidModelIDError(Exception):
    def __init__(self, model_id: str):
        self.model_id = model_id
        super().__init__(f"Invalid model ID '{model_id}'")

    
class InvalidSavePathError(Exception):
    def __init__(self, path_str: str, reason: str):
        self.reason = reason
        super().__init__(f"Invalid save dir '{path_str}': {reason}")


class AppError(Exception):
    status_code = 500

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.message)

    @property
    def message(self) -> str:
        return self.detail


class JobNotFoundError(AppError):
    status_code = 404

    def __init__(self, uuid_str: str):
        self.uuid_str = uuid_str
        super().__init__(f"Job '{uuid_str}' not found")


class InvalidUUIDError(AppError):
    status_code = 422

    def __init__(self, uuid_str: str):
        self.uuid_str = uuid_str
        super().__init__(f"'{uuid_str}' is not a valid UUID")


class FileNotFoundError(AppError):
    status_code = 404

    def __init__(self, path_str: str):
        self.path_str = path_str
        super().__init__(f"File not found: {path_str}")


class CorruptedSaveFileError(AppError):
    status_code = 500

    def __init__(self, path_str: str):
        self.path_str = path_str
        super().__init__(f"Save file '{path_str}' is corrupted")


class GenerationError(AppError):
    status_code = 500

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Error while generating response: {reason}")
    

def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)}
    )