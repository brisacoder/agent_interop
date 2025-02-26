import asyncio
import os
import time

from dotenv import load_dotenv
from fastapi import HTTPException
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types.agent_create_params import AgentConfig
from llama_stack_client import LlamaStackClient
from termcolor import cprint

# Load environment variables from a .env file
load_dotenv()


class LlamaAgentStreaming:
    """
    A class to represent a streaming LlamaStack agent.

    Attributes:
    ----------
    model : str
        The model to be used by the agent.
    base_url : str
        The base URL for the LlamaStack server.
    client : LlamaStackClient
        The client instance for interacting with the LlamaStack server.
    agent_config : AgentConfig
        The configuration for the agent.
    agent : Agent
        The agent instance created with the provided configuration.
    """

    def __init__(self, model: str = None, base_url: str = None):
        """
        Initializes the LlamaStack agent with the provided configuration.

        Parameters:
        ----------
        model : str, optional
            The model to be used by the agent (default is None).
        base_url : str, optional
            The base URL for the LlamaStack server (default is None).
        """
        # Load environment variables or use defaults
        self.base_url = base_url or os.environ.get("LLAMASTACK_SERVER_URL")
        self.model = model or os.environ.get("LLAMASTACK_INFERENCE_MODEL")

        # Initialize LlamaStack client
        self.client = LlamaStackClient(base_url=self.base_url)

        # Configure agent
        self.agent_config = AgentConfig(
            model=self.model,
            instructions="You are a helpful assistant. You give 1 line answers",
            toolgroups=[],
            input_shields=[],
            output_shields=[],
            enable_session_persistence=False,
        )

        # Create agent instance
        self.agent = Agent(self.client, self.agent_config)

    async def run(self, prompt: str):
        """
        Runs the agent with the provided user prompts and returns the responses.

        Parameters:
        ----------
        prompt : str
            The user prompt to be processed by the agent.

        Yields:
        ------
        str
            The response from the agent.
        """
        # Create a session for this run
        session_id = self.agent.create_session("test_session")
        cprint(f"User> {prompt}", "green")
        msg_output = self.agent.create_turn(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            session_id=session_id,
            stream=True
        )

        # Yield the start status of the story.
        for log in EventLogger().log(msg_output):
            try:
                yield f"{log}\n"
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error in llamastack agent: {str(e)}")


# Example usage:
if __name__ == "__main__":
    # Initialize the LlamaAgent with a session name
    llama_agent = LlamaAgentStreaming()

    # Example user prompts
    user_prompts = "Tell me a short story about a hare and tortoise"


    # Define an asynchronous function to handle the responses
    async def main():
        async for response in llama_agent.run(user_prompts):
            print(response)


    # Run the asynchronous function
    asyncio.run(main())
