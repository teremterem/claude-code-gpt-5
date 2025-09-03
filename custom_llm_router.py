import logging
import re
from typing import Any, AsyncGenerator, Callable, Generator, Optional, Union

import httpx
import litellm
from litellm import CustomLLM, GenericStreamingChunk, HTTPHandler, ModelResponse, AsyncHTTPHandler


logger = logging.getLogger(__name__)


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
        logger.info("%s -> %s", requested_model, final)
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
        logger.info("%s -> %s [reasoning_effort: %s]", requested_model, provider_model, effort)
        return provider_model, {"reasoning_effort": effort}

    # Default passthrough – use as-is, but log for visibility
    # If we ever want to restrict models, raise a ValueError here instead.
    logger.info("%s -> %s", requested_model, model)
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
        "tool_use": None,
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
                # custom_prompt_dict=custom_prompt_dict,
                # model_response=model_response,
                # print_verbose=print_verbose,
                # encoding=encoding,
                # logging_obj=logging_obj,
                # optional_params=optional_params,
                # acompletion=acompletion,
                # litellm_params=litellm_params,
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
