from typing import AsyncGenerator, Callable, Generator, Optional, Union

import httpx
import litellm
from litellm import CustomLLM, GenericStreamingChunk, HTTPHandler, ModelResponse, AsyncHTTPHandler

from convert_stream import to_generic_streaming_chunk
from route_model import route_model


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
            yield to_generic_streaming_chunk(chunk)


custom_llm_router = CustomLLMRouter()
