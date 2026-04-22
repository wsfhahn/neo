from __future__ import annotations

from pydantic import BaseModel, ValidationError, Field
from typing import TypeVar, overload, Any, get_args
from openai.types.chat import ChatCompletionMessageParam
from copy import deepcopy

from app.common.literals import MessageRole
from app.common.errors import InvalidMessageContent, InvalidMessageRole, GenerationError
from app.common.config import GLOBAL_CLIENT, GLOBAL_SETTINGS
from app.common.prompts import CONTEXT_STRING_MESSAGE, FOLLOWUP_GENERATOR_SYSTEM_PROMPT


class FollowUpResponse(BaseModel):
    """A follow-up written by the follow-up generator."""
    followup: str = Field(..., description="The single follow-up")

    def to_chat_message(self) -> ChatMessage:
        return ChatMessage(
            role="user",
            content=self.followup
        )


T_BaseModel = TypeVar("T_BaseModel", bound=BaseModel)


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    reasoning_content: str | None = None

    def model_post_init(self, __context: Any) -> None:
        if len(self.content) == 0:
            raise InvalidMessageContent("the message content cannot be empty")

    def to_openai_chat_param(self) -> ChatCompletionMessageParam:
        match self.role:
            case "user":
                return {"role": "user", "content": self.content}
            case "assistant":
                return {"role": "assistant", "content": self.content}
            case "system":
                return {"role": "system", "content": self.content}
    
    @classmethod
    def from_openai_chat_param(cls, message: ChatCompletionMessageParam) -> "ChatMessage":
        if message["role"] not in get_args(MessageRole):
            raise InvalidMessageRole(
                role=message["role"],
                reason="message role must be one of 'user', 'assistant', 'system'"
            )
        if not isinstance(message["content"], str):
            raise InvalidMessageContent("only str message content is supported at this time")
        return ChatMessage(
            role=message["role"], # type: ignore[arg-type]
            content=message["content"]
        )

