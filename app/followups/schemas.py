from __future__ import annotations

from openai.types.chat import ChatCompletionMessageParam
from openai import APIConnectionError, AuthenticationError
from pydantic import BaseModel, Field, ValidationError
from typing import Any, get_args, TypeVar, overload

from app.common.config import GLOBAL_CLIENT, GLOBAL_SETTINGS
from app.followups.strings import CONTEXT_MESSAGE
from app.followups.literals import Role, ChatStatus
from app.followups.prompts import FOLLOWUP_GENERATOR_SYSTEM_PROMPT
from app.common.errors import (
    GenerationError,
    InvalidModelIDError
)
from app.followups.errors import (
    MessageRoleError,
    UnsupportedMessageContentError,
    BadMessageOrderError,
    ChatEmptyError
)


T_BaseModel = TypeVar("T_BaseModel", bound=BaseModel)

class Followup(BaseModel):
    """A followup query written by the followup generator."""
    followup: str = Field(..., description="The single followup query")

    def to_chat_message(self) -> ChatMessage:
        return ChatMessage(
            role="user",
            content=self.followup
        )

class ChatMessage(BaseModel):
    role: Role
    content: str

    def to_openai_chat_param(self) -> ChatCompletionMessageParam:
        match self.role:
            case "user":
                return {"role": "user", "content": self.content}
            case "assistant":
                return {"role": "assistant", "content": self.content}
            case "system":
                return {"role": "system", "content": self.content}
    
    @classmethod
    def from_openai_chat_param(self, message: ChatCompletionMessageParam) -> ChatMessage:
        if message["role"] not in get_args(Role):
            raise MessageRoleError(
                role=message["role"],
                reason="message role must be one of 'user', 'assistant', 'system'"
            )
        
        if not isinstance(message["content"], str):
            raise UnsupportedMessageContentError(
                reason="message content must be type 'str'"
            )
        
        return ChatMessage(
            role=message["role"], # type: ignore[arg-type]
            content=message["content"]
        )
    

class Chat(BaseModel):
    messages: list[ChatMessage]

    def to_openai_chat(self) -> list[ChatCompletionMessageParam]:
        out: list[ChatCompletionMessageParam] = []
        for message in self.messages:
            out.append(message.to_openai_chat_param())
        return out
    
    @classmethod
    def from_openai_chat(self, chat: list[ChatCompletionMessageParam]) -> Chat:
        messages: list[ChatMessage] = []
        for i, message in enumerate(chat):
            if i != 0 and message["role"] == "system":
                raise BadMessageOrderError(reason="system message must be first message in chat")
            messages.append(ChatMessage.from_openai_chat_param(message))
        
        return Chat(messages=messages)
    
    def to_context_string(self) -> str:
        output = ""
        for message in self.messages:
            output += CONTEXT_MESSAGE.format(role=message.role, message=message.content)
        return output.strip()
    
    def set_system_message(self, message: str | ChatMessage) -> None:
        if isinstance(message, ChatMessage) and message.role != "system":
            raise MessageRoleError(
                role=message.role,
                reason="message role must be 'system' to set chat system message"
            )
        if isinstance(message, str):
            message = ChatMessage(
                role="system",
                content=message
            )
        if self.messages[0].role == "system":
            self.messages[0] = message
        else:
            self.messages.insert(0, message)

    @overload
    def generate(
        self,
        model_id: str | None = None,
        append_to_chat: bool = True,
        response_format: None = None
    ) -> ChatMessage:
        ...

    @overload
    def generate(
        self,
        model_id: str | None = None,
        append_to_chat: bool = True,
        response_format: type[T_BaseModel] = ...
    ) -> T_BaseModel:
        ...

    def generate(
        self,
        model_id: str | None = None,
        append_to_chat: bool = True,
        response_format: type[BaseModel] | None = None
    ) -> ChatMessage | BaseModel:
        if model_id and model_id not in [m.id for m in GLOBAL_CLIENT.models.list()]:
            raise InvalidModelIDError(model_id=model_id)
        if len(self.messages) == 0:
            raise ChatEmptyError
        if self.messages[-1].role != "user":
            raise MessageRoleError(
                role=self.messages[-1].role,
                reason="final message in chat role must be 'user' to generate response"
            )

        chat = self.to_openai_chat()
        kwargs: dict[str, Any] = {
            "messages": chat,
            "model": model_id if model_id else GLOBAL_SETTINGS.model_id,
            "temperature": GLOBAL_SETTINGS.temperature,
            "extra_body": {
                "top_k": GLOBAL_SETTINGS.top_k,
                "top_p": GLOBAL_SETTINGS.top_p,
                "min_p": GLOBAL_SETTINGS.min_p
            }
        }

        try:
            if response_format:
                kwargs["response_format"] = response_format
                raw_response = GLOBAL_CLIENT.chat.completions.parse(**kwargs)
            else:
                raw_response = GLOBAL_CLIENT.chat.completions.create(**kwargs)
            
            content = raw_response.choices[0].message.content
            refusal = raw_response.choices[0].message.refusal

            if refusal:
                raise GenerationError(
                    reason=f"API refused request: {refusal}"
                )
            if not content:
                raise GenerationError(
                    reason="model response is 'None'"
                )

            if append_to_chat:
                self.messages.append(ChatMessage(
                    role="assistant",
                    content=content.strip()
                ))
            
            if response_format:
                return response_format.model_validate_json(content)
            return ChatMessage(
                role="assistant",
                content=content
            )
        except APIConnectionError:
            raise GenerationError(f"the host '{GLOBAL_SETTINGS.api_host}' is no longer reachable")
        except AuthenticationError:
            raise GenerationError("the API key is no longer valid")
        except ValidationError:
            raise GenerationError("the model failed to adhere to the output schema")
        
    def generate_followup(
        self,
        max_reties: int,
        model_id: str | None = None,
        append_to_chat: bool = True
    ) -> ChatMessage | None:
        followup_chat = Chat(
            messages=[
                ChatMessage(
                    role="system",
                    content=FOLLOWUP_GENERATOR_SYSTEM_PROMPT
                ),
                ChatMessage(
                    role="user",
                    content=self.to_context_string()
                )
            ]
        )
        retry = 0
        while True:
            try:
                followup = followup_chat.generate(
                    model_id=model_id if model_id else GLOBAL_SETTINGS.model_id,
                    append_to_chat=False,
                    response_format=Followup
                ).to_chat_message()
                if append_to_chat:
                    self.messages.append(followup)
                return followup
            except Exception:
                if retry < max_reties:
                    retry += 1
                    continue
                return None