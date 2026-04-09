# Neo

![Pascal's Triangle](assets/pascals_triangle.png)

This project is a server to handle your synthetic dataset generation needs. It is based on FastAPI, and uses a worker so that you can queue generation jobs, poll their statuses, and retrieve the results at a later time.

It uses the OpenAI completions API with a configurable base URL, so you can point it to any OpenAI compatible server you choose. You can even use it with local models, like I do.

> [!CAUTION]
> For generating queries, it is advisable to use a model that supports structured output. See Recommended Models.

## Getting Started

This project uses `uv` for package management for simplicity and speed.

Installing the requirements is simple:

```zsh
uv sync
```

Once `uv sync` is complete, the requirements are installed, and the only remaining step is to configure your `.env` file. Below is an example you can use to get started, which includes all of the supported variables:

```
# SERVER CONFIG
API_HOST = "http://localhost:8080"
MODEL_ID = "gemma-3-27b-it"
SAVE_DIR = "storage" # this is relative

# SAMPLING
TEMPERATURE = 1.0
TOP_K = 64
TOP_P = 1.0
MIN_P = 0.0
```

After this file is configured, running the server is simple. If you will not be modifying the server while it is running, run the server with:

```zsh
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8080
```

Include the flag `--reload` if you need the server to reload as you make changes.

Optionally, if you do not wish to set the source (for use cases such as running this as a `systemd` service on a unix machine):

```zsh
./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080
```

## Spec

Below is the spec for the server, which you can use to develop a web UI, REPL, or something else entirely.

### Job Types

---

This project uses a worker and a queue to process jobs asynchronously. Thus far, there are three types of supported jobs (with more likely to come in the future).

Each job has a `status` field. Depending on the type of job, the `status` can be one of the following:

Statuses:
- `pending`
    - A job is `pending` when it is in the queue, but not yet processing.
    - Applies to: `MessageJob`, `QueriesGenerationJob`, `ResponsesGenerationJob`
- `running`
    - Intuitively, a job is `running` when it is actively being processed.
    - Applies to: `MessageJob`, `QueriesGenerationJob`, `ResponsesGenerationJob`
- `complete`
    - The job is finished running.
    - Applies to: `MessageJob`, `QueriesGenerationJob`, `ResponsesGenerationJob`
- `error`
    - An error was encountered while processing. The `error_detail` field has been populated with more detail.
    - Applies to: `MessageJob`
- `error_stopped`
    - An error was encountered while processing, and the job was stopped. The `error_detail` field has been populated.
    - Applies to: `QueriesGenerationJob`, `ResponsesGenerationJob`
- `error_continued`
    - An error was encountered while processing, and the job skipped the current entry, continuing to the next items.
    - Applies to: `QueriesGenerationJob`, `ResponsesGenerationJob`

By sending the following request to the server, a job can be saved to disk. This is recommended if you intend to restart the server, and would not like to lose a queued or finished long-running job.

`GET http://{BASE_URL}:{PORT}/job/{UUID}/save/{FORMAT}`

The possible formats are `JSON` and `JSONL`. All jobs can be saved as `JSON`. Only iterative jobs (`QueriesGenerationJob` and `ResponsesGenerationJob`) can be saved as `JSONL`. `JSONL` should be used for big data operations, such as generating responses on the result of a `QueriesGenerationJob`.

Note that since `JSONL` saving is lossy, and does not include fields such as the `status` and `error_detail`, jobs can only be loaded from `JSON` format files. Jobs can be saved as both formats, and they will not conflict with one another.

Below can be found the specifics of each type of job, as well as how to kick them off.

**`MessageJob`:**

A `MessageJob` should be used to send a single message to the model, optionally along with a system prompt. The model will respond to the message, and the result will be stored in memory.

The internal model for a `MessageJob` is:

```py
class MessageJob(BaseModel):
    system: str | None = None,
    user: str,
    status: MessageJobStatus,
    error_detail: str | None = None,
    response: str | None = None
```

In order to initiate a `MessageJob`, the following request should be sent to the server:

`POST http://{BASE_URL}:{PORT}/create`

With this request, you must include the following JSON body:

```
{
    "system": str | null,
    "user": str
}
```

**`QueriesGenerationJob`:**

A `QueriesGenerationJob` is used to generate a set of queries, which emulate queries which may be submitted to a real chatbot by a user.

Below is the internal model used for `QueriesGenerationJob`:

```py
class QueriesGenerationJob(BaseModel):
    categories: list[str]
    queries_per_category: int
    max_retries: int
    on_error: Literal["continue", "stop"]
    status: QueriesJobStatus,
    error_detail: str | None = None,
    response: list[QueriesResponse] | None = None
```

In the JSON body, you must include array of categories, as well as a number of queries to be generated per category.

A `QueriesGenerationJob` can be initiated by hitting the following endpoint:

`POST http://{BASE_URL}:{PORT}/create`

And you must include the following JSON body:

```
{
    "categories": array[str],
    "queries_per_category": int,
    "max_retries": int,
    "on_error": Literal["continue", "stop"]
}
```

If the job is configured to stop on error and an error occurs during the generation (refusal, malformed output, etc), the generation will stop, the `error_detail` field will be populated, and the queries which have already generated will be stored.

Alternatively, if it is configured the continue on error, the `error_detail` field will be populated, but the current category will be skipped, and generation will continue.

This behavior will only occur once the maximum number of retries is exhausted for both `on_error` configurations.

**`ResponsesGenerationJob`:**

A responses generation job generates responses to queries which were generated by a `QueriesGenerationJob`. In order to run this job, the queries job used for response generation must have content (either complete or errored) and saved in `JSONL` format (see Spec above).

The internal model used for `ResponsesGenerationJob` is as follows:

```py
class ResponsesGenerationJob(BaseModel):
    system: str | None = None
    uuid_str: str # the UUID of the queries generation job
    responses_per_query: int
    max_retries: int
    on_error: Literal["continue", "stop"]
    status: ResponsesJobStatus
    error_detail: str | None  = None
    response: list[ResponsesResponse] | None = None
```