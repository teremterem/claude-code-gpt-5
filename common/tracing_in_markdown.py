import json
from itertools import zip_longest
from typing import Optional

from litellm import ModelResponse, ResponsesAPIResponse

from common.config import TRACES_DIR
from common.utils import NOTHING


def write_request_trace(  # pylint: disable=unused-argument
    *,
    timestamp: str,
    calling_method: str,
    messages_original: Optional[list] = None,
    params_original: Optional[dict] = None,
    messages_complapi: Optional[list] = None,
    params_complapi: Optional[dict] = None,
    messages_respapi: Optional[list] = None,
    params_respapi: Optional[dict] = None,
) -> None:
    TRACES_DIR.mkdir(parents=True, exist_ok=True)
    file = TRACES_DIR / f"{timestamp}_REQUEST.md"
    if file.exists():
        # TODO Replace with a warning instead ?
        raise FileExistsError(f"File {file} already exists")

    with file.open("w", encoding="utf-8") as f:
        f.write(f"# {calling_method.upper()}\n\n")

        f.write("## Request Messages\n\n")

        if messages_original is not None and (messages_complapi is None or messages_original != messages_complapi):
            f.write("### Original:\n")
            f.write(f"```json\n{json.dumps(messages_original, indent=2)}\n```\n\n")

        if messages_complapi is not None:
            f.write("### ChatCompletions API:\n")
            f.write(f"```json\n{json.dumps(messages_complapi, indent=2)}\n```\n\n")

        if messages_respapi is not None:
            f.write("### Responses API:\n")
            f.write(f"```json\n{json.dumps(messages_respapi, indent=2)}\n```\n")

        f.write("## Request Params\n\n")

        if params_original is not None and (params_complapi is None or params_original != params_complapi):
            f.write("### Original:\n")
            f.write(f"```json\n{json.dumps(params_original, indent=2)}\n```\n\n")

        if params_complapi is not None:
            f.write("### ChatCompletions API:\n")
            f.write(f"```json\n{json.dumps(params_complapi, indent=2)}\n```\n\n")

        if params_respapi is not None:
            f.write("### Responses API:\n")
            f.write(f"```json\n{json.dumps(params_respapi, indent=2)}\n```\n")


def write_response_trace(
    *,
    timestamp: str,
    calling_method: str,
    response_respapi: Optional[ResponsesAPIResponse] = None,
    response_complapi: Optional[ModelResponse] = None,
) -> None:
    TRACES_DIR.mkdir(parents=True, exist_ok=True)
    file = TRACES_DIR / f"{timestamp}_RESPONSE.md"
    if file.exists():
        # TODO Replace with a warning instead ?
        raise FileExistsError(f"File {file} already exists")

    with file.open("w", encoding="utf-8") as f:
        f.write(f"# {calling_method.upper()}\n\n")

        f.write("## Response\n\n")

        if response_respapi is not None:
            f.write("### Responses API:\n")
            f.write(f"```json\n{response_respapi.model_dump_json(indent=2)}\n```\n\n")

        if response_complapi is not None:
            f.write("### ChatCompletions API:\n")
            f.write(f"```json\n{response_complapi.model_dump_json(indent=2)}\n```\n")


def write_streaming_response_trace(
    timestamp: str,
    calling_method: str,
    respapi_chunks: Optional[list] = None,
    complapi_chunks: Optional[list] = None,
    generic_chunks: Optional[list] = None,
) -> None:
    respapi_chunks = respapi_chunks or []
    complapi_chunks = complapi_chunks or []
    generic_chunks = generic_chunks or []

    TRACES_DIR.mkdir(parents=True, exist_ok=True)
    file = TRACES_DIR / f"{timestamp}_RESPONSE_STREAM.md"
    if file.exists():
        # TODO Replace with a warning instead ?
        raise FileExistsError(f"File {file} already exists")

    with file.open("w", encoding="utf-8") as f:
        f.write(f"# {calling_method.upper()}\n\n")

        zipped = zip_longest(respapi_chunks, complapi_chunks, generic_chunks, fillvalue=NOTHING)
        for idx, (respapi_chunk, complapi_chunk, generic_chunk) in enumerate(zipped):
            f.write(f"## Response Chunk #{idx}\n\n")

            if respapi_chunk is not NOTHING:
                f.write(f"### Responses API:\n```json\n{respapi_chunk.model_dump_json(indent=2)}\n```\n\n")

            if complapi_chunk is not NOTHING:
                f.write(f"### ChatCompletions API:\n```json\n{complapi_chunk.model_dump_json(indent=2)}\n```\n\n")

            if generic_chunk is not NOTHING:
                # TODO Do `gen_chunk.model_dump_json(indent=2)` once it's not
                #  just a dict
                f.write(f"### GenericStreamingChunk:\n```json\n{json.dumps(generic_chunk, indent=2)}\n```\n\n")
