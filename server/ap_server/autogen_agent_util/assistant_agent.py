from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken

from autogen_agent_util.llm_util import MODEL_CLIENT

# Create an instance of AssistantAgent with a specific name, system message, and model client.
AGENT_ASSISTANT = AssistantAgent(
    name="assistant",
    system_message="You are a helpful short story assistant. Provide the moral of the story and introduce a new character.",
    model_client=MODEL_CLIENT,
)
# Create a cancellation token to manage the cancellation of tasks.
CANCELLATION_TOKEN = CancellationToken()
