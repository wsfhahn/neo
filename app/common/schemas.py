from __future__ import annotations
from pydantic import BaseModel

from app.common.literals import MessageJobStatus


class InfoResponse(BaseModel):
    message: str


class JobScheduledResponse(BaseModel):
    message: str
    uuid: str


class JobsList(BaseModel):
    jobs: dict[str, MessageJobStatus]