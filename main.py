from fastapi import FastAPI
from uuid import uuid4, UUID
from contextlib import asynccontextmanager
from asyncio import create_task

from app.common.jobs import job_lock, job_queue, jobs, worker
from app.common.types import JobRequestType, JobType
from app.common.literals import JobStatus, SaveFormat
from app.data.schemas import DataJob
from app.data.errors import QueriesResponseEmpty, InvalidJobType
from app.queries.schemas import QueriesJob
from app.common.errors import (
    AppError,
    handle_app_error,
    JobNotFoundError,
    InvalidUUIDError
)
from app.common.schemas import (
    JobRegisteredResponse,
    MessageResponse,
    JobStatusesResponse
)


@asynccontextmanager
async def lifespan(app: FastAPI): # type: ignore[no-untyped-def]
    worker_task = create_task(worker())
    yield

app = FastAPI(
    lifespan=lifespan,
    exception_handlers={
        AppError: handle_app_error # type: ignore[dict-item]
    }
)


@app.get("/ping", response_model=MessageResponse)
async def ping() -> MessageResponse:
    return MessageResponse(message="pong!")


@app.get("/jobs", response_model=JobStatusesResponse)
async def get_statuses() -> JobStatusesResponse:
    statuses: dict[str, JobStatus] = {}
    async with job_lock:
        for uuid, job in jobs.items():
            statuses[str(uuid)] = job.status
    return JobStatusesResponse(jobs=statuses)


@app.post("/register", response_model=JobRegisteredResponse)
async def register(payload: JobRequestType) -> JobRegisteredResponse:
    job = payload.initialize_job()
    if isinstance(job, DataJob):
        async with job_lock: queries_job = jobs.get(UUID(job.queries_job_uuid))
        if not queries_job:
            raise JobNotFoundError(job.queries_job_uuid)
        if not isinstance(queries_job, QueriesJob):
            raise InvalidJobType(job.queries_job_uuid)
        if not queries_job.result or len(queries_job.result) == 0:
            raise QueriesResponseEmpty(job.queries_job_uuid)
        job.chats = queries_job.to_chats(system_messages=job.system_messages)


    job_uuid = uuid4()
    async with job_lock:
        await job_queue.put(job_uuid)
        jobs[job_uuid] = job
    
    return JobRegisteredResponse(
        uuid_str=str(job_uuid),
        message="Job has been successfully scheduled!"
    )


@app.get("/job/{uuid_str}", response_model=JobType)
async def get_job(uuid_str: str) -> JobType:
    try:
        job_uuid = UUID(uuid_str)
    except Exception:
        raise InvalidUUIDError(uuid_str)
    
    async with job_lock:
        job = jobs.get(job_uuid)
    if not job:
        raise JobNotFoundError(uuid_str)
    return job


@app.get("/job/{uuid_str}/save/{format}", response_model=JobRegisteredResponse)
async def save_job(uuid_str: str, format: SaveFormat) -> JobRegisteredResponse:
    try:
        job_uuid = UUID(uuid_str)
    except Exception:
        raise InvalidUUIDError(uuid_str)
    
    job = jobs.get(job_uuid)
    if not job:
        raise JobNotFoundError(uuid_str)
    job.save(uuid_str, format)

    return JobRegisteredResponse(
        uuid_str=uuid_str,
        message="Job successfully saved!"
    )


@app.get("/job/{uuid_str}/load", response_model=JobRegisteredResponse)
async def load_job(uuid_str: str) -> JobRegisteredResponse:
    def _validate_job() -> JobType:
        try:
            return QueriesJob.load(uuid_str)
        except Exception:
            pass
        
        try:
            return DataJob.load(uuid_str)
        except Exception as e:
            raise e

    try:
        job_uuid = UUID(uuid_str)
    except Exception:
        raise InvalidUUIDError(uuid_str)
    
    job = _validate_job()
    async with job_lock:
        if job.status not in ["complete", "error_continued", "error_stopped"]:
            job.status = "pending"
            await job_queue.put(job_uuid)
        jobs[job_uuid] = job

    return JobRegisteredResponse(
        uuid_str=uuid_str,
        message="Successfully loaded job!"
    )