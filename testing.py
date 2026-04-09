from rich import print
from uuid import UUID

from app.common.file_utils import queries_jsonl_iterator


TEST_UUID = UUID("bb63b409-7b71-42cd-af06-3a032645634a")

for query in queries_jsonl_iterator(uuid=TEST_UUID):
    print(query)