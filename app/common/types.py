from typing import Union

from app.queries.schemas import QueriesGenerationJob, QueriesGenerationRequest
from app.responses.schemas import ResponsesGenerationJob, ResponsesGenerationRequest

JobType = Union[QueriesGenerationJob, ResponsesGenerationJob]

JobRequestType = Union[QueriesGenerationRequest, ResponsesGenerationRequest]