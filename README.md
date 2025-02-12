# Agentic Framework Interoperability Over the Network

This repository demonstrates how to orchestrate interactions between **Langgraph** and **Autogen** agents **over a network**, rather than in a single codebase. By separating the server-side Autogen agent (for generating short stories) and the client-side Langgraph agent, you gain a clear, modular architecture that showcases how distributed AI agents can interoperate via REST APIs.

With this example, you can:

- **Isolate Agent Logic** – Keep the story-generation functionality on the server, while the client remains focused on orchestration.  
- **Leverage REST Endpoints** – Interact with the Autogen agent through streaming or stateless endpoints, providing flexible integration strategies for your own applications.  
- **Streamline Development** – Easily experiment and debug each component, reducing complexity by splitting responsibilities across separate processes.  

---

## Server-Side

Server has an autogen agent(v0.4) to create short stories.

Prereq:<br/>
export azure openai env vars for using autogen agent-

```bash
AZURE_OPENAI_API_KEY="<your-key>"
AZURE_OPENAI_ENDPOINT="<your-endpoint>"
AZURE_OPENAI_DEPLOYMENT="gpt-4o"
AZURE_API_VERSION="2024-08-01-preview"
```

Start server:
```server\ap_server\main.py```  has the entry point for AP Server.

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

`client\lg.py` has a client that consist of a Graph + a `RemoteGraph()` API that hits the above mentioned server.

`client\rest.py` contains a client that makes a stateless request to the above mentioned server via /runs endpoint.

`client\rest_autogen_human_in_loop.py` contains a client that makes a stateless request to the above mentioned server via /runs endpoint and then sends the output to a human in loop.

## Testing

* Run Server as `python main.py`
* Run RemoteGraph client as `python lg.py`
* Run stateless REST client as `python rest.py`
* Run stateless REST client for human-in-loop `python rest_autogen_human_in_loop.py`
