from dotenv import load_dotenv
from llama_index.core.agent import ReActAgent
from llamindex_agent_util.llm_util import get_model_client
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def llama_index_agent(input_query: str):
    """
    Processes an input query using the ReActAgent and returns the response content.

    Args:
        input_query (str): The input query from the user.

    Returns:
        str: The content of the response message from the ReActAgent.

    Raises:
        Exception: If an error occurs during the processing of the input query.
    """
    try:
        # Initialize the ReActAgent with the model client and process the input query.
        agent = ReActAgent.from_tools([], llm=get_model_client())
        logging.info(f"llama index Agent initialized")
        response = agent.chat(input_query)
    except Exception as e:
        # Raise an Exception if an error occurs.
        raise Exception(f"Error in llama_index_agent: {str(e)}")

    # Return data to server in a common format
    common_response = {"type": agent.chat_history[-1].blocks[0].block_type, "content": response.response, "role": agent.chat_history[-1].role.value, 
                       "prompt_tokens": 0, 
                       "completion_tokens": 0}    
    return common_response
