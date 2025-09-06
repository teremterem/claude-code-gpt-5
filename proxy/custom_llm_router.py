import os
from typing import AsyncGenerator, Callable, Generator, Optional, Union

import httpx
import litellm
from litellm import CustomLLM, GenericStreamingChunk, HTTPHandler, ModelResponse, AsyncHTTPHandler

from proxy.convert_stream import to_generic_streaming_chunk
from proxy.route_model import route_model


def _enforce_single_tool_message_enabled() -> bool:
    """Return True if we should append the single-tool-call instruction.

    Defaults to True when the env var is unset. Treats common truthy values
    ("1", "true", "yes", "on") as True and falsy values ("0", "false",
    "no", "off") as False.
    """
    raw = os.getenv("GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE")
    if raw is None:
        return True
    raw_l = raw.strip().lower()
    if raw_l in {"1", "true", "yes", "on"}:
        return True
    if raw_l in {"0", "false", "no", "off"}:
        return False
    # Fallback: non-empty values default to True
    return bool(raw_l)


_SINGLE_TOOL_CALL_INSTRUCTION = (
    "IMPORTANT: The CLI can only process one tool call per response. "
    "Always call at most one tool in a single response. If multiple tools are needed, "
    "choose the next best single tool, return exactly one tool call, and wait for the next turn."
)


def _maybe_append_single_tool_instruction(provider_model: str, messages: list) -> list:
    """Append enforcement instruction as the last message for GPT models when enabled.

    The instruction is only added for OpenAI GPT models, not for Claude/Anthropic.
    """
    try:
        is_gpt = provider_model.startswith("openai/")
    except Exception:  # TODO WTF ?!  # pylint: disable=broad-exception-caught
        is_gpt = False

    if is_gpt and _enforce_single_tool_message_enabled():
        # Append as a final system message without mutating original list
        return [*messages, {"role": "system", "content": _SINGLE_TOOL_CALL_INSTRUCTION}]
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

        try:
            messages = _maybe_append_single_tool_instruction(model, messages)
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

        try:
            messages = _maybe_append_single_tool_instruction(model, messages)
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

        try:
            messages = _maybe_append_single_tool_instruction(model, messages)
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

        try:
            messages = _maybe_append_single_tool_instruction(model, messages)
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
