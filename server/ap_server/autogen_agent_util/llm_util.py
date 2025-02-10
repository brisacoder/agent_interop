import os

from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
MODEL_CLIENT = AzureOpenAIChatCompletionClient(
    azure_deployment="gpt-4o",
    azure_endpoint=os.environ.get('AZURE_OPENAI_ENDPOINT'),
    model="gpt-4o",
    api_version=os.environ.get('AZURE_API_VERSION'),
    api_key=os.environ.get('AZURE_OPENAI_API_KEY'),
    temperature=0)