import os
from typing import AsyncGenerator, Callable, Generator, Optional, Union

import httpx
import litellm
from litellm import CustomLLM, GenericStreamingChunk, HTTPHandler, ModelResponse, AsyncHTTPHandler

from proxy.convert_stream import to_generic_streaming_chunk
from proxy.route_model import route_model


def _add_one_tool_instruction_if_needed(model: str, messages: list) -> list:
    """
    Add instruction to enforce one tool call per response if needed.

    This is added when:
    1. GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE is true (default)
    2. The model is a GPT model (not Claude)
    """
    enforce_one_tool = os.getenv("GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE", "true").lower() == "true"

    # Check if this is a GPT model (after routing it will be openai/gpt-*)
    is_gpt = model.startswith("openai/gpt-")

    if enforce_one_tool and is_gpt:
        # Create a copy of messages to avoid modifying the original
        messages = messages.copy()

        # Add the instruction as a system message at the end
        one_tool_instruction = {
            "role": "system",
            "content": (
                "IMPORTANT: You MUST call only ONE tool at a time per response. "
                "Never attempt to call multiple tools in a single response. "
                "The client cannot handle multiple tool calls in a single response. "
                "After calling one tool, wait for the result before calling another tool."
            ),
        }
        messages.append(one_tool_instruction)

    return messages


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
        litellm.failure_callback = ["langfuse"]  # logs errors to langfuse


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
        model, extra_params = route_model(model)
        optional_params.update(extra_params)

        # Add one-tool instruction if needed for GPT models
        messages = _add_one_tool_instruction_if_needed(model, messages)

        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                **optional_params,
            )
        except Exception as e:
            raise RuntimeError(f"[COMPLETION] Error calling litellm.completion: {e}") from e

        return response

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
        model, extra_params = route_model(model)
        optional_params.update(extra_params)

        # Add one-tool instruction if needed for GPT models
        messages = _add_one_tool_instruction_if_needed(model, messages)

        try:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                **optional_params,
            )
        except Exception as e:
            raise RuntimeError(f"[ACOMPLETION] Error calling litellm.acompletion: {e}") from e
        return response

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
        model, extra_params = route_model(model)

        optional_params.update(extra_params)
        optional_params["stream"] = True

        # Add one-tool instruction if needed for GPT models
        messages = _add_one_tool_instruction_if_needed(model, messages)

        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                **optional_params,
            )
        except Exception as e:
            raise RuntimeError(f"[STREAMING] Error calling litellm.completion: {e}") from e

        for chunk in response:
            yield to_generic_streaming_chunk(chunk)

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
        model, extra_params = route_model(model)

        optional_params.update(extra_params)
        optional_params["stream"] = True

        # Add one-tool instruction if needed for GPT models
        messages = _add_one_tool_instruction_if_needed(model, messages)

        try:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers or {},
                timeout=timeout,
                client=client,
                **optional_params,
            )
        except Exception as e:
            raise RuntimeError(f"[ASTREAMING] Error calling litellm.acompletion: {e}") from e

        async for chunk in response:
            yield to_generic_streaming_chunk(chunk)


custom_llm_router = CustomLLMRouter()
