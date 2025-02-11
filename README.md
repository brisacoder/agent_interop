# agent_interop


## Server-Side

Server has an autogen agent(v0.4) to create short stories. 

Prereq:<br/>
export azure openai env vars for using autogen agent-
```
AZURE_OPENAI_API_KEY="<your-key>"
AZURE_OPENAI_ENDPOINT="<your-endpoint>"
AZURE_OPENAI_DEPLOYMENT="gpt-4o"
AZURE_API_VERSION="2024-08-01-preview"
```

Start server:
```server\ap_server\main.py```  has the entry point for AP Server.

The call to `RemoteGraph()` on the client side sends a request to `/runs/stream` endpoint at `server\ap_server\routers\stateless_runs.py`

`/runs` endpoint calls the autogen agent without streaming

```
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



`/runs/stream/agent` calls the autogen agent with streaming
```
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

 `client\rest.py` contains a client that makes a stateless request to the above mentioned server via Agent Protocol /runs endpoint.

## Testing

* Run Server as `python main.py`
* Run client as `python lg.main`