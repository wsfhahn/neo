from random import randrange
from uuid import UUID, uuid4
import asyncio

from app.data.schemas import DataJob
from app.common.literals import JobStatus
from app.common.chats import Chat


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
            responses_model_id=job.responses_model_id,
            follow_up_model_id=job.follow_up_model_id,
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
                    model_id=job.responses_model_id,
                    append_to_chat=True
                )
                if chat.length == chat_desired_lengths[i]:
                    chat.complete = True
                    job.chats[i] = chat
                    continue
                chat.generate_followup(
                    max_retries=job.max_retries,
                    model_id=job.responses_model_id,
                    append_to_chat=True
                )
            except Exception as e:
                error_detail = str(e)
                chat.complete = True
                job.chats[i] = chat
                if job.on_error == "continue": continue
                elif job.on_error == "stop": return _to_job(stopped=True)
    return _to_job()


async def run_data_job_concurrent(job: DataJob) -> DataJob:
    error_detail: str | None = None
    def _finish_job(stopped: bool = False) -> DataJob:
        if stopped: status: JobStatus = "error_stopped"
        elif error_detail: status = "error_continued"
        else: status = "complete"
        job.status = status
        job.chats = list(chats_dict.values())
        job.error_detail = error_detail
        return job
    
    assert job.chats is not None

    chats_dict: dict[UUID, Chat] = {uuid4(): chat for chat in job.chats}
    desired_lengths: dict[UUID, int] = {uuid: randrange(
        job.chat_length_min,
        job.chat_length_max + 1
    ) for uuid, _ in chats_dict.items()}

    while True:
        try:
            incomplete = {uuid: chat for uuid, chat in chats_dict.items() if chat.complete == False}
            if len(incomplete) == 0:
                break
            i = 0
            while i < len(incomplete):
                batch = list(incomplete.items())[i:i+job.batch_size]
                uuids, chats = zip(*batch)
                await asyncio.gather(
                    *[asyncio.to_thread(
                        chats[j].generate,
                        job.max_retries,
                        job.responses_model_id,
                        True,
                        None,
                        desired_lengths[uuids[j]]
                    ) for j in range(len(batch))]
                )
                i += job.batch_size
            
            incomplete = {uuid: chat for uuid, chat in chats_dict.items() if chat.complete == False}
            i = 0
            while i < len(incomplete):
                batch = list(incomplete.items())[i:i+job.batch_size]
                _, chats = zip(*batch)
                await asyncio.gather(
                    *[asyncio.to_thread(
                        chats[j].generate_followup,
                        job.max_retries,
                        job.follow_up_model_id,
                        True
                    ) for j in range(len(batch))]
                )
                i += job.batch_size
        except Exception as e:
            error_detail = str(e)
            for _, chat in incomplete.items():
                chat.complete = True
            if job.on_error == "continue": continue
            elif job.on_error == "stop": return _finish_job(stopped=True)
    return _finish_job(stopped=False)