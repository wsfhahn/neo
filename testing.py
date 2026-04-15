from app.followups.schemas import Chat
from rich import print


test_chat = Chat.from_openai_chat(
    chat=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Who are you?"},
        {"role": "assistant", "content": "I am a helpful assistant."}
    ]
)

print(test_chat.to_context_string())

followup = test_chat.generate_followup(
    max_reties=3,
    append_to_chat=True
)

print(test_chat.to_context_string())