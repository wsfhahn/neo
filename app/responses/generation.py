from openai.types.chat import ChatCompletionMessageParam
from uuid import UUID

from app.responses.schemas import ResponsesGenerationJob, ResponsesResponse
from app.common.file_utils import queries_jsonl_iterator
from app.common.config import GLOBAL_SETTINGS, GLOBAL_CLIENT
from app.common.errors import GenerationError
from app.common.literals import IterableJobStatus
from app.common.generation import generate_response


def run_responses_job(job: ResponsesGenerationJob) -> ResponsesGenerationJob:
    output: list[ResponsesResponse] = []
    error_detail: str | None = None
    def _to_job(stopped: bool = False) -> ResponsesGenerationJob:
        if stopped: status: IterableJobStatus = "error_stopped"
        elif error_detail: status = "error_continued"
        else: status = "complete"
        return ResponsesGenerationJob(
            system=job.system,
            queries_uuid_str=job.queries_uuid_str,
            max_retries=job.max_retries,
            on_error=job.on_error,
            model_id=job.model_id,
            status=status,
            error_detail=error_detail,
            response=output if len(output) != 0 else None
        )
    for query in queries_jsonl_iterator(UUID(job.queries_uuid_str)):
        retry = 0
        while True:
            try:
                response = generate_response(
                    user_message=query.query
                )
                assert isinstance(response, str)
                output.append(ResponsesResponse(
                    number=query.number,
                    category=query.category,
                    query=query.query,
                    content=response
                ))
                break
            except Exception as e:
                if retry < job.max_retries:
                    retry += 1
                    continue
                if job.on_error == "stop":
                    error_detail = str(e)
                    return _to_job(stopped=True)
                if job.on_error == "continue":
                    error_detail = str(e)
                    break
    
    return _to_job()