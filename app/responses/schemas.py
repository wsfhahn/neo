from __future__ import annotations

from pydantic import BaseModel
from typing import Any, Literal
from pathlib import Path
from uuid import UUID

from app.common.config import GLOBAL_SETTINGS
from app.common.errors import InvalidUUIDError
from app.common.literals import ResponsesJobStatus
from app.responses.errors import JSONLQueriesFileNotFoundError


class ResponsesResponse(BaseModel):
    number: str
    category: str
    query: str
    content: list[str]


class ResponsesGenerationJobRequest(BaseModel):
    system: str | None = None
    uuid_str: str
    responses_per_query: int
    max_retries: int
    on_error: Literal["continue", "stop"]

    def model_post_init(self, __context: Any) -> None:
        try:
            UUID(self.uuid_str)
        except Exception:
            raise InvalidUUIDError(uuid_str=self.uuid_str)

        load_path = GLOBAL_SETTINGS.save_dir / f"{self.uuid_str}.jsonl"
        if not load_path.exists():
            raise JSONLQueriesFileNotFoundError(uuid_str=self.uuid_str)
    
    def initialize_job(self) -> ResponsesGenerationJob:
        return ResponsesGenerationJob(
            system=self.system,
            uuid_str=self.uuid_str,
            responses_per_query=self.responses_per_query,
            max_retries=self.max_retries,
            on_error=self.on_error,
            status="pending",
            error_detail=None,
            response=None
        )

class ResponsesGenerationJob(ResponsesGenerationJobRequest):
    status: ResponsesJobStatus
    error_detail: str | None = None
    response: list[ResponsesResponse] | None = None