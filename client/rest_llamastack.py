# Description: This file contains a sample graph that makes a stateless request to the autogen server.
# python3 client/rest.py

import json
from typing import TypedDict, List
from time import sleep

import requests
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import START, END, MessagesState, StateGraph


# url for the autogen server /runs endpoint
url = "http://127.0.0.1:8123/runs/wait/llamastack"


# Define the graph state
class GraphState(TypedDict):
    messages: List[BaseMessage]


# Graph node that makes a stateless request to the autogen server
def node_llamastack_request_stateless(state: GraphState):

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
        # stateless request to llamastack server
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            print("Server: ", response.json()['output'], end="\n\n")
            return {"messages": [response]}
    except Exception as e:
        return {"messages": [e]}


# Build a sample graph
builder = StateGraph(GraphState)
builder.add_node("node_llamastack_request_stateless", node_llamastack_request_stateless)
builder.add_edge(START, "node_llamastack_request_stateless")
builder.add_edge("node_llamastack_request_stateless", END)
graph = builder.compile()
inputs = {"messages": [HumanMessage(content="Write short introduction on Abraham Lincoln")]}
print(f"\nUser: {inputs['messages'][0].content}")
result = graph.invoke(inputs)


