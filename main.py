from contextlib import asynccontextmanager
from asyncio import create_task
from uuid import UUID, uuid4
from fastapi import FastAPI
from typing import Literal

from app.common.literals import MessageJobStatus, QueriesJobStatus
from app.queries.errors import JobNotQueriesGenerationJobError
from app.common.schemas import (
    InfoResponse,
    JobScheduledResponse,
    JobsList
)
from app.chat.schemas import (
    MessageJob,
    MessageRequest
)
from app.queries.schemas import (
    QueriesGenerationJob,
    QueriesGenerationRequest
)
from app.common.errors import (
    AppError,
    handle_app_error,
    InvalidUUIDError,
    JobNotFoundError
)
from app.common.jobs import (
    jobs,
    job_queue,
    job_lock,
    worker
)
from app.common.file_utils import (
    save_job,
    load_job,
    save_queries_jsonl
)


@asynccontextmanager
async def lifespan(app: FastAPI): # type: ignore
    worker_task = create_task(worker())
    yield


app = FastAPI(
    lifespan=lifespan,
    exception_handlers={
        AppError: handle_app_error # type: ignore
    }
)


@app.get("/ping", response_model=InfoResponse)
async def ping() -> InfoResponse:
    return InfoResponse(message="pong!")


@app.post("/create", response_model=JobScheduledResponse)
async def create_job(payload: MessageRequest | QueriesGenerationRequest) -> JobScheduledResponse:
    uuid = uuid4()
    async with job_lock:
        jobs[uuid] = payload.initialize_job()
        await job_queue.put(uuid)
    
    return JobScheduledResponse(
        message="Job successfully scheduled",
        uuid=str(uuid)
    )


@app.get("/job/{uuid_str}", response_model=MessageJob | QueriesGenerationJob)
async def get_job(uuid_str: str) -> MessageJob | QueriesGenerationJob:
    try:
        uuid = UUID(uuid_str)
    except Exception:
        raise InvalidUUIDError(uuid_str=uuid_str)

    async with job_lock:
        job = jobs.get(uuid)
    
    if not job:
        raise JobNotFoundError(uuid_str=uuid_str)
    
    return job


@app.get("/list", response_model=JobsList)
async def list_jobs() -> JobsList:
    job_statuses: dict[str, MessageJobStatus | QueriesJobStatus] = {}
    for id, job in jobs.items():
        job_statuses[str(id)] = job.status
    
    return JobsList(
        jobs=job_statuses
    )


@app.get("/job/{uuid_str}/save/{format}", response_model=InfoResponse)
async def save_job_endpoint(
    uuid_str: str,
    format: Literal["json", "jsonl"]
) -> InfoResponse:
    try:
        uuid = UUID(uuid_str)
    except Exception as e:
        raise InvalidUUIDError(uuid_str=uuid_str)
    
    async with job_lock:
        job = jobs.get(uuid)
    if not job:
        raise JobNotFoundError(uuid_str=uuid_str)
    
    if format == "json":
        save_job(
            job=job,
            uuid=uuid
        )
    
    if format == "jsonl":
        if not isinstance(job, QueriesGenerationJob):
            raise JobNotQueriesGenerationJobError(uuid_str=uuid_str)
        save_queries_jsonl(
            job=job,
            uuid=uuid
        )

    return InfoResponse(
        message=f"Successfully saved job '{uuid_str}'"
    )


@app.get("/job/{uuid_str}/load", response_model=InfoResponse)
async def load_job_endpoint(uuid_str: str) -> InfoResponse:
    try:
        uuid = UUID(uuid_str)
    except Exception as e:
        raise InvalidUUIDError(uuid_str=uuid_str)
    
    loaded_job = load_job(uuid_str=uuid_str)

    scheduled: bool = False
    async with job_lock:
        jobs[uuid] = loaded_job
        if loaded_job.status not in ["complete", "error"] and uuid not in job_queue._queue: # type: ignore
            await job_queue.put(uuid)
            scheduled = True
    
    if scheduled:
        return InfoResponse(
            message=f"Loaded job '{uuid_str}' and queued it for processing"
        )
    else:
        return InfoResponse(
            message=f"Loaded job '{uuid_str}'"
        )
    