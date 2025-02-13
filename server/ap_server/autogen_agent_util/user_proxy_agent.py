import logging
from autogen_agentchat.agents import UserProxyAgent


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_user_proxy_agent():
    user_proxy = UserProxyAgent("user_proxy", input_func=input)  # Use input() to get user input from console.
    return user_proxy