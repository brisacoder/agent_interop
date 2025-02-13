# Agentic Framework Interoperability Over the Network

This repository demonstrates how to orchestrate interactions between **Langgraph**, **Autogen** and **Llama-Index** agents **over a network**, rather than in a single codebase. By separating the server-side Autogen/Llama-Index agent (for generating short stories) and the client-side Langgraph agent, you gain a clear, modular architecture that showcases how distributed AI agents can interoperate via REST APIs.

With this example, you can:

- **Isolate Agent Logic** – Keep the story-generation functionality on the server, while the client remains focused on orchestration.  
- **Leverage REST Endpoints** – Interact with the Autogen agent through streaming or stateless endpoints, providing flexible integration strategies for your own applications.  
- **Streamline Development** – Easily experiment and debug each component, reducing complexity by splitting responsibilities across separate processes.  

## Server-Side

Server has an autogen (v0.4) and llama-index agents to create short stories.

Prereq:<br/>

Export variables or create a .env file (preferred) with OpenAI or Azure OPenAI infomation. Examples

export azure openai env vars for using autogen agent-

```bash
AZURE_OPENAI_API_KEY="<your-key>"
AZURE_OPENAI_ENDPOINT="<your-endpoint>"
AZURE_OPENAI_DEPLOYMENT="gpt-4o"
AZURE_API_VERSION="2024-08-01-preview"
```

```bash
OPENAI_API_KEY=sk-<your key>
OPENAI_MODEL_NAME=gpt-4o
```

---

Start server:

```python
cd server\ap_server
python main
```
  
---

The call to `RemoteGraph()` on the client side sends a request to `/runs/stream` endpoint at `server\ap_server\routers\stateless_runs.py`

`/runs` endpoint calls the autogen agent without streaming

```bash
curl --location 'http://0.0.0.0:8123/runs' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
  "input": [
    {"query": "write a short story about a cat"}
  ]
}'

output:
{
    "query": "write a short story about a cat",
    "output": "<full story here>"
}

```

`/runs/stream` endpoint is used by remotegraph client

```bash
for autogen subgraph:
curl --location 'http://localhost:8123/runs/stream' \
--header 'Content-Type: application/json' \
--data '{
           "input": {
             "messages": [
               {
                 "content": "write a story about cat"
               }
             ]
           },
           "assistant_id": "autogen",
           "config": {
             "tags": ["tag1", "tag2"]
           }
         }'

for llama_index subgraph:
curl --location 'http://localhost:8123/runs/stream' \
--header 'Content-Type: application/json' \
--data '{
           "input": {
             "messages": [
               {
                 "content": "write a story about cat"
               }
             ]
           },
           "assistant_id": "llama_index",
           "config": {
             "tags": ["tag1", "tag2"]
           }
         }'
```

`/runs/stream/agent` calls the autogen agent with streaming

```bash
curl --location 'http://0.0.0.0:8123/runs/stream/agent' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
  "input": [
    {"query": "write a short story about a cat"}
  ]
}'

output:
<Streamed output from agent>

```

## Client-Side

`client\lg_rg.py` has a client that consist of a Graph + a `RemoteGraph()` API that hits the above mentioned server.

`client\lg_rg_human_in_loop_autogen.py` has a client that consist of a Graph + a `RemoteGraph()` API that hits the above mentioned server via /runs/human_in_loop endpoint and runs a human_in_loop workflow in the autogen subgraph.

`client\llama_rg.py` has a client that consist of a Graph + a `RemoteGraph()` API that hits the above mentioned server.

`client\rest.py` contains a client that makes a stateless request to the above mentioned server via /runs endpoint.

`client\rest_human_in_loop_autogen.py` contains a client that makes a stateless request to the above mentioned server via /runs/human_in_loop endpoint and runs a human_in_loop workflow in the autogen subgraph.

`client\rest_human_in_loop_lg.py` contains a client that makes a stateless request to the above mentioned server via /runs endpoint and then sends the output to a langgraph for human in loop.

## Testing

- Run Server as `python main.py`
- Run RemoteGraph client as `python lg.py`
- Run RemoteGraph client for human-in-loop demo for autogen `python lg_human_in_loop_autogen.py`
- Run stateless REST client as `python rest.py`
- Run stateless REST client for human-in-loop demo for autogen `python rest_human_in_loop_autogen.py`
- Run stateless REST client for human-in-loop demo for LangGraph `python rest_human_in_loop_lg.py`
