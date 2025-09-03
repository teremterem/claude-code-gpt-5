import logging
import re
from typing import Any, AsyncGenerator, Callable, Generator, Optional, Union

import httpx
import litellm
from litellm import CustomLLM, GenericStreamingChunk, HTTPHandler, ModelResponse, AsyncHTTPHandler


def route_model(requested_model: str) -> tuple[str, dict[str, Any]]:
    """
    Map a friendly model alias to a provider model and extra params.

    Supported patterns:
    - gpt-5(-mini|-nano)?-reason-(minimal|low|medium|high)
      -> maps to openai/gpt-5[(-mini|-nano)] with reasoning_effort
    - claude-* -> maps directly to anthropic/claude-*

    Returns a tuple of (provider_model, extra_params)
    """
    model = requested_model.strip()

    # Claude passthrough (kept for Claude Code fast model usage)
    if model.startswith("claude-"):
        final = f"anthropic/{model}"
        # TODO Make it possible to disable this print ? (turn it into a log record ?)
        print(f"\033[1m\033[32m{requested_model}\033[0m -> \033[1m\033[36m{final}\033[0m")
        return final, {}

    # GPT-5 family with reasoning effort
    m = re.fullmatch(
        r"gpt-5(?P<variant>-(mini|nano))?-reason-(?P<effort>minimal|low|medium|high)",
        model,
    )
    if m:
        variant = m.group("variant") or ""
        effort = m.group("effort")
        provider_model = f"openai/gpt-5{variant or ''}"
        # TODO Make it possible to disable this print ? (turn it into a log record ?)
        print(
            f"\033[1m\033[32m{requested_model}\033[0m -> \033[1m\033[36m{provider_model}\033[0m "
            f"[\033[1m\033[33mreasoning_effort: {effort}\033[0m]"
        )
        return provider_model, {"reasoning_effort": effort}

    # Default passthrough – use as-is, but log for visibility
    # If we ever want to restrict models, raise a ValueError here instead.
    logger.error("%s -> %s", requested_model, model)
    return model, {}


def _to_generic_streaming_chunk(chunk: Any) -> GenericStreamingChunk:
    """Best-effort convert a LiteLLM ModelResponseStream chunk into GenericStreamingChunk.

    GenericStreamingChunk TypedDict keys:
      - text: str (required)
      - is_finished: bool (required)
      - finish_reason: str (required)
      - usage: Optional[ChatCompletionUsageBlock] (we pass None for incremental chunks)
      - index: int (default 0)
      - tool_use: Optional[ChatCompletionToolCallChunk] (default None)
      - provider_specific_fields: Optional[dict]
    """
    # Defaults
    text: str = ""
    finish_reason: str = ""
    is_finished: bool = False
    index: int = 0
    provider_specific_fields: Optional[dict[str, Any]] = None
    tool_use: Optional[dict[str, Any]] = None

    try:
        # chunk may be a pydantic object with attributes
        choices = getattr(chunk, "choices", None)
        provider_specific_fields = getattr(chunk, "provider_specific_fields", None)

        if isinstance(choices, list) and choices:
            choice = choices[0]
            # Try common OpenAI-like shapes
            delta = getattr(choice, "delta", None)
            if delta is not None:
                # delta might be an object or dict
                content = getattr(delta, "content", None)
                if content is None and isinstance(delta, dict):
                    content = delta.get("content")
                if isinstance(content, str):
                    text = content

                # TOOL CALLS (OpenAI-style incremental tool_calls on delta)
                # Attempt to normalize to a ChatCompletionToolCallChunk-like dict
                # Expected shape (best-effort):
                # { index: int, id: Optional[str], type: "function", function: { name: str|None, arguments: str|None } }
                tool_calls = getattr(delta, "tool_calls", None)
                if tool_calls is None and isinstance(delta, dict):
                    tool_calls = delta.get("tool_calls")
                if isinstance(tool_calls, list) and tool_calls:
                    tc = tool_calls[0]
                    # tc can be a dict or object with attributes
                    def _get(obj, key, default=None):
                        if isinstance(obj, dict):
                            return obj.get(key, default)
                        return getattr(obj, key, default)

                    tc_index = _get(tc, "index", 0)
                    tc_id = _get(tc, "id", None)
                    tc_type = _get(tc, "type", "function")
                    fn = _get(tc, "function", {})
                    fn_name = _get(fn, "name", None)
                    fn_args = _get(fn, "arguments", None)
                    # Ensure arguments is a string for streaming deltas
                    if fn_args is not None and not isinstance(fn_args, str):
                        try:
                            # Last resort stringification for partial structured args
                            fn_args = str(fn_args)
                        except Exception:
                            fn_args = None
                    tool_use = {
                        "index": tc_index if isinstance(tc_index, int) else 0,
                        "id": tc_id if isinstance(tc_id, str) else None,
                        "type": tc_type if isinstance(tc_type, str) else "function",
                        "function": {
                            "name": fn_name if isinstance(fn_name, str) else None,
                            "arguments": fn_args if isinstance(fn_args, str) else None,
                        },
                    }

                # Anthropic-style tool_use block on delta
                if tool_use is None:
                    a_tool_use = getattr(delta, "tool_use", None)
                    if a_tool_use is None and isinstance(delta, dict):
                        a_tool_use = delta.get("tool_use")
                    if a_tool_use is not None:
                        def _get(obj, key, default=None):
                            if isinstance(obj, dict):
                                return obj.get(key, default)
                            return getattr(obj, key, default)
                        tu_id = _get(a_tool_use, "id", None)
                        tu_name = _get(a_tool_use, "name", None)
                        tu_input = _get(a_tool_use, "input", None)
                        # Represent input as a string for arguments to keep consistency
                        if tu_input is not None and not isinstance(tu_input, str):
                            try:
                                tu_input = str(tu_input)
                            except Exception:
                                tu_input = None
                        tool_use = {
                            "index": 0,
                            "id": tu_id if isinstance(tu_id, str) else None,
                            "type": "function",
                            "function": {
                                "name": tu_name if isinstance(tu_name, str) else None,
                                "arguments": tu_input if isinstance(tu_input, str) else None,
                            },
                        }

                # Older OpenAI-style function_call on delta
                if tool_use is None:
                    function_call = getattr(delta, "function_call", None)
                    if function_call is None and isinstance(delta, dict):
                        function_call = delta.get("function_call")
                    if function_call is not None:
                        # function_call can be dict-like or object-like
                        fn_name = None
                        fn_args = None
                        if isinstance(function_call, dict):
                            fn_name = function_call.get("name")
                            fn_args = function_call.get("arguments")
                        else:
                            fn_name = getattr(function_call, "name", None)
                            fn_args = getattr(function_call, "arguments", None)
                        if fn_args is not None and not isinstance(fn_args, str):
                            try:
                                fn_args = str(fn_args)
                            except Exception:
                                fn_args = None
                        tool_use = {
                            "index": 0,
                            "id": None,
                            "type": "function",
                            "function": {
                                "name": fn_name if isinstance(fn_name, str) else None,
                                "arguments": fn_args if isinstance(fn_args, str) else None,
                            },
                        }

            # Some providers use `text`
            if not text:
                content_text = getattr(choice, "text", None)
                if isinstance(content_text, str):
                    text = content_text

            # Finish reason & index if available
            fr = getattr(choice, "finish_reason", None)
            if isinstance(fr, str):
                finish_reason = fr
                is_finished = True if fr else False

            idx = getattr(choice, "index", None)
            if isinstance(idx, int):
                index = idx

        # Fallbacks
        if not isinstance(text, str):
            text = ""
        if not isinstance(finish_reason, str):
            finish_reason = ""
        if not isinstance(index, int):
            index = 0

    except Exception as e:
        # On any unexpected structure, log and pass through minimal chunk
        logger.debug("Failed to convert stream chunk to generic format: %s", e)

    return {
        "text": text,
        "is_finished": is_finished,
        "finish_reason": finish_reason,
        "usage": None,
        "index": index,
        "tool_use": tool_use,
        "provider_specific_fields": provider_specific_fields,
    }

