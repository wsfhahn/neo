from app.common.chats import Chat, ChatMessage
from app.common.config import GLOBAL_SETTINGS


test_chat = Chat(
    complete=False,
    messages=[
        ChatMessage(
            role="system",
            content="You are a helpful assistant."
        ),
        ChatMessage(
            role="user",
            content="Who are you?"
        )
    ]
)

test_chat.generate(
    max_retries=3,
    model_id=GLOBAL_SETTINGS.default_model_id,
    append_to_chat=True
)

print(test_chat.messages[2])