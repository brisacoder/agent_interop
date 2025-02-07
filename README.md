# agent_interop


## Server-Side

```server\ap_server\main.py```  has the entry point for AP Server.

The call to `RemoteGraph()` on the client side ends upsending a request to `/runs/stream` endpoint at `server\ap_server\routers\stateless_runs.py`

## Client-Side

`client\lg.py` has a client that consist of a Graph + a RemoteGraph that hits the above mentioned server.

## Testing

* Run Server as `python main.py`
* Run client as `python lg.main` 

