from __future__ import annotations
from pydantic import BaseModel

from app.common.literals import IterableJobStatus


class InfoResponse(BaseModel):
    """Simple info response."""
    message: str


class JobScheduledResponse(BaseModel):
    """A response confirming that a job has been scheduled, returning the UUID for polling."""
    message: str
    uuid: str


class JobsList(BaseModel):
    """A response containing a list of jobs and their statuses."""
    jobs: dict[str, IterableJobStatus]