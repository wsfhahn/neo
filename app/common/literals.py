from typing import Literal


JobStatus = Literal[
    "pending",
    "running",
    "complete",
    "error_stopped",
    "error_continued"
]

OnError = Literal["stop", "continue"]

MessageRole = Literal[
    "user",
    "assistant",
    "system"
]

SaveFormat = Literal["json", "jsonl"]