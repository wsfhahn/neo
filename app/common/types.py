from typing import Union

from app.queries.schemas import QueriesGenerationJob, QueriesGenerationRequest
from app.chat.schemas import MessageJob, MessageRequest
from app.responses.schemas import ResponsesGenerationJob, ResponsesGenerationRequest

JobType = Union[QueriesGenerationJob, MessageJob, ResponsesGenerationJob]

JobRequestType = Union[QueriesGenerationRequest, MessageRequest, ResponsesGenerationRequest]