class CustomLLMRouter(CustomLLM):
    """
    Routes model requests to the correct provider and parameters.
    """

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
        headers={},
        timeout: Optional[Union[float, httpx.Timeout]] = None,
        client: Optional[HTTPHandler] = None,
    ) -> ModelResponse:
        model, extra_params = route_model(model)
        optional_params.update(extra_params)

        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers,
                timeout=timeout,
                client=client,
                **(optional_params or {}),
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
        headers={},
        timeout: Optional[Union[float, httpx.Timeout]] = None,
        client: Optional[AsyncHTTPHandler] = None,
    ) -> ModelResponse:
        model, extra_params = route_model(model)
        optional_params.update(extra_params)

        try:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers,
                timeout=timeout,
                client=client,
                **(optional_params or {}),
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
        headers={},
        timeout: Optional[Union[float, httpx.Timeout]] = None,
        client: Optional[HTTPHandler] = None,
    ) -> Generator[GenericStreamingChunk, None, None]:
        model, extra_params = route_model(model)

        optional_params.update(extra_params)
        optional_params["stream"] = True

        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers,
                timeout=timeout,
                client=client,
                **(optional_params or {}),
            )
        except Exception as e:
            raise RuntimeError(f"[STREAMING] Error calling litellm.completion: {e}") from e

        for chunk in response:
            yield _to_generic_streaming_chunk(chunk)

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
        headers={},
        timeout: Optional[Union[float, httpx.Timeout]] = None,
        client: Optional[AsyncHTTPHandler] = None,
    ) -> AsyncGenerator[GenericStreamingChunk, None]:
        model, extra_params = route_model(model)

        optional_params.update(extra_params)
        optional_params["stream"] = True

        try:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                logger_fn=logger_fn,
                headers=headers,
                timeout=timeout,
                client=client,
                **optional_params,
            )
        except Exception as e:
            raise RuntimeError(f"[ASTREAMING] Error calling litellm.acompletion: {e}") from e

        async for chunk in response:
            yield _to_generic_streaming_chunk(chunk)


custom_llm_router = CustomLLMRouter()
