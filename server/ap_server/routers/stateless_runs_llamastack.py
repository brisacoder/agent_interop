from __future__ import annotations

from fastapi import APIRouter
from http import HTTPStatus
import json
import logging

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import StreamingResponse

from llamastack_agent_util.llamastack_agent_streaming import LlamaAgentStreaming
from models import Any, ErrorResponse, RunCreateStateless, Union
from llamastack_agent_util.llamastack_agent import LlamaAgent

router = APIRouter(tags=["Stateless Runs_Llamastack"])


@router.post(
    "/runs/wait/llamastack",
    response_model=Any,
    responses={
        "404": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
    },
    tags=["Stateless Runs_Llamastack"],
)
def wait_run_stateless_runs_wait_post(
        body: RunCreateStateless, ) -> Union[Any, ErrorResponse]:
    """
    Create Run, Wait for Output


    Synchronously processes a stateless run request and returns the result.

    Args:
        body (RunCreateStateless): The request body containing the run details.

    Returns:
        Union[Any, ErrorResponse]: The result of the run or an error response.
    """

    # Extract the query input from the request body.

    query_input = (
        body.input[0]["query"] if isinstance(body.input, list) else body.input["query"]
    )

    print(f"Received query: {query_input}")

    # Run the autogen agent with the extracted query input and await the output.
    agent: LlamaAgent = LlamaAgent()
    output_data = agent.run(query_input)
    print(f"Output: {output_data}")

    return {"query": query_input, "output": output_data}


@router.post(
    "/runs/llamastack",
    response_model=Any,
    responses={
        "404": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
    },
    tags=["Stateless Runs_Llamastack"],
)
def run_stateless_runs_post(body: RunCreateStateless) -> Union[Any, ErrorResponse]:
    pass


@router.post(
    "/runs/stream/llamastack",
    response_model=str,
    responses={
        "404": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
    },
    tags=["Stateless Runs_Llamastack"],
)
def stream_run_stateless_runs_stream_post(
        body: RunCreateStateless,
) -> Union[str, ErrorResponse]:
    """
    Create Run, Stream Output

    Asynchronously processes a stateless run request and streams the output.

    Args:
        body (RunCreateStateless): The request body containing the run details.

    Returns:
        Union[str, ErrorResponse]: A streaming response with the run output or an error response.
    """
    # Extract the query input from the request body.
    query_input = (
        body.input[0]["query"] if isinstance(body.input, list) else body.input["query"]
    )
    print(f"Received query: {query_input}")

    # Create an instance of LlamaAgentStreaming
    agent = LlamaAgentStreaming()

    # Create a StreamingResponse with the event generator
    stream_response = StreamingResponse(agent.run(query_input), media_type="text/event-stream")

    return stream_response
