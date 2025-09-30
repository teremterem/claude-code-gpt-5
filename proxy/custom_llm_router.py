import json
from datetime import datetime, timezone
from typing import AsyncGenerator, Callable, Generator, Optional, Union

import httpx
import litellm
from litellm import (
    CustomLLM,
    GenericStreamingChunk,
    HTTPHandler,
    ModelResponse,
    AsyncHTTPHandler,
    ResponsesAPIResponse,
)

from proxy.config import ANTHROPIC, ENFORCE_ONE_TOOL_CALL_PER_RESPONSE, RESPAPI_TRACES_DIR, RESPAPI_TRACING_ENABLED
from proxy.route_model import route_model
from proxy.utils import (
    ProxyError,
    convert_chat_messages_to_responses_items,
    convert_chat_params_to_responses,
    convert_responses_to_model_response,
    to_generic_streaming_chunk,
)


def _adapt_for_non_anthropic_models(model: str, messages: list, optional_params: dict) -> None:
    """
    Perform necessary prompt injections to adjust certain requests to work with non-Anthropic models.

    Args:
        model: The model string (e.g., "openai/gpt-5") to adapt for
        messages: Messages list to modify "in place"
        optional_params: Request params which may include tools/functions (may also be modified "in place")

    Returns:
        Modified messages list with additional instruction for non-Anthropic models
    """
    if model.startswith(f"{ANTHROPIC}/"):
        # Do not alter requests for Anthropic models
        return

    if (
        optional_params.get("max_tokens") == 1
        and len(messages) == 1
        and messages[0].get("role") == "user"
        and messages[0].get("content") == "test"
    ):
        # This is a "connectivity test" request by Claude Code => we need to make sure non-Anthropic models don't fail
        # because of exceeding max_tokens
        optional_params["max_tokens"] = 100
        messages[0]["role"] = "system"
        messages[0][
            "content"
        ] = "The intention of this request is to test connectivity. Please respond with a single word: OK"
        return

    if not ENFORCE_ONE_TOOL_CALL_PER_RESPONSE:
        return

    # Only add the instruction if at least two tools and/or functions are present in the request (in total)
    num_tools = len(optional_params.get("tools") or []) + len(optional_params.get("functions") or [])
    if num_tools < 2:
        return

    # Add the single tool call instruction as the last message
    tool_instruction = {
        "role": "system",
        "content": (
            "IMPORTANT: When using tools, call AT MOST one tool per response. Never attempt multiple tool calls in a "
            "single response. The client does not support multiple tool calls in a single response. If multiple "
            "tools are needed, choose the next best single tool, return exactly one tool call, and wait for the next "
            "turn."
        ),
    }
    messages.append(tool_instruction)


def _generate_timestamp() -> str:
    """
    Generate timestamp in format yyyymmdd_hhmmss_mmmm.
    """
    now = datetime.now(timezone.utc)
    return now.strftime("%Y%m%d_%H%M%S_%f")[:-2]  # Remove last 3 digits to get milliseconds


