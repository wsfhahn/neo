from openai.types.chat import ChatCompletionMessageParam
from openai import APIConnectionError, AuthenticationError
from pydantic import BaseModel, ValidationError
from typing import Any, Literal

from app.common.config import GLOBAL_SETTINGS, GLOBAL_CLIENT
from app.common.errors import GenerationError


def generate_response(
    user_message: str,
    system_message: str | None = None,
    response_format: type[BaseModel] | None = None,
    model_id: str | None = None
) -> str | BaseModel:
    chat: list[ChatCompletionMessageParam] = []
    if system_message:
        chat.append({"role": "system", "content": system_message})
    chat.append({"role": "user", "content": user_message})

    request_kwargs: dict[str, Any] = {
        "messages": chat,
        "model": model_id if model_id else GLOBAL_SETTINGS.model_id,
        "temperature": GLOBAL_SETTINGS.temperature,
        "extra_body": {
            "top_k": GLOBAL_SETTINGS.top_k,
            "top_p": GLOBAL_SETTINGS.top_p,
            "min_p": GLOBAL_SETTINGS.min_p
        }
    }
    if response_format: request_kwargs["response_format"] = response_format

    try:
        if response_format:
            raw_response = GLOBAL_CLIENT.chat.completions.parse(**request_kwargs)
        else:
            raw_response = GLOBAL_CLIENT.chat.completions.create(**request_kwargs)
        
        response = raw_response.choices[0].message.content
        refusal = raw_response.choices[0].message.refusal

        if refusal:
            raise GenerationError(f"API refused request: {refusal}")
        if not response:
            raise GenerationError("model response is 'None' or otherwise empty")
        
        if response_format:
            return response_format.model_validate_json(response)
        return response
    except ValidationError:
        raise GenerationError("model failed to adhere to response format model")
    except APIConnectionError:
        raise GenerationError(f"failed to connect to completions api at {GLOBAL_SETTINGS.api_host}")
    except AuthenticationError:
        raise GenerationError("auth token is no longer valid")