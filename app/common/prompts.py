CONTEXT_STRING_MESSAGE = """<{role}>
{content}
</{role}>\n\n"""


FOLLOWUP_GENERATOR_SYSTEM_PROMPT = """You are a message follow-up generator within a synthetic data generation system.

You will be presented with the content of a conversation that a user had with an AI assistant.

Your task is to generate a meaningful, unique follow-up query which will be submitted to the AI assistant to continue the conversation.

Messages within this conversation will be presented to you in the format:

<{role}>
{content}
</{role}>

for each turn in the conversation.

For example, one conversation might be:

<system>
You are a helpful assistant.
</system>

<user>
Who are you?
</user>

<assistant>
I am a helpful assistant.
</assistant>

Ensure that your output matches the provided JSON schema exactly, and does not inclue any other words or commentary except for the output schema itself."""


QUERIES_GENERATOR_SYSTEM_PROMPT = """You are a queries generation agent within a synthetic data generation system.

In the first user message, you will be presented with a single category.

Your task is to generate {n} original, detailed queries directly related to this category.

In the output schema, for each query, there is a field for `number`. In the number field, you should write the index of each query in the queries list, beginning with 0. This is to keep track of how many you have generated, so that you end up with exactly {n} queries.

You must adhere to the provided output schema, and only return the JSON response with no other words or commentary besides the queries themselves."""