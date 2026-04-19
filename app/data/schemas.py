from __future__ import annotations

from pydantic import BaseModel, field_validator, model_validator, ValidationError
from uuid import UUID
from typing import Self

from app.common.config import GLOBAL_SETTINGS, GLOBAL_CLIENT
from app.data.errors import InvalidDataJobRequest
from app.common.literals import JobStatus, OnError, SaveFormat
from app.common.chats import Chat, ChatJSONLEntry
from app.common.errors import (
    InvalidUUIDError,
    InvalidModelIDError,
    SaveFileNotFoundError,
    CorrupedSaveFileError,
    JobEmptyError
)


class DataJobRequest(BaseModel):
    system_messages: list[str]
    chat_length_max: int
    chat_length_min: int
    queries_job_uuid: str
    max_retries: int = 3
    on_error: OnError = "continue"
    model_id: str = GLOBAL_SETTINGS.default_model_id

    @field_validator("system_messages")
    @classmethod
    def validate_system_messages(cls, system_messages: list[str]) -> list[str]:
        if len(system_messages) == 0:
            raise InvalidDataJobRequest("expected at least one system message")
        for i, system_message in enumerate(system_messages):
            if len(system_message) == 0:
                raise InvalidDataJobRequest(f"system message {i} is empty")
        return system_messages
    
    @field_validator("chat_length_max")
    @classmethod
    def validate_chat_length_max(cls, chat_length_max: int) -> int:
        return chat_length_max
    
    @field_validator("chat_length_min")
    @classmethod
    def validate_chat_length_min(cls, chat_length_min: int) -> int:
        if chat_length_min <= 0:
            raise InvalidDataJobRequest(f"chat_length_min must be > 0, got {chat_length_min}")
        return chat_length_min
    
    @field_validator("queries_job_uuid")
    @classmethod
    def validate_queries_job_uuid(cls, queries_job_uuid: str) -> str:
        try:
            UUID(queries_job_uuid)
        except Exception:
            raise InvalidUUIDError(queries_job_uuid)
        return queries_job_uuid
    
    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, max_retries: int) -> int:
        if max_retries < 0 or max_retries > 10:
            raise InvalidDataJobRequest("max_retries must be >= 0 and <= 10")
        return max_retries
    
    @field_validator("model_id")
    @classmethod
    def validate_model_id(cls, model_id: str) -> str:
        if model_id not in [m.id for m in GLOBAL_CLIENT.models.list()]:
            raise InvalidModelIDError(model_id)
        return model_id
    
    @model_validator(mode="after")
    def validate_cross_fields(self) -> Self:
        if self.chat_length_max < self.chat_length_min:
            raise InvalidDataJobRequest("chat_length_max must be >= chat_length_min")
        return self
    
    def initialize_job(self) -> DataJob:
        return DataJob(
            system_messages=self.system_messages,
            chat_length_max=self.chat_length_max,
            chat_length_min=self.chat_length_min,
            queries_job_uuid=self.queries_job_uuid,
            max_retries=self.max_retries,
            on_error=self.on_error,
            model_id=self.model_id,
            status="pending",
            error_detail=None,
            chats=None
        )
    

class DataJob(DataJobRequest):
    status: JobStatus
    error_detail: str | None = None
    chats: list[Chat] | None = None

    def save(self, uuid_str: str, format: SaveFormat) -> None:
        save_path = GLOBAL_SETTINGS.save_dir / f"{uuid_str}.{format}"
        with open(save_path, 'w') as save_file:
            if format == "json":
                save_file.write(self.model_dump_json(indent=2))
            elif format == "jsonl":
                if not self.chats:
                    raise JobEmptyError(uuid_str)
                for chat in self.chats:
                    entry = ChatJSONLEntry(messages=chat.messages)
                    save_file.write(entry.model_dump_json() + "\n")

    @classmethod
    def load(cls, uuid_str: str) -> "DataJob":
        load_path = GLOBAL_SETTINGS.save_dir / f"{uuid_str}.json"
        if not load_path.exists():
            raise SaveFileNotFoundError(str(load_path))
        with open(load_path, 'r') as load_file:
            try:
                return DataJob.model_validate_json(load_file.read())
            except ValidationError:
                raise CorrupedSaveFileError(str(load_path))