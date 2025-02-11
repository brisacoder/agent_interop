import logging
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from autogen_agent_util.llm_util import get_model_client

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_assistant_agent():
    """
    Initializes and returns an instance of AssistantAgent and a CancellationToken.

    The function attempts to create an instance of AssistantAgent with a specific name,
    system message, and model client. It also creates a CancellationToken to manage
    the cancellation of tasks. If any exception occurs during the initialization,
    it logs the error and returns None for both the agent and the cancellation token.

    Returns:
        tuple: A tuple containing the AssistantAgent instance and the CancellationToken instance.
               If an error occurs, both values in the tuple will be None.
    """
    try:
        # Create an instance of AssistantAgent with a specific name, system message, and model client.
        agent_assistant = AssistantAgent(
            name="assistant",
            system_message="You are a helpful short story assistant. Provide the moral of the story and introduce a new character.",
            model_client=get_model_client(),
        )
        # Create a cancellation token to manage the cancellation of tasks.
        cancellation_token = CancellationToken()
        logging.info("AssistantAgent initialized successfully.")
    except Exception as e:
        logging.error(f"An error occurred during initialization of agent: {e}")
        agent_assistant = None
        cancellation_token = None

    return agent_assistant, cancellation_token
