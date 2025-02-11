import time

from autogen_agentchat.messages import TextMessage
from fastapi import HTTPException

from autogen_agent_util.assistant_agent import AGENT_ASSISTANT, CANCELLATION_TOKEN

async def autogen_agent_streaming(input_query: str):
    """
    Asynchronously processes an input query using the AssistantAgent and streams the response content.

    Args:
        input_query (str): The input query from the user.

    Yields:
        str: The status and content of the response message from the AssistantAgent.

    Raises:
        HTTPException: If an error occurs during the processing of the input query.
    """
    try:
        # Send the input query to the AssistantAgent and get a stream of responses.
        stream_output = AGENT_ASSISTANT.on_messages_stream([TextMessage(content=input_query, source="user")],
                                                           CANCELLATION_TOKEN)

        # Yield the start status of the story.
        yield "Status: [Start of the story]\n\n"
        time.sleep(2)

        # Iterate over the streamed responses and yield each response content.
        async for response in stream_output:
            print(response)
            yield f"data: {response.chat_message.content}\n\n"
        time.sleep(2)

        # Yield the end status of the story.
        yield "Status: [End of the story]\n\n"
    except Exception as e:
        # Raise an HTTPException with status code 500 if an error occurs.
        raise HTTPException(status_code=500, detail=f"Error in autogen_agent: {str(e)}")
