from typing import Any, AsyncGenerator, Callable, Generator, Optional, Union

import httpx
import litellm
from litellm import CustomLLM, GenericStreamingChunk, HTTPHandler, ModelResponse, AsyncHTTPHandler

from common.config import WRITE_TRACES_TO_FILES
from common.tracing_in_markdown import write_request_trace, write_response_trace, write_streaming_response_trace
from common.utils import generate_timestamp_local_tz, to_generic_streaming_chunk


_YODA_SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Regardless of the request, respond in Yoda-speak."
        " Short sentences, inverted syntax, and the wisdom of the Jedi, you must use."
    ),
}


class YodaSpeakLLM(CustomLLM):
    # pylint: disable=too-many-positional-arguments,too-many-locals
    """
    Proxy wrapper that forces Yoda-speak responses from the underlying LLM.
    """

    def __init__(self, *, target_model: str = "openai/gpt-4o", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.target_model = target_model

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
        timestamp = generate_timestamp_local_tz()
        calling_method = "completion"

        messages_modified = messages + [_YODA_SYSTEM_PROMPT]

        if WRITE_TRACES_TO_FILES:
            write_request_trace(
                timestamp=timestamp,
                calling_method=calling_method,
                messages_original=messages,
                messages_complapi=messages_modified,
                params_original=optional_params,
            )

        response = litellm.completion(
            model=self.target_model,
            messages=messages_modified,
            logger_fn=logger_fn,
            headers=headers or {},
            timeout=timeout,
            client=client,
            # Drop any params that are not supported by the provider
            drop_params=True,
            **optional_params,
        )

        if WRITE_TRACES_TO_FILES:
            write_response_trace(
                timestamp=timestamp,
                calling_method=calling_method,
                response_complapi=response,
            )

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
        timestamp = generate_timestamp_local_tz()
        calling_method = "acompletion"

        messages_modified = messages + [_YODA_SYSTEM_PROMPT]

        if WRITE_TRACES_TO_FILES:
            write_request_trace(
                timestamp=timestamp,
                calling_method=calling_method,
                messages_original=messages,
                messages_complapi=messages_modified,
                params_original=optional_params,
            )

        response = await litellm.acompletion(
            model=self.target_model,
            messages=messages_modified,
            logger_fn=logger_fn,
            headers=headers or {},
            timeout=timeout,
            client=client,
            # Drop any params that are not supported by the provider
            drop_params=True,
            **optional_params,
        )

        if WRITE_TRACES_TO_FILES:
            write_response_trace(
                timestamp=timestamp,
                calling_method=calling_method,
                response_complapi=response,
            )

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
        timestamp = generate_timestamp_local_tz()
        calling_method = "streaming"

        messages_modified = messages + [_YODA_SYSTEM_PROMPT]

        if WRITE_TRACES_TO_FILES:
            write_request_trace(
                timestamp=timestamp,
                calling_method=calling_method,
                messages_original=messages,
                messages_complapi=messages_modified,
                params_original=optional_params,
            )

        resp_stream = litellm.completion(
            model=self.target_model,
            messages=messages_modified,
            logger_fn=logger_fn,
            headers=headers or {},
            timeout=timeout,
            client=client,
            # Drop any params that are not supported by the provider
            drop_params=True,
            **optional_params,
        )

        complapi_chunks = []
        generic_chunks = []

        for resp_chunk in resp_stream:
            generic_chunk = to_generic_streaming_chunk(resp_chunk)
            if WRITE_TRACES_TO_FILES:
                complapi_chunks.append(resp_chunk)
                generic_chunks.append(generic_chunk)
            yield generic_chunk

        if WRITE_TRACES_TO_FILES:
            write_streaming_response_trace(
                timestamp=timestamp,
                calling_method=calling_method,
                complapi_chunks=complapi_chunks,
                generic_chunks=generic_chunks,
            )

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
        timestamp = generate_timestamp_local_tz()
        calling_method = "astreaming"

        messages_modified = messages + [_YODA_SYSTEM_PROMPT]

        if WRITE_TRACES_TO_FILES:
            write_request_trace(
                timestamp=timestamp,
                calling_method=calling_method,
                messages_original=messages,
                messages_complapi=messages_modified,
                params_original=optional_params,
            )

        resp_stream = await litellm.acompletion(
            model=self.target_model,
            messages=messages_modified,
            logger_fn=logger_fn,
            headers=headers or {},
            timeout=timeout,
            client=client,
            # Drop any params that are not supported by the provider
            drop_params=True,
            **optional_params,
        )

        complapi_chunks = []
        generic_chunks = []

        async for resp_chunk in resp_stream:
            generic_chunk = to_generic_streaming_chunk(resp_chunk)
            if WRITE_TRACES_TO_FILES:
                complapi_chunks.append(resp_chunk)
                generic_chunks.append(generic_chunk)
            yield generic_chunk

        if WRITE_TRACES_TO_FILES:
            write_streaming_response_trace(
                timestamp=timestamp,
                calling_method=calling_method,
                complapi_chunks=complapi_chunks,
                generic_chunks=generic_chunks,
            )


yoda_speak_llm = YodaSpeakLLM()
