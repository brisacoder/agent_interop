import time

from autogen_agentchat.messages import TextMessage
from fastapi import HTTPException

from autogen_agent_util.assistant_agent import get_assistant_agent


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
        # Initialize the AssistantAgent and CancellationToken.
        assistant_agent, cancellation_token = get_assistant_agent()
        cancellation_token.cancel()
        yield "event: TERMINATE\n\n"
        # Send the input query to the AssistantAgent and get a stream of responses.
        # stream_output = assistant_agent.on_messages_stream([TextMessage(content=input_query, source="user")],
        #                                                    cancellation_token)
        #
        # # Yield the start status of the story.
        # yield "event: updates\ndata: [Start of the story]\n\n"
        # time.sleep(2)
        #
        # # Iterate over the streamed responses and yield each response content.
        # async for response in stream_output:
        #     print(response)
        #     yield f"event: updates\ndata: {response.chat_message.content}\n\n"
        # time.sleep(2)
        #
        # # Yield the end status of the story.
        # yield "event: updates\ndata: [End of the story]\n\n"
    except Exception as e:
        # Raise an HTTPException with status code 500 if an error occurs.
        raise HTTPException(status_code=500, detail=f"Error in autogen_agent: {str(e)}")
