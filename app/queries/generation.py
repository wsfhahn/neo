from openai.types.chat import ChatCompletionMessageParam
from pydantic import ValidationError

from app.common.errors import GenerationError
from app.common.config import GLOBAL_CLIENT, GLOBAL_SETTINGS
from app.queries.prompts import QUERY_GENERATOR_SYSTEM_PROMPT
from app.queries.schemas import (
    ModelQueriesResponse,
    QueriesGenerationJob,
    QueriesResponse
)


def run_queries_job(job: QueriesGenerationJob) -> QueriesGenerationJob:
    """Run a queries job and return the completed job."""

    output: list[QueriesResponse] = []

    for category in job.categories:
        chat: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": QUERY_GENERATOR_SYSTEM_PROMPT.format(n=job.queries_per_category)},
            {"role": "user", "content": category}
        ]

        error_detail: str | None = None

        retry = 0
        while True:
            try:
                raw_response = GLOBAL_CLIENT.chat.completions.parse(
                    messages=chat,
                    model=GLOBAL_SETTINGS.model_id,
                    temperature=GLOBAL_SETTINGS.temperature,
                    extra_body={
                        "top_k": GLOBAL_SETTINGS.top_k,
                        "top_p": GLOBAL_SETTINGS.top_p,
                        "min_p": GLOBAL_SETTINGS.min_p
                    },
                    response_format=ModelQueriesResponse
                )

                response = raw_response.choices[0].message.content
                refusal = raw_response.choices[0].message.refusal

                if not response:
                    if refusal:
                        raise GenerationError(
                            reason=f"model refused to generate queries for category {category}: {refusal}"
                        )
                    raise GenerationError(
                        reason="model response was empty"
                    )
                
                try:
                    loaded = ModelQueriesResponse.model_validate_json(response)
                except ValidationError as e:
                    raise GenerationError(
                        reason=f"model failed to adhere to output schema: {e}"
                    )
                output.append(QueriesResponse(
                    category=category,
                    queries=loaded.queries
                ))
                break
            except Exception as e:
                if retry < job.max_retries:
                    retry += 1
                    continue

                if job.on_error == "stop":
                    return QueriesGenerationJob(
                        categories=job.categories,
                        queries_per_category=job.queries_per_category,
                        max_retries=job.max_retries,
                        on_error=job.on_error,
                        status="error_stopped",
                        error_detail=str(e),
                        response=output
                    )
                elif job.on_error == "continue":
                    error_detail = str(e)
                    break
    
    return QueriesGenerationJob(
        categories=job.categories,
        queries_per_category=job.queries_per_category,
        max_retries=job.max_retries,
        on_error=job.on_error,
        status="error_continued" if error_detail else "complete",
        error_detail=error_detail,
        response=output
    )