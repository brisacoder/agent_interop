# Description: This file contains a demonstration of human-in-the-loop in langgraph,
# using a sample graph that makes a stateless request to the autogen server.
# python3 client/rest_autogen_human_in_loop.py

import uuid
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver

import json
import requests

# url for the autogen server /runs endpoint
url = "http://127.0.0.1:8123/runs"

# define state for the graph
class State(TypedDict):
    input: str # stores input from the user
    output: str # output from REST Api call to Autogen server
    user_feedback: str # stores feedback from the user


def node_autogen_request_stateless(state):

    # Read the prompt from the input state
    query = state["input"]

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
            #print("response", response.json())
            return {"output": response.json()["output"]}
    except Exception as e:
        #print("error:", e)
        return {"output": e}


def human_feedback(state):
    print("---human_feedback---")
    feedback = interrupt("Please provide feedback:")
    return {"user_feedback": feedback}


def step_3(state):
    print("---Step 3---")
    pass


# build the graph
# step1: request autogen server for output to the user prompt
# step2: human feedback
# step3: executed based on user feedback
builder = StateGraph(State)
builder.add_node("step_1", node_autogen_request_stateless)
builder.add_node("human_feedback", human_feedback)
builder.add_node("step_3", step_3)
builder.add_edge(START, "step_1")
builder.add_edge("step_1", "human_feedback")
builder.add_edge("human_feedback", "step_3")
builder.add_edge("step_3", END)

# Set up memory
memory = MemorySaver()

# Add
graph = builder.compile(checkpointer=memory)

# User Input
initial_input = {"input": "tell me a story about a cat"}

# Thread
thread_id = uuid.uuid4()
thread = {"configurable": {"thread_id": thread_id}}

# Run the graph until the first interruption
for event in graph.stream(initial_input, thread, stream_mode="updates"):
    print(event)
    print("\n")

# Manually update graph state with the user input
for event in graph.stream(
    Command(resume="go to step 3!"), thread, stream_mode="updates"
):
    print(event)
    print("\n")