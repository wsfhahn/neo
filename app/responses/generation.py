from openai.types.chat import ChatCompletionMessageParam
from uuid import UUID

from app.responses.schemas import ResponsesGenerationJob, ResponsesResponse
from app.common.file_utils import queries_jsonl_iterator
from app.common.config import GLOBAL_SETTINGS, GLOBAL_CLIENT
from app.common.errors import GenerationError


def run_responses_job(job: ResponsesGenerationJob) -> ResponsesGenerationJob:
    output: list[ResponsesResponse] = []

    error_detail: str | None = None

    for query in queries_jsonl_iterator(UUID(job.queries_uuid_str)):
        if job.system:
            chat: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": job.system},
                {"role": "user", "content": query.query}
            ]
        else:
            chat = [
                {"role": "user", "content": query.query}
            ]
        
        retry = 0
        while True:
            try:
                raw_response = GLOBAL_CLIENT.chat.completions.create(
                    messages=chat,
                    model=GLOBAL_SETTINGS.model_id,
                    temperature=GLOBAL_SETTINGS.temperature,
                    extra_body={
                        "top_k": GLOBAL_SETTINGS.top_k,
                        "top_p": GLOBAL_SETTINGS.top_p,
                        "min_p": GLOBAL_SETTINGS.min_p
                    }
                )

                response = raw_response.choices[0].message.content
                refusal = raw_response.choices[0].message.refusal

                if not response:
                    if refusal:
                        raise GenerationError(
                            reason=f"response refusal for query: {query.query}"
                        )
                    raise GenerationError(
                        reason=f"model returned empty message for query: {query.query}"
                    )
                
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
                    return ResponsesGenerationJob(
                        system=job.system,
                        queries_uuid_str=job.queries_uuid_str,
                        max_retries=job.max_retries,
                        on_error=job.on_error,
                        status="error_stopped",
                        error_detail=str(e),
                        response=output
                    )
                elif job.on_error == "continue":
                    error_detail = str(e)
                    break
    
    return ResponsesGenerationJob(
        system=job.system,
        queries_uuid_str=job.queries_uuid_str,
        max_retries=job.max_retries,
        on_error=job.on_error,
        status="error_continued" if error_detail else "complete",
        error_detail=error_detail,
        response=output
    )