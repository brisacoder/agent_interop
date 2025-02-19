import os
import logging
from dotenv import load_dotenv
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient, OpenAIChatCompletionClient

# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_model_client():
    """
    Initializes and returns an instance of a model client based on available environment variables.

    The function first checks for the required environment variables for the OpenAI model.
    If they are set, it creates an instance of OpenAIChatCompletionClient.
    If not, it checks for the required environment variables for the Azure OpenAI model.
    If they are set, it creates an instance of AzureOpenAIChatCompletionClient.
    If neither set of environment variables is available, it logs an error and returns None.

    Returns:
        object: An instance of OpenAIChatCompletionClient or AzureOpenAIChatCompletionClient.
                Returns None if the required environment variables are not set or an error occurs.
    """
    try:
        # Check if the required environment variables for OpenAI are set
        openai_api_key = os.getenv('OPENAI_API_KEY')
        openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o')

        if openai_api_key:
            # Create an instance of OpenAIChatCompletionClient
            model_client = OpenAIChatCompletionClient(
                api_key=openai_api_key,
                model=openai_model,
                seed=42,
                temperature=0
            )
            logging.info("Using OpenAI model client.")
        else:
            # Check if the required environment variables for Azure OpenAI are set
            azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            api_version = os.getenv('AZURE_API_VERSION')
            api_key = os.getenv('AZURE_OPENAI_API_KEY')

            if not azure_endpoint or not api_version or not api_key:
                raise EnvironmentError("Required environment variables for Azure OpenAI are not set.")

            # Create an instance of AzureOpenAIChatCompletionClient
            model_client = AzureOpenAIChatCompletionClient(
                azure_deployment="gpt-4o",
                azure_endpoint=azure_endpoint,
                model="gpt-4o",
                api_version=api_version,
                api_key=api_key,
                temperature=0
            )
            logging.info("Using Azure OpenAI model client.")
    except EnvironmentError as e:
        logging.error(f"Environment error: {e}")
        model_client = None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        model_client = None

    return model_client
