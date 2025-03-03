# Description: This file contains a sample graph that makes a stateless request to the autogen server
# which is instrumented to use human-in-the-loop.
# 1. Start the server: python3 server/ap_server/main.py
# 2. Start the client: python3 client/rest_human_in_loop_autogen.py
# 3. Monitor the server logs, after running the client. When prompted, as below - enter 'APPROVE' on the server terminal.
# 2025-02-13 10:14:49,183 - INFO - source='user_proxy' models_usage=None request_id='2e4386bb-0f69-4eaf-936d-7d6e4f48d4d1' content='' type='UserInputRequestedEvent'
# APPROVE

import json
import logging
from typing import Annotated, Dict, Literal, TypedDict, List

import requests
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Command
from langgraph.errors import GraphInterrupt
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables.config import RunnableConfig
import uuid

# Configure logging
log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# url for the autogen server /runs endpoint
url = "http://127.0.0.1:8123/runs/human_in_the_loop_interrupt"
url_continue = "http://127.0.0.1:8123/runs/continue/"


def default_state() -> Dict:
    return {
        "messages": [],
    }


# Define the graph state
class GraphState(TypedDict):
    text_to_approve: str
    exception_text: str
    human_input: str
    thread_id: str
    messages: Annotated[List[BaseMessage], add_messages]


# Graph node that makes a stateless request to the autogen server
def node_autogen_resume(
    state: GraphState,
) -> Command[Literal["exception_node", END]]:

    headers = {"accept": "application/json", "Content-Type": "application/json"}

    payload = {
        "agent_id": "hitl",
        "input": {"messages": [HumanMessage(state["human_input"]).model_dump()]},
        "model": "gpt-4o",
        "thread_id": state["thread_id"]
    }
    try:
        # Continue the process with user input and task ID
        response = requests.post(url=url_continue, headers=headers, json=payload)
        # Handle HTTP errors (4xx, 5xx)
        if response.status_code != 200:
            error_message = f"HTTP Error: {response.status_code} - {response.text}"
            return Command(
                goto="exception_node", update={"exception_text": error_message}
            )
        resp_json = response.json()
        message = resp_json["choices"][0]["message"]
        log.debug(f"Server response: {message["content"]}")
        return Command(goto=END, update={"messages": [AIMessage(message["content"]).model_dump()]})
    except Exception as e:
        return Command(goto="exception_node", update={"exception_text": str(e)})


# Graph node that makes a stateless request to the autogen server
def node_autogen_request_stateless(
    state: GraphState,
) -> Command[Literal["human_node", "exception_node", END]]:

    # streamed messages received will be stored here
    messages: List[BaseMessage] = []

    # Read the prompt from the input state
    query = state["messages"][-1].content

    # request headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    # payload to send to autogen server at /runs endpoint
    payload = {
        "agent_id": "hitl",
        "input": {"messages": [HumanMessage(query).model_dump()]},
        "model": "gpt-4o",
    }

    try:
        # POST request to the autogen server with streaming enabled.
        response = requests.post(url, headers=headers, json=payload, stream=True)

        # Handle HTTP errors (4xx, 5xx)
        if response.status_code != 200:
            error_message = f"HTTP Error: {response.status_code} - {response.text}"
            return Command(
                goto="exception_node", update={"exception_text": error_message}
            )

        # Check the content type to see if it's an SSE stream.
        content_type = response.headers.get("Content-Type", "")
        if "text/event-stream" in content_type:
            accumulator = []
            # Process SSE lines until we get a complete event (blank line)
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    accumulator.append(line)
                else:
                    # End of an event
                    event_type = None
                    data = None
                    for event_line in accumulator:
                        if event_line.startswith("event:"):
                            event_type = event_line[len("event:") :].strip()
                        elif event_line.startswith("data:"):
                            data = event_line[len("data:") :].strip()
                    accumulator = []  # Reset for the next event

                    # Only process events of type 'updates'
                    if event_type == "updates" and data:
                        event_data = json.loads(data)
                        # Check if this is an interrupt event that requires human approval
                        if event_data.get("type") == "__interrupt__":
                            data = event_data.get("data")
                            message_to_approve = data["messages"][0]["content"]
                            log.debug(f"\nServer asks: {message_to_approve}\n")
                            return Command(
                                goto="human_node",
                                update={
                                    "text_to_approve": message_to_approve,
                                    "messages": messages,
                                    "thread_id": event_data.get("thread_id")
                                },
                            )
                        elif event_data.get("type") == "updates":
                            data = event_data.get("data")
                            messages.extend(data.get("messages", []))
                        else:
                            # TODO this is wrong of course
                            return Command(goto=END, update={"messages": [event_data]})
            # In case the stream ends without producing a full event:
            return Command(
                goto=END,
                update={"messages": [{"error": "No complete SSE event received."}]},
            )
        else:
            # Not an SSE stream; assume a standard JSON response.
            response_data = response.json()
            if response_data["output"]["status"] == "need_input":
                log.debug(f"\nServer asks: {response_data['output']['message']}\n")
                return Command(
                    goto="human_node",
                    update={
                        "text_to_approve": f"\nServer asks: {response_data['output']['message']}\n"
                    },
                )
            else:
                return Command(goto=END, update={"messages": [response_data]})

    except Exception as e:
        return Command(goto="exception_node", update={"exception_text": str(e)})


def exception_node(state: GraphState):
    print(f"Exception happen while processing graph: {state["exception_text"]}")
    return default_state()


def human_node(state: GraphState):
    """Human node with validation."""
    valid_responses = ["Yes", "No"]
    question = "Do you APPROVE this text (Yes/No)?"

    while True:
        answer = interrupt(
            value={"text": state["text_to_approve"], "question": question}
        )

        # Validate answer, if the answer isn't valid ask for input again.
        if not isinstance(answer, str) or answer not in valid_responses:
            question = f"{answer} is not a valid response. {question}"
            answer = None
            continue
        else:
            # If the answer is valid, we can proceed.
            break

    log.debug(f"The human in the loop input is {answer}")

    return {
        # Update the state with the human's input
        "human_input": answer,
        "messages": [HumanMessage(answer).model_dump()],
    }


# Build a sample graph
builder = StateGraph(GraphState)
builder.add_node("human_node", human_node)
builder.add_node("exception_node", exception_node)
builder.add_node("node_autogen_request_stateless", node_autogen_request_stateless)
builder.add_node("node_autogen_resume", node_autogen_resume)

# Edges
builder.add_edge(START, "node_autogen_request_stateless")
builder.add_edge("exception_node", END)
builder.add_edge("human_node", "node_autogen_resume")

# A checkpointer needs be enabled for interrupts to work
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
inputs = {"messages": [HumanMessage(content="write a story about a hare and tortoise")]}

config: RunnableConfig = {
    "configurable": {
        "thread_id": uuid.uuid4(),
    }
}

for chunk in graph.stream(inputs, config=config, stream_mode="updates"):
    if "__interrupt__" not in chunk:
        print(chunk)

state = graph.get_state(config)
print(f"{state.values["text_to_approve"]}\n\n")
human_input = input("Do you APPROVE this text (Yes/No)? ")

# Resume using Command
for chunk in graph.stream(Command(resume=human_input), config=config, stream_mode="updates"):
    print(chunk)
