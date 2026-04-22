from uuid import UUID

from app.common.types import JobType
from app.common.config import GLOBAL_SETTINGS
from app.common.errors import CorrupedSaveFileError, SaveFileNotFoundError
from app.queries.schemas import QueriesJob
from app.data.schemas import DataJob


def load_job(uuid: UUID) -> JobType:
    def _validate_job(content: str, path_str: str) -> JobType:
        try: return QueriesJob.model_validate_json(content)
        except Exception: pass

        try: return DataJob.model_validate_json(content)
        except Exception: pass

        raise CorrupedSaveFileError(path_str)
    
    load_path = GLOBAL_SETTINGS.save_dir / f"{str(uuid)}.json"
    if not load_path.exists():
        raise SaveFileNotFoundError(str(load_path))
    with open(load_path, 'r') as load_file:
        content = load_file.read()
    return _validate_job(
        content=content,
        path_str=str(load_path)
    )