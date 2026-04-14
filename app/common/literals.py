from typing import Literal

IterableJobStatus = Literal[
    "pending",
    "running",
    "complete",
    "error_stopped",
    "error_continued"
]