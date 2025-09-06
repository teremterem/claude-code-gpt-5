import os
from typing import AsyncGenerator, Callable, Generator, Optional, Union

import httpx
import litellm
from litellm import CustomLLM, GenericStreamingChunk, HTTPHandler, ModelResponse, AsyncHTTPHandler

from proxy.convert_stream import to_generic_streaming_chunk
from proxy.route_model import route_model


def _should_enforce_single_tool_call() -> bool:
    """Return True if we should append an instruction enforcing a single tool call per response.

    Defaults to True when env var is unset. Accept typical falsy values to disable.
    """
    val = os.getenv("GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE", "true").strip().lower()
    return val not in {"false", "0", "no", "off"}


def _append_single_tool_instruction_if_needed(provider_model: str, messages: list) -> list:
    """Append a final system instruction for GPT models to ensure only one tool call per response.

    - Only applies when env flag is enabled and provider is OpenAI (GPT), not Anthropic.
    - Appends as the last message to the LLM input.
    """
    # Quick return if disabled
    if not _should_enforce_single_tool_call():
        return messages

    # Only enforce for OpenAI/GPT models; skip Anthropic/Claude
    if not provider_model.startswith("openai/"):
        return messages

    # Create a shallow copy to avoid mutating caller-provided list in place
    new_messages = list(messages)

    instruction = (
        "Important: When using tools, call at most one tool per response. "
        "Never attempt multiple tool calls in a single response; the CLI cannot handle it."
    )
    new_messages.append({"role": "system", "content": instruction})
    return new_messages


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

        # Ensure single-tool-call instruction is appended for GPT models when enabled
        messages = _append_single_tool_instruction_if_needed(model, messages)

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

        # Ensure single-tool-call instruction is appended for GPT models when enabled
        messages = _append_single_tool_instruction_if_needed(model, messages)

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

        # Ensure single-tool-call instruction is appended for GPT models when enabled
        messages = _append_single_tool_instruction_if_needed(model, messages)

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

        # Ensure single-tool-call instruction is appended for GPT models when enabled
        messages = _append_single_tool_instruction_if_needed(model, messages)

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
