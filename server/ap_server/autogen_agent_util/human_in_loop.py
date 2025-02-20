from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
from fastapi import HTTPException
import uuid
from fastapi import APIRouter

from autogen_agent_util.assistant_agent import get_assistant_agent
from autogen_agent_util.user_proxy_agent import get_user_proxy_agent
from autogen_agentchat.messages import UserInputRequestedEvent
from langgraph.types import interrupt

router = APIRouter(tags=["Stateless Runs"])


paused_tasks = {}
# Send the input query to the AssistantAgent and await the response.
assistant_agent, cancellation_token = get_assistant_agent()
user_proxy_agent = get_user_proxy_agent()
termination = TextMentionTermination("APPROVE")
team = RoundRobinGroupChat(
    [assistant_agent, user_proxy_agent], termination_condition=termination
)
history = []


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
        # Run the conversation and stream to the console.
        stream = team.run_stream(task=input_query)
        async for message_autogen in stream:
            if isinstance(message_autogen, UserInputRequestedEvent):
                task_id = str(uuid.uuid4())  # Optional: task_id
                paused_tasks["task_id"] = {"status": "waiting_for_input"}
                return {
                    "task_id": task_id,
                    "status": "need_input",
                    "message": "Remote agent needs approval. Type APPROVE to terminate",
                }
            else:
                print(history)
                history.append(message_autogen)
            # Console(message_autogen)
    except Exception as e:
        # Raise an HTTPException with status code 500 if an error occurs.
        raise HTTPException(status_code=500, detail=f"Error in autogen_agent: {str(e)}")


async def continue_process(user_input: str):  # Changed to dict to match client format
    # Resume processing with user input
    print(f"Server: Continuing task with input: {user_input}")
    print(history)
    response = await assistant_agent.on_messages(
        [TextMessage(content=user_input, source="user")], cancellation_token
    )
    history.append(response.chat_message.content)
    # Return the content of the response message
    common_response = {
        "type": "AUTOGEN_APPROVE",
        "content": history,
        "role": response.chat_message.source,
        "prompt_tokens": response.chat_message.models_usage.prompt_tokens,
        "completion_tokens": response.chat_message.models_usage.completion_tokens,
    }

    return common_response
