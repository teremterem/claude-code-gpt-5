import os
from typing import AsyncGenerator, Callable, Generator, Optional, Union

import httpx
import litellm
from litellm import CustomLLM, GenericStreamingChunk, HTTPHandler, ModelResponse, AsyncHTTPHandler

from proxy.convert_stream import to_generic_streaming_chunk
from proxy.route_model import route_model

# We don't have to do `dotenv.load_dotenv()` - litellm does this for us upon import


if os.getenv("LANGFUSE_SECRET_KEY") or os.getenv("LANGFUSE_PUBLIC_KEY"):
    try:
        import langfuse  # pylint: disable=unused-import
    except ImportError:
        print(
            "\033[1;31mLangfuse is not installed. Please install it with either `uv sync --extra langfuse` or "
            "`uv sync --all-extras`.\033[0m"
        )
    else:
        print("\033[1;34mEnabling Langfuse logging...\033[0m")
        litellm.success_callback = ["langfuse"]
        litellm.failure_callback = ["langfuse"]


SHOULD_ENFORCE_SINGLE_TOOL_CALL = os.getenv("OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE", "true").lower() in (
    "true",
    "1",
    "on",
    "yes",
    "y",
)


def _modify_messages_for_openai(messages: list, provider_model: str, optional_params: dict) -> list:
    """
    Add instruction to enforce single tool call per response for OpenAI models,
    but only if tools/functions are available on the request.

    Args:
        messages: Original messages list
        provider_model: The provider/model string (e.g., "openai/gpt-5")
        optional_params: Request params which may include tools/functions

    Returns:
        Modified messages list with additional instruction for OpenAI models
    """
    if not SHOULD_ENFORCE_SINGLE_TOOL_CALL:
        return messages

    # Only modify for OpenAI models, not Claude models
    if not provider_model.startswith("openai/"):
        return messages

    # Only add the instruction if tools/functions are present in the request
    if not (optional_params.get("tools") or optional_params.get("functions")):
        return messages

    # Create a copy of messages to avoid modifying the original
    modified_messages = messages.copy()

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

    modified_messages.append(tool_instruction)
    return modified_messages


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

            # Adapt messages for OpenAI models if needed
            modified_messages = _modify_messages_for_openai(messages, provider_model, optional_params)

            response = litellm.completion(
                model=provider_model,
                messages=modified_messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                **optional_params,
            )
            return response

        except Exception as e:
            raise RuntimeError(f"[COMPLETION] Error calling litellm.completion: {e}") from e

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

            # Adapt messages for OpenAI models if needed
            modified_messages = _modify_messages_for_openai(messages, provider_model, optional_params)

            response = await litellm.acompletion(
                model=provider_model,
                messages=modified_messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                **optional_params,
            )
            return response

        except Exception as e:
            raise RuntimeError(f"[ACOMPLETION] Error calling litellm.acompletion: {e}") from e

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

            # Adapt messages for OpenAI models if needed
            modified_messages = _modify_messages_for_openai(messages, provider_model, optional_params)

            response = litellm.completion(
                model=provider_model,
                messages=modified_messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                **optional_params,
            )
            for chunk in response:
                generic_chunk = to_generic_streaming_chunk(chunk)
                yield generic_chunk

        except Exception as e:
            raise RuntimeError(f"[STREAMING] Error calling litellm.completion: {e}") from e

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

            # Adapt messages for OpenAI models if needed
            modified_messages = _modify_messages_for_openai(messages, provider_model, optional_params)

            response = await litellm.acompletion(
                model=provider_model,
                messages=modified_messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                **optional_params,
            )
            async for chunk in response:
                generic_chunk = to_generic_streaming_chunk(chunk)
                yield generic_chunk

        except Exception as e:
            raise RuntimeError(f"[ASTREAMING] Error calling litellm.acompletion: {e}") from e


custom_llm_router = CustomLLMRouter()
