from asyncio import Queue, Lock, to_thread
from uuid import UUID

from app.chat.schemas import MessageJob
from app.queries.schemas import QueriesGenerationJob
from app.responses.schemas import ResponsesGenerationJob
from app.common.types import JobType
from app.chat.generation import run_message_job
from app.queries.generation import run_queries_job
from app.responses.generation import run_responses_job


jobs: dict[UUID, JobType] = {}
job_queue: Queue[UUID] = Queue()
job_lock = Lock()


async def worker() -> None:
    """The primary worker for the project.
    
    This worker scans a job queue, consuming the next pending job, kicking off processing, and storing the result."""

    while True:
        try:
            next_job_id = await job_queue.get()
            if not next_job_id:
                continue

            async with job_lock:
                job = jobs[next_job_id]
                job.status = "running"
            
            if isinstance(job, MessageJob):
                result: JobType = await to_thread(run_message_job, job)
            elif isinstance(job, QueriesGenerationJob):
                result = await to_thread(run_queries_job, job)
            elif isinstance(job, ResponsesGenerationJob):
                result = await to_thread(run_responses_job, job)

            async with job_lock:
                jobs[next_job_id] = result
        except Exception as e:
            raise e