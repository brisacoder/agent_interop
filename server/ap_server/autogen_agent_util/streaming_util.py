import time

from autogen_agentchat.messages import TextMessage
from fastapi import HTTPException

from autogen_agent_util.assistant_agent import AGENT_ASSISTANT, CANCELLATION_TOKEN


async def autogen_agent_streaming(input_query: str):
    try:

        stream_output = AGENT_ASSISTANT.on_messages_stream([TextMessage(content=input_query, source="user")],
                                                           CANCELLATION_TOKEN)

        yield "Status: [Start of the story]\n\n"
        time.sleep(2)
        async for response in stream_output:
            print(response)
            yield f"data: {response.chat_message.content}\n\n"
        time.sleep(2)
        yield "Status: [End of the story]\n\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in autogen_agent: {str(e)}")
