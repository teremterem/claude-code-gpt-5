from typing import AsyncGenerator, Callable, Generator, Optional, Union

import httpx
import litellm
from litellm import CustomLLM, GenericStreamingChunk, HTTPHandler, ModelResponse, AsyncHTTPHandler

from proxy.config import OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE
from proxy.convert_stream import to_generic_streaming_chunk
from proxy.route_model import route_model


def _adapt_for_openai_in_place(provider_model: str, messages: list, optional_params: dict) -> None:
    """
    Perform necessary prompt injections to adjust certain requests to work with OpenAI models.

    Args:
        provider_model: The provider/model string (e.g., "openai/gpt-5") to adapt for
        messages: Messages list to modify "in place"
        optional_params: Request params which may include tools/functions (may also be modified "in place")

    Returns:
        Modified messages list with additional instruction for OpenAI models
    """
    if not OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE:
        return

    # Only modify for OpenAI models, not Claude models
    if not provider_model.startswith("openai/"):
        return

    if (
        optional_params.get("max_tokens") == 1
        and len(messages) == 1
        and messages[0].get("role") == "user"
        and messages[0].get("content") == "test"
    ):
        # This is a "connectivity test" request for Anthropic models, but OpenAI models respond to it differently =>
        # let's modify the request to make it work with OpenAI models too
        optional_params["max_tokens"] = 100
        messages[0]["role"] = "system"
        messages[0][
            "content"
        ] = "The intention of this request is to test connectivity. Please respond with a single word: OK"
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
            provider_model, extra_params = route_model(model)
            optional_params.update(extra_params)

            # Adapt request for OpenAI models if needed
            _adapt_for_openai_in_place(
                provider_model=provider_model,
                messages=messages,
                optional_params=optional_params,
            )

            response = litellm.completion(
                model=provider_model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                drop_params=True,  # Drop any params which are not supported by the provider
                **optional_params,
            )
            return response

        except Exception as e:
            raise RuntimeError(f"[PROXY FAILURE] CUSTOM_LLM_ROUTER.COMPLETION: {e}") from e

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
            provider_model, extra_params = route_model(model)
            optional_params.update(extra_params)

            # Adapt request for OpenAI models if needed
            _adapt_for_openai_in_place(
                provider_model=provider_model,
                messages=messages,
                optional_params=optional_params,
            )

            response = await litellm.acompletion(
                model=provider_model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                drop_params=True,  # Drop any params which are not supported by the provider
                **optional_params,
            )
            return response

        except Exception as e:
            raise RuntimeError(f"[PROXY FAILURE] CUSTOM_LLM_ROUTER.ACOMPLETION: {e}") from e

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
            provider_model, extra_params = route_model(model)
            optional_params.update(extra_params)
            optional_params["stream"] = True

            # Adapt request for OpenAI models if needed
            _adapt_for_openai_in_place(
                provider_model=provider_model,
                messages=messages,
                optional_params=optional_params,
            )

            response = litellm.completion(
                model=provider_model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                drop_params=True,  # Drop any params which are not supported by the provider
                **optional_params,
            )
            for chunk in response:
                generic_chunk = to_generic_streaming_chunk(chunk)
                yield generic_chunk

        except Exception as e:
            raise RuntimeError(f"[PROXY FAILURE] CUSTOM_LLM_ROUTER.STREAMING: {e}") from e

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
            provider_model, extra_params = route_model(model)
            optional_params.update(extra_params)
            optional_params["stream"] = True

            # Adapt request for OpenAI models if needed
            _adapt_for_openai_in_place(
                provider_model=provider_model,
                messages=messages,
                optional_params=optional_params,
            )

            response = await litellm.acompletion(
                model=provider_model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                drop_params=True,  # Drop any params which are not supported by the provider
                **optional_params,
            )
            async for chunk in response:
                generic_chunk = to_generic_streaming_chunk(chunk)
                yield generic_chunk

        except Exception as e:
            raise RuntimeError(f"[PROXY FAILURE] CUSTOM_LLM_ROUTER.ASTREAMING: {e}") from e


custom_llm_router = CustomLLMRouter()
