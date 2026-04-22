from random import randrange

from app.data.schemas import DataJob
from app.common.literals import JobStatus


def run_data_job(job: DataJob) -> DataJob:
    def _to_job(stopped: bool = False) -> DataJob:
        if stopped: status: JobStatus = "error_stopped"
        elif error_detail: status = "error_continued"
        else: status = "complete"
        return DataJob(
            system_messages=job.system_messages,
            chat_length_max=job.chat_length_max,
            chat_length_min=job.chat_length_min,
            queries_job_uuid=job.queries_job_uuid,
            max_retries=job.max_retries,
            on_error=job.on_error,
            model_id=job.model_id,
            status=status,
            error_detail=error_detail,
            chats=job.chats
        )
    assert job.chats is not None

    chat_desired_lengths: list[int] = [randrange(
        start=job.chat_length_min,
        stop=job.chat_length_max + 1
    ) for _ in job.chats]

    error_detail: str | None = None
    while True:
        if all([chat.complete == True for chat in job.chats]): break
        for i, chat in enumerate(job.chats):
            if chat.complete: continue
            try:
                chat.generate(
                    max_retries=job.max_retries,
                    model_id=job.model_id,
                    append_to_chat=True
                )
                if chat.length == chat_desired_lengths[i]:
                    chat.complete = True
                    job.chats[i] = chat
                    continue
                chat.generate_followup(
                    max_retries=job.max_retries,
                    model_id=job.model_id,
                    append_to_chat=True
                )
            except Exception as e:
                error_detail = str(e)
                chat.complete = True
                job.chats[i] = chat
                if job.on_error == "continue": continue
                elif job.on_error == "stop": return _to_job(stopped=True)
    return _to_job()
