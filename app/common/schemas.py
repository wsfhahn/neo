from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any

from app.common.literals import MessageJobStatus
from app.chat.errors import InvalidMessageRequestError


class InfoResponse(BaseModel):
    message: str


class JobScheduledResponse(BaseModel):
    message: str
    uuid: str


class JobsList(BaseModel):
    jobs: dict[str, MessageJobStatus]