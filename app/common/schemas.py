from pydantic import BaseModel

from app.common.literals import JobStatus


class MessageResponse(BaseModel):
    message: str


class JobRegisteredResponse(BaseModel):
    uuid_str: str
    message: str


class JobStatusesResponse(BaseModel):
    jobs: dict[str, JobStatus]