from rich import print

from app.common.chats import Chat, ChatMessage

my_chat = Chat(
    complete=False, # defaults to False if left unspecified
    messages=[
        ChatMessage(
            role="system",
            content="You are a helpful assistant."
        ),
        ChatMessage(
            role="user",
            content="What is the capital of France?"
        )
    ]
)

my_chat.generate(
    max_retries=3,
    model_id="gemma-4-26B-A4B-it-Q8_0.gguf", # will default to env variable DEFAULT_MODEL_ID
    append_to_chat=True # defaults to true if unspecified
)

my_chat.add_message(
    message="What is the capital of Germany?",
    role="user"
)

my_chat.add_message(
    message={
        "role": "assistant",
        "content": "The capital of Germany is Berlin."
    }
)

# from ChatMessage
my_chat.add_message(
    message=ChatMessage(
        role="user",
        content="What is the capital of China?"
    )
)

my_chat.generate(max_retries=3)

my_chat.set_system_message("You are an expert in geography.")

print(my_chat)

openai_messages = my_chat.to_openai_chat()

print(openai_messages)

another_chat = Chat.from_openai_chat(openai_messages)

print(another_chat)