class CustomLLMRouter(CustomLLM):
    """
    Routes model requests to the correct provider and parameters.
    """

    # pylint: disable=too-many-positional-arguments,too-many-locals

    def completion(
        self,
        model: str,
        messages: list,
        api_base: str,
        custom_prompt_dict: dict,
        model_response: ModelResponse,
        print_verbose: Callable,
        encoding,
        api_key,
        logging_obj,
        optional_params: dict,
        acompletion=None,
        litellm_params=None,
        logger_fn=None,
        headers=None,
        timeout: Optional[Union[float, httpx.Timeout]] = None,
        client: Optional[HTTPHandler] = None,
    ) -> ModelResponse:
        try:
            timestamp = _generate_timestamp()
            calling_method = "COMPLETION"

            final_model, extra_params = route_model(model)
            optional_params.update(extra_params)
            optional_params["stream"] = False
            optional_params.pop("temperature", None)  # TODO How to do it only when needed ?

            # For Langfuse
            optional_params.setdefault("metadata", {})["trace_name"] = f"{timestamp}-OUTBOUND-completion"

            _adapt_for_non_anthropic_models(
                model=final_model,
                messages=messages,
                optional_params=optional_params,
            )

            messages_respapi = convert_chat_messages_to_responses_items(messages)
            params_respapi = convert_chat_params_to_responses(optional_params)

            if RESPAPI_TRACING_ENABLED:
                _write_request_trace(
                    timestamp=timestamp,
                    calling_method=calling_method,
                    messages_complapi=messages,
                    params_complapi=optional_params,
                    messages_respapi=messages_respapi,
                    params_respapi=params_respapi,
                )

            messages = messages_respapi
            optional_params = params_respapi

            response = litellm.responses(  # TODO Check all params are supported
                model=final_model,
                input=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                **optional_params,
            )
            response_complapi = convert_responses_to_model_response(response)

            if RESPAPI_TRACING_ENABLED:
                _write_response_trace(timestamp, calling_method, response, response_complapi)

            return response_complapi

        except Exception as e:
            raise ProxyError(e) from e

    async def acompletion(
        self,
        model: str,
        messages: list,
        api_base: str,
        custom_prompt_dict: dict,
        model_response: ModelResponse,
        print_verbose: Callable,
        encoding,
        api_key,
        logging_obj,
        optional_params: dict,
        acompletion=None,
        litellm_params=None,
        logger_fn=None,
        headers=None,
        timeout: Optional[Union[float, httpx.Timeout]] = None,
        client: Optional[AsyncHTTPHandler] = None,
    ) -> ModelResponse:
        try:
            timestamp = _generate_timestamp()
            calling_method = "ACOMPLETION"

            final_model, extra_params = route_model(model)
            optional_params.update(extra_params)
            optional_params["stream"] = False
            optional_params.pop("temperature", None)  # TODO How to do it only when needed ?

            # For Langfuse
            optional_params.setdefault("metadata", {})["trace_name"] = f"{timestamp}-OUTBOUND-acompletion"

            _adapt_for_non_anthropic_models(
                model=final_model,
                messages=messages,
                optional_params=optional_params,
            )

            messages_respapi = convert_chat_messages_to_responses_items(messages)
            params_respapi = convert_chat_params_to_responses(optional_params)

            if RESPAPI_TRACING_ENABLED:
                _write_request_trace(
                    timestamp=timestamp,
                    calling_method=calling_method,
                    messages_complapi=messages,
                    params_complapi=optional_params,
                    messages_respapi=messages_respapi,
                    params_respapi=params_respapi,
                )

            messages = messages_respapi
            optional_params = params_respapi

            response = await litellm.aresponses(  # TODO Check all params are supported
                model=final_model,
                input=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                **optional_params,
            )
            response_complapi = convert_responses_to_model_response(response)

            if RESPAPI_TRACING_ENABLED:
                _write_response_trace(timestamp, calling_method, response, response_complapi)

            return response_complapi

        except Exception as e:
            raise ProxyError(e) from e

    def streaming(
        self,
        model: str,
        messages: list,
        api_base: str,
        custom_prompt_dict: dict,
        model_response: ModelResponse,
        print_verbose: Callable,
        encoding,
        api_key,
        logging_obj,
        optional_params: dict,
        acompletion=None,
        litellm_params=None,
        logger_fn=None,
        headers=None,
        timeout: Optional[Union[float, httpx.Timeout]] = None,
        client: Optional[HTTPHandler] = None,
    ) -> Generator[GenericStreamingChunk, None, None]:
        try:
            timestamp = _generate_timestamp()
            calling_method = "STREAMING"

            final_model, extra_params = route_model(model)
            optional_params.update(extra_params)
            optional_params["stream"] = True
            optional_params.pop("temperature", None)  # TODO How to do it only when needed ?

            # For Langfuse
            optional_params.setdefault("metadata", {})["trace_name"] = f"{timestamp}-OUTBOUND-streaming"

            _adapt_for_non_anthropic_models(
                model=final_model,
                messages=messages,
                optional_params=optional_params,
            )

            messages_respapi = convert_chat_messages_to_responses_items(messages)
            params_respapi = convert_chat_params_to_responses(optional_params)

            if RESPAPI_TRACING_ENABLED:
                _write_request_trace(
                    timestamp=timestamp,
                    calling_method=calling_method,
                    messages_complapi=messages,
                    params_complapi=optional_params,
                    messages_respapi=messages_respapi,
                    params_respapi=params_respapi,
                )

            messages = messages_respapi
            optional_params = params_respapi

            response = litellm.responses(  # TODO Check all params are supported
                model=final_model,
                input=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                **optional_params,
            )

            responses_chunks = []
            generic_chunks = []
            for chunk in response:
                generic_chunk = to_generic_streaming_chunk(chunk)

                if RESPAPI_TRACING_ENABLED:
                    responses_chunks.append(chunk)
                    generic_chunks.append(generic_chunk)

                yield generic_chunk

            if RESPAPI_TRACING_ENABLED:
                _write_streaming_response_trace(timestamp, calling_method, responses_chunks, generic_chunks)

        except Exception as e:
            raise ProxyError(e) from e

    async def astreaming(
        self,
        model: str,
        messages: list,
        api_base: str,
        custom_prompt_dict: dict,
        model_response: ModelResponse,
        print_verbose: Callable,
        encoding,
        api_key,
        logging_obj,
        optional_params: dict,
        acompletion=None,
        litellm_params=None,
        logger_fn=None,
        headers=None,
        timeout: Optional[Union[float, httpx.Timeout]] = None,
        client: Optional[AsyncHTTPHandler] = None,
    ) -> AsyncGenerator[GenericStreamingChunk, None]:
        try:
            timestamp = _generate_timestamp()
            calling_method = "ASTREAMING"

            final_model, extra_params = route_model(model)
            optional_params.update(extra_params)
            optional_params["stream"] = True
            optional_params.pop("temperature", None)  # TODO How to do it only when needed ?

            # For Langfuse
            optional_params.setdefault("metadata", {})["trace_name"] = f"{timestamp}-OUTBOUND-astreaming"

            _adapt_for_non_anthropic_models(
                model=final_model,
                messages=messages,
                optional_params=optional_params,
            )

            messages_respapi = convert_chat_messages_to_responses_items(messages)
            params_respapi = convert_chat_params_to_responses(optional_params)

            if RESPAPI_TRACING_ENABLED:
                _write_request_trace(
                    timestamp=timestamp,
                    calling_method=calling_method,
                    messages_complapi=messages,
                    params_complapi=optional_params,
                    messages_respapi=messages_respapi,
                    params_respapi=params_respapi,
                )

            messages = messages_respapi
            optional_params = params_respapi

            response = await litellm.aresponses(  # TODO Check all params are supported
                model=final_model,
                input=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                **optional_params,
            )

            responses_chunks = []
            generic_chunks = []
            async for chunk in response:
                generic_chunk = to_generic_streaming_chunk(chunk)

                if RESPAPI_TRACING_ENABLED:
                    responses_chunks.append(chunk)
                    generic_chunks.append(generic_chunk)

                yield generic_chunk

            if RESPAPI_TRACING_ENABLED:
                _write_streaming_response_trace(timestamp, calling_method, responses_chunks, generic_chunks)

        except Exception as e:
            raise ProxyError(e) from e