class Chat(BaseModel):
    complete: bool = False
    messages: list[ChatMessage]

    def model_post_init(self, __context: Any) -> None:
        for i, message in enumerate(self.messages):
            if i != 0 and message.role == "system":
                raise InvalidMessageRole(
                    role="system",
                    reason="system message can only appear at the first index of chat"
                )
            
    @property
    def context_string(self) -> str:
        if len(self.messages) == 0:
            raise InvalidMessageContent("must have at least on message to create context string")
        out = ""
        for message in self.messages:
            out += CONTEXT_STRING_MESSAGE.format(
                role=message.role,
                content=message.content.strip()
            )
        return out.strip()
    
    def to_openai_chat(self) -> list[ChatCompletionMessageParam]:
        out: list[ChatCompletionMessageParam] = []
        for message in self.messages:
            out.append(message.to_openai_chat_param())
        return out
    
    @property
    def length(self) -> int:
        return len([m for m in self.messages if m.role == "assistant"])
    
    @classmethod
    def from_openai_chat(cls, chat: list[ChatCompletionMessageParam]) -> "Chat":
        messages: list[ChatMessage] = []
        for message in chat:
            messages.append(ChatMessage.from_openai_chat_param(message))
        return Chat(
            complete=False,
            messages=messages
        )
    
    def set_system_message(self, message: str | ChatMessage | ChatCompletionMessageParam) -> None:
        def _set_system(message: ChatMessage) -> None:
            if len(self.messages) == 0:
                self.messages = [message]
            elif self.messages[0].role == "system":
                self.messages[0] = message
            else:
                self.messages.insert(0, message)
        if isinstance(message, str):
            _set_system(ChatMessage(
                role="system",
                content=message
            ))
        elif isinstance(message, dict):
            if message["role"] != "system":
                raise InvalidMessageRole(
                    role=message["role"],
                    reason="to set systen, message role must be 'system'"
                )
            _set_system(ChatMessage.from_openai_chat_param(message))
        elif isinstance(message, ChatMessage):
            if message.role != "system":
                raise InvalidMessageRole(
                    role=message.role,
                    reason="to set system, message role must be 'system'"
                )
            _set_system(message)

    def duplicate_with_system_message(self, message: str | ChatMessage | ChatCompletionMessageParam) -> "Chat":
        chat_copy = deepcopy(self)
        chat_copy.set_system_message(message)
        return chat_copy

    def add_message(
        self,
        message: str | ChatMessage | ChatCompletionMessageParam,
        role: MessageRole | None = None
    ) -> None:
        if isinstance(message, str):
            if not role:
                raise InvalidMessageRole(
                    role="none",
                    reason="to add message from str, you must set the role"
                )
            elif role == "system":
                raise InvalidMessageRole(
                    role="system",
                    reason="to set system message, call set_system_message"
                )
            self.messages.append(ChatMessage(
                role=role,
                content=message
            ))
        elif isinstance(message, dict):
            if message["role"] == "system":
                raise InvalidMessageRole(
                    role="system",
                    reason="to set system message, call set_system_message"
                )
            self.messages.append(ChatMessage.from_openai_chat_param(message))
        elif isinstance(message, ChatMessage):
            if message.role == "system":
                raise InvalidMessageRole(
                    role="system",
                    reason="to set system message, call set_system_message"
                )
            self.messages.append(message)

    @overload
    def generate(
        self,
        max_retries: int,
        model_id: str = GLOBAL_SETTINGS.default_model_id,
        append_to_chat: bool = True,
        response_model: None = None
    ) -> ChatMessage:
        ...

    @overload
    def generate(
        self,
        max_retries: int,
        model_id: str = GLOBAL_SETTINGS.default_model_id,
        append_to_chat: bool = True,
        response_model: type[T_BaseModel] = ...
    ) -> T_BaseModel:
        ...
    
    def generate(
        self,
        max_retries: int,
        model_id: str = GLOBAL_SETTINGS.default_model_id,
        append_to_chat: bool = True,
        response_model: None | type[T_BaseModel] = None
    ) -> ChatMessage | T_BaseModel:
        openai_chat = self.to_openai_chat()
        kwargs: dict[str, Any] = {
            "messages": openai_chat,
            "model": model_id,
            "temperature": GLOBAL_SETTINGS.temperature,
            "extra_body": {
                "top_k": GLOBAL_SETTINGS.top_k,
                "top_p": GLOBAL_SETTINGS.top_p,
                "min_p": GLOBAL_SETTINGS.min_p
            }
        }
        retry = 0
        while True:
            try:
                if response_model:
                    kwargs["response_format"] = response_model
                    raw_response = GLOBAL_CLIENT.chat.completions.parse(**kwargs)
                else:
                    raw_response = GLOBAL_CLIENT.chat.completions.create(**kwargs)
                
                message = raw_response.choices[0].message
                content = message.content
                reasoning_content = getattr(message, "reasoning_content", None)
                refusal = message.refusal

                if refusal: raise GenerationError(f"API refused request: {refusal}")
                if not content: raise GenerationError("API returned empty response content")

                new_message = ChatMessage(
                    role="assistant",
                    content=content,
                    reasoning_content=reasoning_content
                )

                if response_model:
                    try:
                        output: ChatMessage | T_BaseModel = response_model.model_validate_json(content)
                    except ValidationError:
                        raise GenerationError("Model failed to adhere to output format")
                else:
                    output = new_message

                if append_to_chat:
                    self.add_message(new_message)
                
                return output
            except Exception as e:
                if retry < max_retries:
                    print(f"Hit retry {retry}... continuing")
                    retry += 1
                    continue
                raise e
            
    def generate_followup(
        self,
        max_retries: int,
        model_id: str = GLOBAL_SETTINGS.default_model_id,
        append_to_chat: bool = True
    ) -> FollowUpResponse:
        context_string = self.context_string
        followup_chat = Chat(
            complete=False,
            messages=[
                ChatMessage(
                    role="system",
                    content=FOLLOWUP_GENERATOR_SYSTEM_PROMPT
                ),
                ChatMessage(
                    role="user",
                    content=context_string
                )
            ]
        )
        followup = followup_chat.generate(
            max_retries=max_retries,
            model_id=model_id,
            append_to_chat=False,
            response_model=FollowUpResponse
        )

        if append_to_chat: self.add_message(followup.to_chat_message())
        return followup
    

class ChatJSONLEntry(BaseModel):
    messages: list[ChatMessage]