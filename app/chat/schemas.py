from __future__ import annotations

from pydantic import BaseModel
from typing import Any

from app.chat.errors import InvalidMessageRequestError
from app.common.literals import MessageJobStatus


class MessageRequest(BaseModel):
    """Schema for a message request, used by the API for validating a request."""

    system: str | None = None
    user: str

    def model_post_init(self, __context: Any) -> None:
        if not self.user:
            raise InvalidMessageRequestError(
                reason="user message cannot be empty"
            )
    
    def initialize_job(self) -> MessageJob:
        return MessageJob(
            system=self.system,
            user=self.user,
            status="pending",
            error_detail=None,
            response=None
        )


class MessageJob(MessageRequest):
    """A message job, which inherits MessageQuest and adds fields necessary for processing."""

    status: MessageJobStatus
    error_detail: str | None = None
    response: str | None = None