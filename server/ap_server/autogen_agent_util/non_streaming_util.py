from autogen_agentchat.messages import TextMessage
from fastapi import HTTPException

from autogen_agent_util.assistant_agent import get_assistant_agent


async def autogen_agent(input_query: str):
    """
    Asynchronously processes an input query using the AssistantAgent and returns the response content.

    Args:
        input_query (str): The input query from the user.

    Returns:
        str: The content of the response message from the AssistantAgent.

    Raises:
        HTTPException: If an error occurs during the processing of the input query.
    """
    try:
        # Send the input query to the AssistantAgent and await the response.
        assistant_agent, cancellation_token = get_assistant_agent()
        response = await assistant_agent.on_messages([TextMessage(content=input_query, source="user")],
                                                     cancellation_token)
    except Exception as e:
        # Raise an HTTPException with status code 500 if an error occurs.
        raise HTTPException(status_code=500, detail=f"Error in autogen_agent: {str(e)}")

    # Return the content of the response message.
    common_response = {"type": response.chat_message.type, "content": response.chat_message.content, "role": response.chat_message.source, 
                       "prompt_tokens": response.chat_message.models_usage.prompt_tokens, 
                       "completion_tokens": response.chat_message.models_usage.completion_tokens}
    # return response
    return common_response
