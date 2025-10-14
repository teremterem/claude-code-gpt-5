from copy import deepcopy
from typing import AsyncGenerator, Callable, Generator, Optional, Union

import httpx
import litellm
from litellm import (
    BaseResponsesAPIStreamingIterator,
    CustomLLM,
    CustomStreamWrapper,
    GenericStreamingChunk,
    HTTPHandler,
    ModelResponse,
    AsyncHTTPHandler,
    ResponsesAPIResponse,
)

from claude_code_proxy.proxy_config import ANTHROPIC, ENFORCE_ONE_TOOL_CALL_PER_RESPONSE, WRITE_TRACES_TO_FILES
from claude_code_proxy.route_model import ModelRoute
from claude_code_proxy.tracing_in_markdown import (
    write_request_trace,
    write_response_trace,
    write_streaming_response_trace,
)
from common.utils import (
    ProxyError,
    convert_chat_messages_to_respapi,
    convert_chat_params_to_respapi,
    convert_respapi_to_model_response,
    generate_timestamp_local_tz,
    to_generic_streaming_chunk,
)


def _adapt_for_non_anthropic_models(model: str, messages_complapi: list, params_complapi: dict) -> None:
    """
    Perform necessary prompt injections to adjust certain requests to work with
    non-Anthropic models.

    Args:
        model: The model string (e.g., "openai/gpt-5") to adapt for
        messages: Messages list to modify "in place"
        optional_params: Request params which may include tools/functions (may
            also be modified "in place")

    Returns:
        Modified messages list with additional instruction for non-Anthropic
        models
    """
    if model.startswith(f"{ANTHROPIC}/"):
        # Do not alter requests for Anthropic models
        return

    if (
        params_complapi.get("max_tokens") == 1
        and len(messages_complapi) == 1
        and messages_complapi[0].get("role") == "user"
        and messages_complapi[0].get("content") in ["quota", "test"]
    ):
        # This is a "connectivity test" request by Claude Code => we need to make sure non-Anthropic models don't fail
        # because of exceeding max_tokens
        params_complapi["max_tokens"] = 100
        messages_complapi[0]["role"] = "system"
        messages_complapi[0][
            "content"
        ] = "The intention of this request is to test connectivity. Please respond with a single word: OK"
        return

    if not ENFORCE_ONE_TOOL_CALL_PER_RESPONSE:
        return

    # Only add the instruction if at least two tools and/or functions are present in the request (in total)
    num_tools = len(params_complapi.get("tools") or []) + len(params_complapi.get("functions") or [])
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
    messages_complapi.append(tool_instruction)


class RoutedRequest:
    def __init__(
        self,
        *,
        calling_method: str,
        model: str,
        messages_original: list,
        params_original: dict,
        stream: bool,
    ) -> None:
        self.timestamp = generate_timestamp_local_tz()
        self.calling_method = calling_method
        self.model_route = ModelRoute(model)

        self.messages_original = messages_original
        self.params_original = params_original

        self.messages_complapi = deepcopy(self.messages_original)
        self.params_complapi = deepcopy(self.params_original)

        self.params_complapi.update(self.model_route.extra_params)
        self.params_complapi["stream"] = stream

        if self.model_route.use_responses_api:
            # TODO What's a more reasonable way to decide when to unset
            #  temperature ?
            self.params_complapi.pop("temperature", None)

        # For Langfuse
        trace_name = f"{self.timestamp}-OUTBOUND-{self.calling_method}"
        self.params_complapi.setdefault("metadata", {})["trace_name"] = trace_name

        _adapt_for_non_anthropic_models(
            model=self.model_route.target_model,
            messages_complapi=self.messages_complapi,
            params_complapi=self.params_complapi,
        )

        if self.model_route.use_responses_api:
            self.messages_respapi = convert_chat_messages_to_respapi(self.messages_complapi)
            self.params_respapi = convert_chat_params_to_respapi(self.params_complapi)
        else:
            self.messages_respapi = None
            self.params_respapi = None

        if WRITE_TRACES_TO_FILES:
            write_request_trace(
                timestamp=self.timestamp,
                calling_method=self.calling_method,
                messages_original=self.messages_original,
                params_original=self.params_original,
                messages_complapi=self.messages_complapi,
                params_complapi=self.params_complapi,
                messages_respapi=self.messages_respapi,
                params_respapi=self.params_respapi,
            )


