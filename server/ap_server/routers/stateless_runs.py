# generated by fastapi-codegen:
#   filename:  openapi.json

from __future__ import annotations
from http import HTTPStatus
import json
import logging

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import StreamingResponse

from autogen_agent_util.non_streaming_util import autogen_agent
from autogen_agent_util.human_in_loop import autogen_agent_human_in_loop
from autogen_agent_util.streaming_util import autogen_agent_streaming
from models import Any, ErrorResponse, RunCreateStateless, Union
from langchain_core.messages import AIMessage
from llamindex_agent_util.llamaindex_agent import llama_index_agent

router = APIRouter(tags=["Stateless Runs"])


@router.post(
    "/runs",
    response_model=Any,
    responses={
        "404": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
    },
    tags=["Stateless Runs"],
)
# async function because autogen_agent_util is async
async def run_stateless_runs_post(body: RunCreateStateless) -> Union[Any, ErrorResponse]:
    """
    Asynchronously processes a stateless run request and returns the result.

    Args:
        body (RunCreateStateless): The request body containing the run details.

    Returns:
        Union[Any, ErrorResponse]: The result of the run or an error response.
    """
    # Extract the query input from the request body.
    query_input = body.input[0]['query'] if isinstance(body.input, list) else body.input['query']
    print(f"Received query: {query_input}")
    # Run the autogen agent with the extracted query input and await the output.
    output_data = await autogen_agent(query_input)
    print(f"Output: {output_data}")

    return {"query": query_input, "output": output_data}


@router.post(
    "/runs/stream",
    response_model=str,
    responses={
        "404": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
    },
    tags=["Stateless Runs"],
)
def stream_run_stateless_runs_stream_post(
        body: RunCreateStateless,
) -> Union[str, ErrorResponse]:
    """
    Create Run, Stream Output

    This endpoint accepts a JSON payload describing a run to be executed in stream mode.
    The payload is automatically parsed into a `RunCreateStateless` object.
    """
    try:
        # Convert the validated Pydantic model to a dictionary.
        # Using model_dump() is recommended in Pydantic v2 over the deprecated dict() method.
        payload = body.model_dump()
        logging.debug("Decoded payload: %s", payload)

        # Extract assistant_id from the payload
        assistant_id = payload.get("assistant_id")

        # Validate that the assistant_id is not empty.
        if not payload.get("assistant_id"):
            msg = "assistant_id is required and cannot be empty."
            logging.error(msg)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=msg,
            )

        # Validate the config section: ensure that config.tags is a non-empty list.
        config = payload.get("config", {})

        # -----------------------------------------------
        # Extract the human input content from the payload.
        # We expect the content to be located at: payload["input"]["messages"][0]["content"]
        # -----------------------------------------------
        try:
            # Retrieve the 'input' field and ensure it is a dictionary.
            input_field = payload.get("input")
            if not isinstance(input_field, dict):
                raise ValueError("The 'input' field should be a dictionary.")

            # Retrieve the 'messages' list from the 'input' dictionary.
            messages = input_field.get("messages")
            if not isinstance(messages, list) or not messages:
                raise ValueError("The 'input.messages' field should be a non-empty list.")

            # Access the first message in the list.
            first_message = messages[0]
            if not isinstance(first_message, dict):
                raise ValueError("The first element in 'input.messages' should be a dictionary.")

            # Extract the 'content' from the first message.
            human_input_content = first_message.get("content")
            if human_input_content is None:
                raise ValueError("Missing 'content' in the first message of 'input.messages'.")

            # Small helper function
            async def run_autogen(human_input: str) -> str:
                # Run the autogen agent with the extracted query input and await the output.
                output_data = await autogen_agent(human_input)
                return output_data

            async def run_autogen_human_in_loop(human_input: str) -> str:
                # Run the autogen agent with the extracted query input and human_in_loop.
                output_data = await autogen_agent_human_in_loop(human_input)
                return output_data

            # -----------------------------------------------
            # Define a generator function for SSE streaming.
            # -----------------------------------------------
            async def event_generator():
                """
                Generator function to yield SSE events with JSON-formatted data.
                The event data is serialized as JSON and prefixed with 'data:'.
                """
                # Create a dictionary with the response information.
                
                if assistant_id == "autogen":
                    common_response = await run_autogen(human_input_content)
                    output_data = common_response["content"]
                elif assistant_id == "autogen_human_in_loop":
                    common_response = await run_autogen_human_in_loop(human_input_content)
                    output_data = common_response["content"]
                elif assistant_id == "llama_index":
                    common_response = llama_index_agent(human_input_content)
                    output_data = common_response["content"]
                else:
                    raise ValueError("Unrecognized Agent")

                event_data = {
                    "messages": [AIMessage(output_data).model_dump()],
                }
                # Serialize the dictionary as JSON and yield as an SSE event.
                
                # The event name here, "updates" MUST match the stream_mode on the client
                yield f"event: messages\ndata: {json.dumps(event_data)}\n\n"
                # This is for interrupts
                # yield f"event: updates\ndata: {json.dumps(event_data)}\n\n"
                # If more events are needed, add additional yields here.

            # Return a StreamingResponse with the SSE generator and the proper content type.
            return StreamingResponse(event_generator(), media_type="text/event-stream")

        except Exception as e:
            # Log and raise an HTTP 422 error if extraction fails.
            msg = f"Error extracting human input content: {str(e)}"
            logging.error(msg)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=msg,
            )

        # Continue processing the run request after successful validations and content extraction.
        logging.info("Run creation request validated and accepted: %s", payload)

        # In a real application, additional processing (like starting a background task) would occur here.
        return Response("Run processing started successfully.", status_code=status.HTTP_200_OK)

    except HTTPException as http_exc:
        # Log HTTP exceptions and re-raise them so that FastAPI can generate the appropriate response.
        logging.error("HTTP error during run processing: %s", http_exc.detail)
        raise http_exc

    except Exception as exc:
        # Catch unexpected exceptions, log them, and return a 500 Internal Server Error.
        logging.exception("An unexpected error occurred while processing the run.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

@router.post(
    "/runs/stream/agent",
    response_model=str,
    responses={
        "404": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
    },
    tags=["Stateless Runs"],
)
def stream_run_stateless_runs_stream_post_agent(
        body: RunCreateStateless,
) -> Union[str, ErrorResponse]:
    """
        Create Run, Stream Output using Agent

        This endpoint accepts a JSON payload describing a run to be executed in stream mode using an agent.
        The payload is automatically parsed into a `RunCreateStateless` object.

        Args:
            body (RunCreateStateless): The request body containing the run details.

        Returns:
            Union[str, ErrorResponse]: The streaming response or an error response.
        """
    # Extract the query input from the request body.
    query_input = body.input[0]['query'] if isinstance(body.input, list) else body.input['query']
    print(f"Received query: {query_input}")
    # Create a StreamingResponse with the autogen_agent_streaming generator and the proper content type.
    stream_response = StreamingResponse(autogen_agent_streaming(query_input), media_type="text/event-stream")

    return stream_response

@router.post(
    "/runs/wait",
    response_model=Any,
    responses={
        "404": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
        "422": {"model": ErrorResponse},
    },
    tags=["Stateless Runs"],
)
def wait_run_stateless_runs_wait_post(
        body: RunCreateStateless,
) -> Union[Any, ErrorResponse]:
    """
    Create Run, Wait for Output
    """
    pass
