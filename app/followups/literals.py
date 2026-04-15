from typing import Literal


Role = Literal[
    "user",
    "assistant",
    "system"
]

ChatStatus = Literal[
    "live",
    "complete",
    "error_stopped",
    "error_continued"
]