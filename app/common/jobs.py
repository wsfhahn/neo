from asyncio import Queue, Lock, to_thread
from uuid import UUID

from app.chat.schemas import MessageJob
from app.chat.generation import run_message_job


jobs: dict[UUID, MessageJob] = {}
job_queue: Queue[UUID] = Queue()
job_lock = Lock()


async def worker() -> None:
    while True:
        try:
            next_job_id = await job_queue.get()
            if not next_job_id:
                continue

            async with job_lock:
                job = jobs[next_job_id]
                job.status = "running"
            
            result = await to_thread(run_message_job, job)

            async with job_lock:
                jobs[next_job_id] = result
        except Exception as e:
            raise e