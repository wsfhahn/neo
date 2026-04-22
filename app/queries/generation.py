from app.queries.schemas import QueriesJob, QueriesResponse
from app.common.chats import Chat, ChatMessage
from app.common.prompts import QUERIES_GENERATOR_SYSTEM_PROMPT
from app.common.literals import JobStatus


def run_queries_job(job: QueriesJob) -> QueriesJob:
    def _to_job(stopped: bool = False) -> QueriesJob:
        if stopped: status: JobStatus = "error_stopped"
        elif error_detail: status = "error_continued"
        else: status = "complete"
        return QueriesJob(
            categories=job.categories,
            queries_per_category=job.queries_per_category,
            max_retries=job.max_retries,
            on_error=job.on_error,
            model_id=job.model_id,
            status=status,
            error_detail=error_detail,
            result=responses
        )

    responses: list[QueriesResponse] = []
    error_detail: str | None = None
    for category in job.categories:
        category_chat = Chat(
            messages=[
                ChatMessage(
                    role="system",
                    content=QUERIES_GENERATOR_SYSTEM_PROMPT.format(n=job.queries_per_category)
                ),
                ChatMessage(
                    role="user",
                    content=category
                )
            ]
        )
        try:
            response = category_chat.generate(
                max_retries=job.max_retries,
                model_id=job.model_id,
                append_to_chat=False,
                response_model=QueriesResponse
            )
            responses.append(response)
        except Exception as e:
            error_detail = str(e)
            if job.on_error == "stop":
                return _to_job(stopped=True)
            elif job.on_error == "continue":
                continue
    return _to_job()