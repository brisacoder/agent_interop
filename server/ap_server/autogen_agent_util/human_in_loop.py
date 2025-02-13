from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
from fastapi import HTTPException

from autogen_agent_util.assistant_agent import get_assistant_agent
from autogen_agent_util.user_proxy_agent import get_user_proxy_agent


async def autogen_agent_human_in_loop(input_query: str):
    """
    Asynchronously processes an input query using the AssistantAgent and UserProxyAgent with human-in-loop
    and returns the response content.
    Server expects the user to enter "APPROVE" on server terminal, to end the conversation.

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
        user_proxy_agent = get_user_proxy_agent()

        # Create the termination condition which will end the conversation when the user says "APPROVE".
        termination = TextMentionTermination("APPROVE")

        # Create the team.
        team = RoundRobinGroupChat([assistant_agent, user_proxy_agent], termination_condition=termination)
        # Run the conversation and stream to the console.
        stream = team.run_stream(task=input_query)
        await Console(stream)
        response = await assistant_agent.on_messages([TextMessage(content=input_query, source="user")],
                                                     cancellation_token)
    except Exception as e:
        # Raise an HTTPException with status code 500 if an error occurs.
        raise HTTPException(status_code=500, detail=f"Error in autogen_agent: {str(e)}")

    # Return the content of the response message.
    common_response = {"type": "AUTOGEN_APPROVE", "content": response.chat_message.content,
                       "role": response.chat_message.source,
                       "prompt_tokens": response.chat_message.models_usage.prompt_tokens,
                       "completion_tokens": response.chat_message.models_usage.completion_tokens}
    # return response
    return common_response
