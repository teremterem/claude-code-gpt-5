from typing import AsyncGenerator, Callable, Generator, Optional, Union

import httpx
import litellm
from litellm import CustomLLM, GenericStreamingChunk, HTTPHandler, ModelResponse, AsyncHTTPHandler

from proxy.config import ANTHROPIC, ENFORCE_ONE_TOOL_CALL_PER_RESPONSE, ProxyError
from proxy.convert_stream import to_generic_streaming_chunk
from proxy.route_model import route_model


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
            final_model, extra_params = route_model(model)
            optional_params.update(extra_params)

            # For Langfuse
            optional_params.setdefault("metadata", {})["trace_name"] = "OUTBOUND-from-completion"

            _adapt_for_non_anthropic_models(
                model=final_model,
                messages=messages,
                optional_params=optional_params,
            )

            response = litellm.completion(
                model=final_model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                drop_params=True,  # Drop any params that are not supported by the provider
                **optional_params,
            )
            return response

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
            final_model, extra_params = route_model(model)
            optional_params.update(extra_params)

            # For Langfuse
            optional_params.setdefault("metadata", {})["trace_name"] = "OUTBOUND-from-acompletion"

            _adapt_for_non_anthropic_models(
                model=final_model,
                messages=messages,
                optional_params=optional_params,
            )

            response = await litellm.acompletion(
                model=final_model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                drop_params=True,  # Drop any params that are not supported by the provider
                **optional_params,
            )
            return response

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
            final_model, extra_params = route_model(model)
            optional_params.update(extra_params)
            optional_params["stream"] = True

            # For Langfuse
            optional_params.setdefault("metadata", {})["trace_name"] = "OUTBOUND-from-streaming"

            _adapt_for_non_anthropic_models(
                model=final_model,
                messages=messages,
                optional_params=optional_params,
            )

            response = litellm.completion(
                model=final_model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                drop_params=True,  # Drop any params that are not supported by the provider
                **optional_params,
            )
            for chunk in response:
                generic_chunk = to_generic_streaming_chunk(chunk)
                yield generic_chunk

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
            final_model, extra_params = route_model(model)
            optional_params.update(extra_params)
            optional_params["stream"] = True

            # For Langfuse
            optional_params.setdefault("metadata", {})["trace_name"] = "OUTBOUND-from-astreaming"

            _adapt_for_non_anthropic_models(
                model=final_model,
                messages=messages,
                optional_params=optional_params,
            )

            response = await litellm.acompletion(
                model=final_model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                drop_params=True,  # Drop any params that are not supported by the provider
                **optional_params,
            )
            async for chunk in response:
                generic_chunk = to_generic_streaming_chunk(chunk)
                yield generic_chunk

        except Exception as e:
            raise ProxyError(e) from e


custom_llm_router = CustomLLMRouter()
