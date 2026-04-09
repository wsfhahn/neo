from openai.types.chat import ChatCompletionMessageParam

from app.common.errors import GenerationError
from app.chat.schemas import MessageJob
from app.common.config import (
    GLOBAL_CLIENT,
    GLOBAL_SETTINGS
)


def run_message_job(job: MessageJob) -> MessageJob:
    """Process a MessageJob and return the completed job."""

    system = job.system
    user = job.user

    chat: list[ChatCompletionMessageParam] = []
    if system:
        chat.append({
            "role": "system",
            "content": system
        })
    chat.append({
        "role": "user",
        "content": user
    })

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
                    reason=f"message was refused: {refusal}"
                )
            raise GenerationError(
                reason="model response is empty"
            )
        
        return MessageJob(
            system=job.system,
            user=job.user,
            status="complete",
            error_detail=None,
            response=response
        )
    except Exception as e:
        return MessageJob(
            system=job.system,
            user=job.user,
            status="error",
            error_detail=str(e),
            response=None
        )
        