custom_llm_router = CustomLLMRouter()


def _write_request_trace(
    *,
    timestamp: str,
    calling_method: str,
    messages_complapi: list,
    params_complapi: dict,
    messages_respapi: list,
    params_respapi: dict,
) -> None:
    RESPAPI_TRACES_DIR.mkdir(parents=True, exist_ok=True)
    with (RESPAPI_TRACES_DIR / f"{timestamp}_REQUEST.md").open("w", encoding="utf-8") as f:
        f.write(f"# {calling_method}\n\n")

        f.write("## Request Messages\n\n")

        f.write("### Completion API:\n")
        f.write(f"```json\n{json.dumps(messages_complapi, indent=2)}\n```\n\n")

        f.write("### Responses API:\n")
        f.write(f"```json\n{json.dumps(messages_respapi, indent=2)}\n```\n\n")

        f.write("## Request Params\n\n")

        f.write("### Completion API:\n")
        f.write(f"```json\n{json.dumps(params_complapi, indent=2)}\n```\n\n")

        f.write("### Responses API:\n")
        f.write(f"```json\n{json.dumps(params_respapi, indent=2)}\n```\n")


def _write_response_trace(
    timestamp: str,
    calling_method: str,
    response: ResponsesAPIResponse,
    response_complapi: ModelResponse,
) -> None:
    RESPAPI_TRACES_DIR.mkdir(parents=True, exist_ok=True)
    with (RESPAPI_TRACES_DIR / f"{timestamp}_RESPONSE.md").open("w", encoding="utf-8") as f:
        f.write(f"# {calling_method}\n\n")

        f.write("## Response\n\n")

        f.write("### Responses API:\n")
        f.write(f"```json\n{response.model_dump_json(indent=2)}\n```\n\n")

        f.write("### Completion API:\n")
        f.write(f"```json\n{response_complapi.model_dump_json(indent=2)}\n```\n")


def _write_streaming_response_trace(
    timestamp: str,
    calling_method: str,
    responses_chunks: list,
    generic_chunks: list,
) -> None:
    RESPAPI_TRACES_DIR.mkdir(parents=True, exist_ok=True)
    with (RESPAPI_TRACES_DIR / f"{timestamp}_RESPONSE_STREAM.md").open("w", encoding="utf-8") as f:
        f.write(f"# {calling_method}\n\n")

        for idx, (resp_chunk, gen_chunk) in enumerate(zip(responses_chunks, generic_chunks)):
            f.write(f"## Response Chunk #{idx}\n\n")
            f.write(f"### Responses API:\n```json\n{resp_chunk.model_dump_json(indent=2)}\n```\n\n")
            # TODO Do `gen_chunk.model_dump_json(indent=2)` once it's not just a dict
            f.write(f"### GenericStreamingChunk:\n```json\n{json.dumps(gen_chunk, indent=2)}\n```\n\n")
