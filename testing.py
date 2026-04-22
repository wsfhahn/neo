from uuid import UUID
from app.common.file_utils import load_job


job = load_job(UUID("c4a49679-643c-41a6-b7ad-35b69421968b"))
print(job)