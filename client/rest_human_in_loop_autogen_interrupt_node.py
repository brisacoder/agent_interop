# Description: This file contains a sample graph that makes a stateless request to the autogen server
# which is instrumented to use human-in-the-loop.
# 1. Start the server: python3 server/ap_server/main.py
# 2. Start the client: python3 client/rest_human_in_loop_autogen.py
# 3. Monitor the server logs, after running the client. When prompted, as below - enter 'APPROVE' on the server terminal.
# 2025-02-13 10:14:49,183 - INFO - source='user_proxy' models_usage=None request_id='2e4386bb-0f69-4eaf-936d-7d6e4f48d4d1' content='' type='UserInputRequestedEvent'
# APPROVE

import json
from typing import Annotated, Dict, Literal, TypedDict, List

import requests
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables.config import RunnableConfig
import uuid

# url for the autogen server /runs endpoint
url = "http://127.0.0.1:8123/runs/human_in_loop"
url_continue = "http://127.0.0.1:8123/runs/continue/"


def default_state() -> Dict:
    return {
        "messages": [],
    }


# Define the graph state
class GraphState(TypedDict):
    text_to_approve: str
    exception_text: str
    messages: Annotated[List[BaseMessage], add_messages]


# Graph node that makes a stateless request to the autogen server
def node_autogen_request_stateless(
    state: GraphState,
) -> Command[Literal["human_node", "exception_node", END]]:

    # Read the prompt from the input state
    query = state["messages"][-1].content

    # request headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    # payload to send to autogen server at /runs endpoint
    payload = json.dumps(
        {
            "input": [{"query": query}],
        }
    )

    try:
        # stateless request to autogen server
        response = requests.post(url, headers=headers, data=payload).json()
        if response["output"]["status"] == "need_input":
            print(f"\nServer asks: {response['output']['message']}\n")

            # OPTIONAL: Get task ID from initial response
            # task_id = response['output']["task_id"]

            return Command(
                goto="human_node",  # The next node(s) to go to
                update={
                    "text_to_approve": f"\nServer asks: {response['output']['message']}\n"
                },
            )
        else:
            return Command(
                goto=END,  # The next node(s) to go to
                update={"messages": [response]},  # The update to apply to the state
            )
    except Exception as e:
        return Command(
            goto="exception_node",  # The next node(s) to go to
            update={"exception_text": e},  # The update to apply to the state
        )


def exception_node(state: GraphState):
    print(f"Exception happen while processing graph: {state["exception_text"]}")
    return default_state()


def human_node(state: GraphState):
    value = interrupt(
        # Any JSON serializable value to surface to the human.
        # For example, a question or a piece of text or a set of keys in the state
        {"text_to_revise": state["text_to_approve"]}
    )
    return {
        # Update the state with the human's input
        "text_to_approve": value
    }


# Build a sample graph
builder = StateGraph(GraphState)
builder.add_node("human_node", human_node)
builder.add_node("exception_node", exception_node)
builder.add_node("node_autogen_request_stateless", node_autogen_request_stateless)
builder.add_edge(START, "node_autogen_request_stateless")
builder.add_edge("exception_node", END)
builder.add_edge("node_autogen_request_stateless", END)

# A checkpointer needs be enabled for interrupts to work
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
inputs = {"messages": [HumanMessage(content="write a story about a hare and tortoise")]}

config: RunnableConfig = {
    "configurable": {
        "thread_id": uuid.uuid4(),
    }
}
for chunk in graph.stream(inputs, config=config):
    print(chunk)

# Resume using Command
for chunk in graph.stream(Command(resume="Edited text"), config=config):
    print(chunk)
