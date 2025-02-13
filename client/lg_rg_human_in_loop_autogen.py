# Description: This file contains a sample graph that uses Langgrpah RemoteGraph for an Autogen subgraph invocation.
# It is instrumented to use human-in-the-loop.
# 1. Start the server: python3 server/ap_server/main.py
# 2. Start the client: python3 client/lg_rg_human_in_loop_autogen.py
# 3. Monitor the server logs, after running the client. When prompted, as below - enter 'APPROVE' on the server terminal.
# 2025-02-13 10:14:49,183 - INFO - source='user_proxy' models_usage=None request_id='2e4386bb-0f69-4eaf-936d-7d6e4f48d4d1' content='' type='UserInputRequestedEvent'
# APPROVE
from langgraph_sdk import get_sync_client
from langgraph.pregel.remote import RemoteGraph
from langgraph.graph import StateGraph, MessagesState, START, END
from typing import TypedDict

url = "http://127.0.0.1:8123"
graph_name = "autogen_human_in_loop"
remote_graph = RemoteGraph(graph_name, url=url)

# define parent graph
builder = StateGraph(MessagesState)
# add remote graph directly as a node
builder.add_node("child", remote_graph)
builder.add_edge(START, "child")
builder.add_edge("child", END)
graph = builder.compile()

# The stream_mpde below MUST match the event name that comes back from the server
for chunk in graph.stream({
    "messages": [{"role": "user", "content": "Tell me a story about San Francisco"}]
}, stream_mode="updates", subgraphs=True):
    print(chunk)