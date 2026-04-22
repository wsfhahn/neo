from uuid import UUID
from asyncio import to_thread
from pathlib import Path

from app.common.types import JobType
from app.common.config import GLOBAL_SETTINGS
from app.common.errors import CorrupedSaveFileError, SaveFileNotFoundError
from app.common.jobs import jobs, job_queue, job_lock
from app.queries.schemas import QueriesJob
from app.data.schemas import DataJob


def _validate_job(content: str, path_str: str) -> JobType:
    try: return QueriesJob.model_validate_json(content)
    except Exception: pass

    try: return DataJob.model_validate_json(content)
    except Exception: pass

    raise CorrupedSaveFileError(path_str)


def load_job(uuid: UUID) -> JobType:
    load_path = GLOBAL_SETTINGS.save_dir / f"{str(uuid)}.json"
    if not load_path.exists():
        raise SaveFileNotFoundError(str(load_path))
    with open(load_path, 'r') as load_file:
        content = load_file.read()
    return _validate_job(content, str(load_path))


async def load_and_add_job(uuid: UUID) -> None:
    job = await to_thread(load_job, uuid)
    async with job_lock:
        if job.status not in ["complete", "error_stopped", "error_continued"]:
            await job_queue.put(uuid)
        jobs[uuid] = job


async def startup_load_jobs() -> None:
    for item in Path.iterdir(GLOBAL_SETTINGS.save_dir):
        if item.is_file() and item.suffix == ".json":
            try:
                uuid = UUID(item.stem)
                await load_and_add_job(uuid)
            except Exception:
                continue


async def shutdown_save_jobs() -> None:
    for uuid, job in jobs.items():
        job.save(str(uuid), "json")