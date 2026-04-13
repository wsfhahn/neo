from uuid import UUID
from typing import Iterator

from app.common.types import JobType
from app.queries.schemas import QueriesGenerationJob, QueriesJSONLEntry
from app.responses.schemas import ResponsesGenerationJob
from app.common.config import GLOBAL_SETTINGS
from app.common.errors import (
    FileNotFoundError,
    CorruptedSaveFileError,
    ResponseEmptyError
)


def save_job(
    job: JobType,
    job_uuid: UUID
) -> None:
    """Save a job to a .json file named by the UUID."""

    save_path = GLOBAL_SETTINGS.save_dir / f"{str(job_uuid)}.json"
    with open(save_path, 'w') as save_file:
        save_file.write(job.model_dump_json(indent=2))


def load_job(uuid_str: str) -> JobType:
    """Load a job from a .json file by the UUID."""

    def validate_job_model(data: str, path_str: str) -> JobType:
        try:
            return QueriesGenerationJob.model_validate_json(data)
        except Exception:
            pass

        try:
            return ResponsesGenerationJob.model_validate_json(data)
        except Exception:
            raise CorruptedSaveFileError(path_str=path_str)

    load_path = GLOBAL_SETTINGS.save_dir / f"{uuid_str}.json"
    if not load_path.exists():
        raise FileNotFoundError(path_str=str(load_path))
    with open(load_path, 'r') as load_file:
        content = load_file.read()
    
    return validate_job_model(content, str(load_path))


def queries_jsonl_iterator(job_uuid: UUID) -> Iterator[QueriesJSONLEntry]:
    load_path = GLOBAL_SETTINGS.save_dir / f"{str(job_uuid)}.jsonl"
    if not load_path.exists():
        raise FileNotFoundError(path_str=str(load_path))
    with open(load_path, 'r') as load_file:
        for entry in load_file.readlines():
            try:
                loaded = QueriesJSONLEntry.model_validate_json(entry)
                yield loaded
            except Exception:
                raise CorruptedSaveFileError(path_str=str(load_path))