from autogen_agentchat.messages import TextMessage
from fastapi import HTTPException

from autogen_agent_util.assistant_agent import AGENT_ASSISTANT, CANCELLATION_TOKEN


async def autogen_agent(input_query: str):
    try:

        response = await AGENT_ASSISTANT.on_messages([TextMessage(content=input_query, source="user")],
                                                     CANCELLATION_TOKEN)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in autogen_agent: {str(e)}")
    return response.chat_message.content
