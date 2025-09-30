import json

from litellm import ModelResponse, ResponsesAPIResponse

from proxy.config import RESPAPI_TRACES_DIR


def write_request_trace(
    *,
    timestamp: str,
    calling_method: str,
    messages_complapi: list,
    params_complapi: dict,
    messages_respapi: list,
    params_respapi: dict,
) -> None:
    RESPAPI_TRACES_DIR.mkdir(parents=True, exist_ok=True)
    with (RESPAPI_TRACES_DIR / f"{timestamp}_REQUEST.md").open("w", encoding="utf-8") as f:
        f.write(f"# {calling_method}\n\n")

        f.write("## Request Messages\n\n")

        f.write("### Completion API:\n")
        f.write(f"```json\n{json.dumps(messages_complapi, indent=2)}\n```\n\n")

        f.write("### Responses API:\n")
        f.write(f"```json\n{json.dumps(messages_respapi, indent=2)}\n```\n\n")

        f.write("## Request Params\n\n")

        f.write("### Completion API:\n")
        f.write(f"```json\n{json.dumps(params_complapi, indent=2)}\n```\n\n")

        f.write("### Responses API:\n")
        f.write(f"```json\n{json.dumps(params_respapi, indent=2)}\n```\n")


def write_response_trace(
    timestamp: str,
    calling_method: str,
    response: ResponsesAPIResponse,
    response_complapi: ModelResponse,
) -> None:
    RESPAPI_TRACES_DIR.mkdir(parents=True, exist_ok=True)
    with (RESPAPI_TRACES_DIR / f"{timestamp}_RESPONSE.md").open("w", encoding="utf-8") as f:
        f.write(f"# {calling_method}\n\n")

        f.write("## Response\n\n")

        f.write("### Responses API:\n")
        f.write(f"```json\n{response.model_dump_json(indent=2)}\n```\n\n")

        f.write("### Completion API:\n")
        f.write(f"```json\n{response_complapi.model_dump_json(indent=2)}\n```\n")


def write_streaming_response_trace(
    timestamp: str,
    calling_method: str,
    responses_chunks: list,
    generic_chunks: list,
) -> None:
    RESPAPI_TRACES_DIR.mkdir(parents=True, exist_ok=True)
    with (RESPAPI_TRACES_DIR / f"{timestamp}_RESPONSE_STREAM.md").open("w", encoding="utf-8") as f:
        f.write(f"# {calling_method}\n\n")

        for idx, (resp_chunk, gen_chunk) in enumerate(zip(responses_chunks, generic_chunks)):
            f.write(f"## Response Chunk #{idx}\n\n")
            f.write(f"### Responses API:\n```json\n{resp_chunk.model_dump_json(indent=2)}\n```\n\n")
            # TODO Do `gen_chunk.model_dump_json(indent=2)` once it's not just a dict
            f.write(f"### GenericStreamingChunk:\n```json\n{json.dumps(gen_chunk, indent=2)}\n```\n\n")
