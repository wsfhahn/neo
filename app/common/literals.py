from typing import Literal


MessageJobStatus = Literal[
    "pending",
    "running",
    "complete",
    "error"
]


IterableJobStatus = Literal[
    "pending",
    "running",
    "complete",
    "error_stopped",
    "error_continued"
]