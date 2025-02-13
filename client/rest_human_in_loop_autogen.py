# Description: This file contains a sample graph that makes a stateless request to the autogen server
# which is instrumented to use human-in-the-loop.
# 1. Start the server: python3 server/ap_server/main.py
# 2. Start the client: python3 client/rest_human_in_loop_autogen.py
# 3. Monitor the server logs, after running the client. When prompted, as below - enter 'APPROVE' on the server terminal.
# 2025-02-13 10:14:49,183 - INFO - source='user_proxy' models_usage=None request_id='2e4386bb-0f69-4eaf-936d-7d6e4f48d4d1' content='' type='UserInputRequestedEvent'
# APPROVE

import json
from typing import TypedDict, List

import requests
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import START, END, MessagesState, StateGraph

# url for the autogen server /runs endpoint
url = "http://127.0.0.1:8123/runs/human_in_loop"


# Define the graph state
class GraphState(TypedDict):
    messages: List[BaseMessage]


# Graph node that makes a stateless request to the autogen server
def node_autogen_request_stateless(state: GraphState):

    # Read the prompt from the input state
    query = state["messages"][-1].content

    # request headers
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # payload to send to autogen server at /runs endpoint
    payload = json.dumps({
        "input": [
            {"query": query}
        ],
    })

    try:
        # stateless request to autogen server
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            print("response", response.json())
            return {"messages": [response]}
    except Exception as e:
        return {"messages": [e]}


# Build a sample graph
builder = StateGraph(GraphState)
builder.add_node("node_autogen_request_stateless", node_autogen_request_stateless)
builder.add_edge(START, "node_autogen_request_stateless")
builder.add_edge("node_autogen_request_stateless", END)
graph = builder.compile()
inputs = {"messages": [HumanMessage(content="write a story about a cat")]}
result = graph.invoke(inputs)
