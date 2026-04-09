from uuid import UUID

from app.common.types import JobType
from app.queries.schemas import QueriesGenerationJob, QueriesJSONLEntry
from app.queries.errors import ResponseEmptyError
from app.chat.schemas import MessageJob
from app.common.config import GLOBAL_SETTINGS
from app.common.errors import (
    FileNotFoundError,
    CorruptedSaveFileError
)


def save_job(
    job: JobType,
    uuid: UUID
) -> None:
    save_path = GLOBAL_SETTINGS.save_dir / f"{str(uuid)}.json"
    with open(save_path, 'w') as save_file:
        save_file.write(job.model_dump_json(indent=2))


def load_job(uuid_str: str) -> JobType:
    def validate_job_model(data: str, path_str: str) -> JobType:
        try:
            return MessageJob.model_validate_json(data)
        except Exception:
            pass

        try:
            return QueriesGenerationJob.model_validate_json(data)
        except Exception:
            raise CorruptedSaveFileError(path_str=path_str)

    load_path = GLOBAL_SETTINGS.save_dir / f"{uuid_str}.json"
    if not load_path.exists():
        raise FileNotFoundError(path_str=str(load_path))
    with open(load_path, 'r') as load_file:
        content = load_file.read()
    
    return validate_job_model(content, str(load_path))


def save_queries_jsonl(
    job: QueriesGenerationJob,
    uuid: UUID
) -> None:
    if not job.response:
        raise ResponseEmptyError(uuid_str=str(uuid))
    save_path = GLOBAL_SETTINGS.save_dir / f"{str(UUID)}.jsonl"
    with open(save_path, 'w') as save_file:
        for response in job.response:
            category = response.category
            for query in response.queries:
                jsonl_entry = QueriesJSONLEntry(
                    category=category,
                    number=query.number,
                    query=query.query
                )
                save_file.write(jsonl_entry.model_dump_json())