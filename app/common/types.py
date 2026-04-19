from typing import Union

from app.queries.schemas import QueriesJob, QueriesJobRequest
from app.data.schemas import DataJob, DataJobRequest


JobType = Union[QueriesJob, DataJob]

JobRequestType = Union[QueriesJobRequest, DataJobRequest]