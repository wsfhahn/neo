from app.common.literals import IterableJobStatus
from app.common.generation import generate_response
from app.queries.prompts import QUERY_GENERATOR_SYSTEM_PROMPT
from app.queries.schemas import QueriesGenerationJob, QueriesResponse, ModelQueriesResponse


def run_queries_job(job: QueriesGenerationJob) -> QueriesGenerationJob:
    """Run a queries job and return the completed job."""

    output: list[QueriesResponse] = []
    error_detail: str | None = None
    def _to_job(stopped: bool = False) -> QueriesGenerationJob:
        if stopped: status: IterableJobStatus = "error_stopped"
        elif error_detail: status = "error_continued"
        else: status = "complete"
        return QueriesGenerationJob(
            categories=job.categories,
            queries_per_category=job.queries_per_category,
            max_retries=job.max_retries,
            on_error=job.on_error,
            model_id=job.model_id,
            status=status,
            error_detail=error_detail,
            response=output if len(output) != 0 else None
        )
    for category in job.categories:
        retry = 0
        while True:
            try:
                response = generate_response(
                    user_message=category,
                    system_message=QUERY_GENERATOR_SYSTEM_PROMPT,
                    response_format=ModelQueriesResponse,
                    model_id=job.model_id
                )
                assert isinstance(response, ModelQueriesResponse)
                output.append(QueriesResponse(
                    category=category,
                    queries=response.queries
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