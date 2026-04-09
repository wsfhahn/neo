from contextlib import asynccontextmanager
from asyncio import create_task
from uuid import UUID, uuid4
from fastapi import FastAPI
from typing import Literal

from app.common.literals import MessageJobStatus, IterableJobStatus
from app.common.types import JobType, JobRequestType
from app.queries.schemas import QueriesGenerationJob
from app.responses.schemas import ResponsesGenerationJob
from app.common.schemas import (
    InfoResponse,
    JobScheduledResponse,
    JobsList
)
from app.common.errors import (
    AppError,
    handle_app_error,
    InvalidUUIDError,
    JobNotFoundError,
    JobNotIterativeError
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
    save_queries_job_jsonl,
    save_responses_job_jsonl
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
async def create_job(payload: JobRequestType) -> JobScheduledResponse:
    uuid = uuid4()
    async with job_lock:
        jobs[uuid] = payload.initialize_job()
        await job_queue.put(uuid)
    
    return JobScheduledResponse(
        message="Job successfully scheduled",
        uuid=str(uuid)
    )


@app.get("/job/{uuid_str}", response_model=JobType)
async def get_job(uuid_str: str) -> JobType:
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
    job_statuses: dict[str, MessageJobStatus | IterableJobStatus] = {}
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
        
        if format == "jsonl" and isinstance(job, QueriesGenerationJob):
            save_queries_job_jsonl(
                job=job,
                uuid=uuid
            )
        elif format == "jsonl" and isinstance(job, ResponsesGenerationJob):
            save_responses_job_jsonl(
                job=job,
                uuid=uuid
            )
        else:
            raise JobNotIterativeError(uuid_str=uuid_str)

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
    
    
    return InfoResponse(
        message=f"Loaded job '{uuid_str}' and queued it for processing" if scheduled else f"Loaded job '{uuid_str}'"
    )
    