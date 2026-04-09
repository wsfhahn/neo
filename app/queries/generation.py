from openai.types.chat import ChatCompletionMessageParam

from app.common.errors import GenerationError
from app.common.config import GLOBAL_CLIENT, GLOBAL_SETTINGS
from app.queries.prompts import QUERY_GENERATOR_SYSTEM_PROMPT
from app.queries.schemas import (
    QueriesGenerationRequest,
    ModelQueriesResponse,
    QueriesGenerationJob
)


def run_queries_job(job: QueriesGenerationJob) -> QueriesGenerationJob: # type: ignore
    output: list[QueriesGenerationRequest] = []

    for category in job.categories:
        chat: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": QUERY_GENERATOR_SYSTEM_PROMPT.format(n=job.queries_per_category)},
            {"role": "user", "content": ""}
        ]