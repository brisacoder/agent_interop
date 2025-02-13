import tiktoken
from dotenv import load_dotenv
from llama_index.core.agent import ReActAgent
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llamindex_agent_util.llm_util import get_model_client
from llama_index.core import Settings
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
        token_counter = TokenCountingHandler(
            tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode
        )

        Settings.llm = get_model_client()
        Settings.callback_manager = CallbackManager([token_counter])
        # Initialize the ReActAgent with the model client and process the input query.
        agent = ReActAgent.from_tools([], llm=get_model_client())
        logging.info(f"llama index Agent initialized")
        response = agent.chat(input_query)
    except Exception as e:
        # Raise an Exception if an error occurs.
        raise Exception(f"Error in llama_index_agent: {str(e)}")

    # Return data to server in a common format
    common_response = {"type": agent.chat_history[-1].blocks[0].block_type, "content": response.response, "role": agent.chat_history[-1].role.value, 
                       "prompt_tokens": token_counter.prompt_llm_token_count,
                       "completion_tokens": token_counter.completion_llm_token_count}
    # Reset token counter
    token_counter.reset_counts()
    return common_response
