from asyncio import Queue, Lock, to_thread
from uuid import UUID

from app.common.types import JobType
from app.queries.schemas import QueriesJob
from app.data.schemas import DataJob
from app.queries.generation import run_queries_job
from app.data.generation import run_data_job


jobs: dict[UUID, JobType] = {}
job_lock = Lock()
job_queue: Queue[UUID] = Queue()


async def worker() -> None:
    while True:
        try:
            next_job_uuid = await job_queue.get()
            if not next_job_uuid:
                continue
            async with job_lock:
                next_job = jobs[next_job_uuid]
                jobs[next_job_uuid].status = "running"
            if isinstance(next_job, QueriesJob):
                result: JobType = await to_thread(run_queries_job, next_job)
            if isinstance(next_job, DataJob):
                result = await to_thread(run_data_job, next_job)
            async with job_lock:
                jobs[next_job_uuid] = result
        except Exception as e:
            raise e