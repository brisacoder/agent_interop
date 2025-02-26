import logging
from typing import Any
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


# Configure logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

router = APIRouter(tags=["Stateless Runs"])


paused_tasks = {}
# Send the input query to the AssistantAgent and await the response.
assistant_agent, cancellation_token = get_assistant_agent()
user_proxy_agent = get_user_proxy_agent()
termination = TextMentionTermination("APPROVE")
team = RoundRobinGroupChat(
    [assistant_agent, user_proxy_agent], termination_condition=termination
)
history: list[Any] = []


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

        if team._is_running:
            await team.reset()
        stream = team.run_stream(task=input_query)
        async for message_autogen in stream:
            history.append(message_autogen)
            if isinstance(message_autogen, UserInputRequestedEvent):
                task_id = str(uuid.uuid4())  # Optional: task_id
                paused_tasks["task_id"] = {"status": "waiting_for_input"}
                log.info(f"Interrupt message: {message_autogen}")
                yield {
                    "node": "autogen",
                    "type": "__interrupt__",
                    "thread_id": task_id,
                    "mode": "updates",
                    "data": {"__interrupt__": "human approval",
                             "messages": [{"role": "assistant", "content": history[-2].content}]}
                }
            elif isinstance(message_autogen, TextMessage):
                if message_autogen.source == "assistant":
                    log.info(f"AI message: {message_autogen}")
                    yield {
                        "node": "autogen",
                        "type": "updates",
                        "thread_id": "",
                        "mode": "updates",
                        "data": {"messages": [{"role": "assistant", "content": message_autogen.content}]},
                    }
                else:
                    log.info(f"User message: {message_autogen}")
            else:
                raise HTTPException(status_code=500, detail=f"Unknown message type: {message_autogen}")

    except Exception as e:
        # Raise an HTTPException with status code 500 if an error occurs.
        raise HTTPException(status_code=500, detail=f"Error in autogen_agent: {str(e)}")


async def continue_process(user_input: str):  # Changed to dict to match client format
    # Resume processing with user input
    log.info(f"Server: Continuing task with input: {user_input}")
    response = await assistant_agent.on_messages(
        [TextMessage(content=user_input, source="user")], cancellation_token
    )
    history.append(response.chat_message.content)
    # Return the content of the response message
    common_response = {
        "object": response.chat_message.type,
        "choices": [
            {
                "message": {
                    "role": response.chat_message.source,
                    "content": response.chat_message.content,
                }
            }
        ],
        "usage": {
            "prompt_tokens": response.chat_message.models_usage.prompt_tokens,
            "completion_tokens": response.chat_message.models_usage.completion_tokens,
            "total_tokens": response.chat_message.models_usage.prompt_tokens
            + response.chat_message.models_usage.completion_tokens,
        },
    }

    return common_response