class ClaudeCodeRouter(CustomLLM):
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
            routed_request = RoutedRequest(
                calling_method="completion",
                model=model,
                messages_original=messages,
                params_original=optional_params,
                stream=False,
            )

            if routed_request.model_route.use_responses_api:
                response_respapi: ResponsesAPIResponse = litellm.responses(
                    # TODO Make sure all params are supported
                    model=routed_request.model_route.target_model,
                    input=routed_request.messages_respapi,
                    logger_fn=logger_fn,
                    headers=headers or {},
                    timeout=timeout,
                    client=client,
                    **routed_request.params_respapi,
                )
                response_complapi: ModelResponse = convert_respapi_to_model_response(response_respapi)

            else:
                response_respapi = None
                response_complapi: ModelResponse = litellm.completion(
                    model=routed_request.model_route.target_model,
                    messages=routed_request.messages_complapi,
                    logger_fn=logger_fn,
                    headers=headers or {},
                    timeout=timeout,
                    client=client,
                    # Drop any params that are not supported by the provider
                    drop_params=True,
                    **routed_request.params_complapi,
                )

            if WRITE_TRACES_TO_FILES:
                write_response_trace(
                    timestamp=routed_request.timestamp,
                    calling_method=routed_request.calling_method,
                    response_respapi=response_respapi,
                    response_complapi=response_complapi,
                )

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
            routed_request = RoutedRequest(
                calling_method="acompletion",
                model=model,
                messages_original=messages,
                params_original=optional_params,
                stream=False,
            )

            if routed_request.model_route.use_responses_api:
                response_respapi: ResponsesAPIResponse = await litellm.aresponses(
                    # TODO Make sure all params are supported
                    model=routed_request.model_route.target_model,
                    input=routed_request.messages_respapi,
                    logger_fn=logger_fn,
                    headers=headers or {},
                    timeout=timeout,
                    client=client,
                    **routed_request.params_respapi,
                )
                response_complapi: ModelResponse = convert_respapi_to_model_response(response_respapi)

            else:
                response_respapi = None
                response_complapi: ModelResponse = await litellm.acompletion(
                    model=routed_request.model_route.target_model,
                    messages=routed_request.messages_complapi,
                    logger_fn=logger_fn,
                    headers=headers or {},
                    timeout=timeout,
                    client=client,
                    # Drop any params that are not supported by the provider
                    drop_params=True,
                    **routed_request.params_complapi,
                )

            if WRITE_TRACES_TO_FILES:
                write_response_trace(
                    timestamp=routed_request.timestamp,
                    calling_method=routed_request.calling_method,
                    response_respapi=response_respapi,
                    response_complapi=response_complapi,
                )

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
            routed_request = RoutedRequest(
                calling_method="streaming",
                model=model,
                messages_original=messages,
                params_original=optional_params,
                stream=True,
            )

            if routed_request.model_route.use_responses_api:
                resp_stream: BaseResponsesAPIStreamingIterator = litellm.responses(
                    # TODO Make sure all params are supported
                    model=routed_request.model_route.target_model,
                    input=routed_request.messages_respapi,
                    logger_fn=logger_fn,
                    headers=headers or {},
                    timeout=timeout,
                    client=client,
                    **routed_request.params_respapi,
                )

            else:
                resp_stream: CustomStreamWrapper = litellm.completion(
                    model=routed_request.model_route.target_model,
                    messages=routed_request.messages_complapi,
                    logger_fn=logger_fn,
                    headers=headers or {},
                    timeout=timeout,
                    client=client,
                    # Drop any params that are not supported by the provider
                    drop_params=True,
                    **routed_request.params_complapi,
                )

            respapi_chunks = []
            complapi_chunks = []
            generic_chunks = []

            for resp_chunk in resp_stream:
                generic_chunk = to_generic_streaming_chunk(resp_chunk)

                if WRITE_TRACES_TO_FILES:
                    if routed_request.model_route.use_responses_api:
                        respapi_chunks.append(resp_chunk)
                    else:
                        complapi_chunks.append(resp_chunk)
                    generic_chunks.append(generic_chunk)

                yield generic_chunk

            if WRITE_TRACES_TO_FILES:
                write_streaming_response_trace(
                    timestamp=routed_request.timestamp,
                    calling_method=routed_request.calling_method,
                    respapi_chunks=respapi_chunks,
                    complapi_chunks=complapi_chunks,
                    generic_chunks=generic_chunks,
                )

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
            routed_request = RoutedRequest(
                calling_method="astreaming",
                model=model,
                messages_original=messages,
                params_original=optional_params,
                stream=True,
            )

            if routed_request.model_route.use_responses_api:
                resp_stream: BaseResponsesAPIStreamingIterator = await litellm.aresponses(
                    # TODO Make sure all params are supported
                    model=routed_request.model_route.target_model,
                    input=routed_request.messages_respapi,
                    logger_fn=logger_fn,
                    headers=headers or {},
                    timeout=timeout,
                    client=client,
                    **routed_request.params_respapi,
                )

            else:
                resp_stream: CustomStreamWrapper = await litellm.acompletion(
                    model=routed_request.model_route.target_model,
                    messages=routed_request.messages_complapi,
                    logger_fn=logger_fn,
                    headers=headers or {},
                    timeout=timeout,
                    client=client,
                    # Drop any params that are not supported by the provider
                    drop_params=True,
                    **routed_request.params_complapi,
                )

            respapi_chunks = []
            complapi_chunks = []
            generic_chunks = []

            async for resp_chunk in resp_stream:
                generic_chunk = to_generic_streaming_chunk(resp_chunk)

                if WRITE_TRACES_TO_FILES:
                    if routed_request.model_route.use_responses_api:
                        respapi_chunks.append(resp_chunk)
                    else:
                        complapi_chunks.append(resp_chunk)
                    generic_chunks.append(generic_chunk)

                yield generic_chunk

            if WRITE_TRACES_TO_FILES:
                write_streaming_response_trace(
                    timestamp=routed_request.timestamp,
                    calling_method=routed_request.calling_method,
                    respapi_chunks=respapi_chunks,
                    complapi_chunks=complapi_chunks,
                    generic_chunks=generic_chunks,
                )

        except Exception as e:
            raise ProxyError(e) from e


claude_code_router = ClaudeCodeRouter()
