from typing import Literal


MessageJobStatus = Literal[
    "pending",
    "running",
    "complete",
    "error"
]


QueriesJobStatus = Literal[
    "pending",
    "running",
    "complete",
    "error_stopped",
    "error_continued"
]