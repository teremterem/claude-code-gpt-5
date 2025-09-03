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
        return f"anthropic/{model}", {}

    # GPT-5 family with reasoning effort
    m = re.fullmatch(
        r"gpt-5(?P<variant>-(mini|nano))?-reason-(?P<effort>minimal|low|medium|high)",
        model,
    )
    if m:
        variant = m.group("variant") or ""
        effort = m.group("effort")
        provider_model = f"openai/gpt-5{variant or ''}"
        return provider_model, {"reasoning_effort": effort}

    # Default passthrough – use as-is
    # TODO Raise an error instead ?
    return model, {}

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
            )
        except Exception as e:
            raise RuntimeError(f"[STREAMING] Error calling litellm.completion: {e}") from e

        for chunk in response:
            # TODO Convert ModelResponseStream (chunk) into GenericStreamingChunk
            yield chunk

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
            # TODO Convert ModelResponseStream (chunk) into GenericStreamingChunk
            yield chunk


custom_llm_router = CustomLLMRouter()
