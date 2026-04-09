from typing import Union

from app.queries.schemas import QueriesGenerationJob
from app.chat.schemas import MessageJob


JobType = Union[QueriesGenerationJob, MessageJob]