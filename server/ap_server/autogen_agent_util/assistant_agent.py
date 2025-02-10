from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken

from autogen_agent_util.llm_util import MODEL_CLIENT

AGENT_ASSISTANT = AssistantAgent(
    name="assistant",
    system_message="You are a helpful short story assistant. Provide the moral of the story and introduce a new character.",
    model_client=MODEL_CLIENT,
)

CANCELLATION_TOKEN = CancellationToken()