import os
from dotenv import load_dotenv
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types.agent_create_params import AgentConfig
from llama_stack_client import LlamaStackClient
from termcolor import cprint

# Load environment variables
load_dotenv()

class LlamaAgent:
    def __init__(self, model: str = None, base_url: str = None):
        """
        Initializes the LlamaStack agent with the provided configuration.
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

    def run(self, prompt: str):
        """
        Runs the agent with the provided user prompts and returns the responses.
        """
        # Create a session for this run
        session_id = self.agent.create_session("test_session")
        cprint(f"User> {prompt}", "green")
        response = self.agent.create_turn(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    }
               ],
               session_id=session_id,
               stream=False
          )

        return response.output_message.content

# Example usage:
if __name__ == "__main__":
    # Initialize the LlamaAgent with a session name
    llama_agent = LlamaAgent(session_name="test-session")

    # Example user prompts
    user_prompts = [
        "Tell me a short story about a hare and tortoise",
        "What is the capital of France?"
    ]

    # Run the agent with the user prompts and get responses
    responses = llama_agent.run(user_prompts)

    # Output the responses
    for response in responses:
        cprint(f"Agent Response> {response}", "blue")
