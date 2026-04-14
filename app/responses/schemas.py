from __future__ import annotations

from pydantic import BaseModel
from typing import Any, Literal
from uuid import UUID

from app.common.config import GLOBAL_SETTINGS, GLOBAL_CLIENT
from app.common.errors import (
    InvalidUUIDError,
    InvalidModelIDError,
    ResponseEmptyError,
    FileNotFoundError,
    CorruptedSaveFileError
)
from app.common.literals import IterableJobStatus
from app.responses.errors import JSONLQueriesFileNotFoundError


class ResponsesResponse(BaseModel):
    """Response from the model answering a query during a responses generation job."""
    number: int
    category: str
    query: str
    content: str


class ResponsesJSONEntry(BaseModel):
    """An entry for saving responses as JSONL."""
    responses_model_id: str
    number: int
    category: str
    query: str
    content: str


class ResponsesGenerationRequest(BaseModel):
    """A request from the client to start a responses generation job."""

    system: str | None = None
    queries_uuid_str: str
    max_retries: int
    on_error: Literal["continue", "stop"]
    model_id: str | None = None

    def model_post_init(self, __context: Any) -> None:
        try:
            UUID(self.queries_uuid_str)
        except Exception:
            raise InvalidUUIDError(uuid_str=self.queries_uuid_str)

        load_path = GLOBAL_SETTINGS.save_dir / f"{self.queries_uuid_str}.jsonl"
        if not load_path.exists():
            raise JSONLQueriesFileNotFoundError(uuid_str=self.queries_uuid_str)
        
        if self.model_id and self.model_id not in [m.id for m in GLOBAL_CLIENT.models.list()]:
                raise InvalidModelIDError(model_id=self.model_id)
    
    def initialize_job(self) -> ResponsesGenerationJob:
        return ResponsesGenerationJob(
            system=self.system,
            queries_uuid_str=self.queries_uuid_str,
            max_retries=self.max_retries,
            on_error=self.on_error,
            model_id=self.model_id if self.model_id else GLOBAL_SETTINGS.model_id,
            status="pending",
            error_detail=None,
            response=None
        )

class ResponsesGenerationJob(ResponsesGenerationRequest):
    model_id: str
    status: IterableJobStatus
    error_detail: str | None = None
    response: list[ResponsesResponse] | None = None

    def save(
        self,
        format: Literal["json", "jsonl"],
        uuid: UUID
    ) -> None:
        save_path = GLOBAL_SETTINGS.save_dir / f"{str(uuid)}.{format}"
        with open(save_path, 'w') as save_file:
            if format == "json":
                save_file.write(self.model_dump_json(indent=2))
            elif format == "jsonl":
                if not self.response:
                    raise ResponseEmptyError(str(uuid))
                for r in self.response:
                    entry = ResponsesJSONEntry(
                        responses_model_id=self.model_id,
                        number=r.number,
                        category=r.category,
                        query=r.query,
                        content=r.content
                    )
                    save_file.write(entry.model_dump_json() + "\n")
    
    @classmethod
    def load(
        self,
        uuid: UUID
    ) -> ResponsesGenerationJob:
        load_path = GLOBAL_SETTINGS.save_dir / f"{str(uuid)}.json"
        if not load_path.exists(): raise FileNotFoundError(str(load_path))
        with open(load_path, 'r') as load_file:
            content = load_file.read()
        try:
            return ResponsesGenerationJob.model_validate_json(content)
        except Exception as e:
            raise CorruptedSaveFileError(str(load_path))