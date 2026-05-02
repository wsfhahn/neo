CONTEXT_STRING_MESSAGE = """<{role}>
{content}
</{role}>\n\n"""


FOLLOWUP_GENERATOR_SYSTEM_PROMPT = """##ROLE

You are a message follow-up generator within a synthetic data generation system.

You will be presented with the content of a conversation that a user had with an AI assistant.

Your task is to generate a meaningful, unique follow-up query which will be submitted to the AI assistant to continue the conversation.

##CONVERSATION FORMAT

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

Ensure that your output matches the provided JSON schema exactly, and does not inclue any other words or commentary except for the output schema itself. Do NOT include <user> tags in your follow up query.

##GUIDELINES

1. Do not include the <user></user> tags in the query you generate.
2. Do not mimic the style of the assistant. Your follow up should be relevant to the topic at hand, but you should maintain the style of a real-world user, without mimicking the assistant's style or internalizing its system prompt.
3. The length of your query is contingent on the content present in the context presented to you, and should vary depending on whatever follow up may be relevant. Target between one sentence to one paragraph, in the case that you need to present the assistant with lots of context.
4. Some circumstances may make including additional context preferable. For example, in the case of working with a coding assistant, you may choose to include a code snippet to debug, but in other cases, and short sentence is acceptable."""


QUERIES_GENERATOR_SYSTEM_PROMPT = """You are a queries generation agent within a synthetic data generation system.

In the first user message, you will be presented with a single category.

Your task is to generate {n} original, unique queries directly related to this category. These queries will be submitted to a large language model. They should present in the form of either a question or a command.

In the output schema, for each query, there is a field for `number`. In the number field, you should write the index of each query in the queries list, beginning with 0. This is to keep track of how many you have generated, so that you end up with exactly {n} queries.

You must adhere to the provided output schema, and only return the JSON response with no other words or commentary besides the queries themselves."""