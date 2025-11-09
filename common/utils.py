# pylint: disable=too-many-branches,too-many-locals,too-many-statements,too-many-return-statements
# pylint: disable=too-many-nested-blocks
"""
NOTE: The utilities in this module were mostly vibe-coded without review.
"""
import os
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Union

from litellm import GenericStreamingChunk, ModelResponseStream


class ProxyError(RuntimeError):
    def __init__(self, error: Union[BaseException, str], highlight: Optional[bool] = None):

        final_highlight: bool
        if highlight is None:
            # No value provided, read from env var (default 'True')
            env_val = os.environ.get("PROXY_ERROR_HIGHLIGHT", "True")
            final_highlight = env_val.lower() not in ("false", "0", "no")
        else:
            # Value was provided, use it
            final_highlight = highlight

        if final_highlight:
            # Highlight error messages in red, so the actual problems are
            # easier to spot in long tracebacks
            super().__init__(f"\033[1;31m{error}\033[0m")
        else:
            super().__init__(error)


def env_var_to_bool(value: Optional[str], default: str = "false") -> bool:
    """
    Convert environment variable string to boolean.

    Args:
        value: The environment variable value (or None if not set)
        default: Default value to use if value is None

    Returns:
        True if the value (or default) is a truthy string, False otherwise
    """
    return (value or default).lower() in ("true", "1", "on", "yes", "y")


def generate_timestamp_utc() -> str:
    """
    Generate timestamp in format YYYYmmdd_HHMMSS_fffff in UTC.

    An example of how these timestamps are used later:

    `.traces/20251005_140642_18034_RESPONSE_STREAM.md`
    """
    now = datetime.now(UTC)
    # Keep only the first 5 digits of microseconds
    return now.strftime("%Y%m%d_%H%M%S_%f")[:-1]


def to_generic_streaming_chunk(chunk: ModelResponseStream) -> GenericStreamingChunk:
    return GenericStreamingChunk(**_build_generic_streaming_chunk_payload(chunk))


def _build_generic_streaming_chunk_payload(chunk: ModelResponseStream) -> Dict[str, Any]:
    chunk_dict = _model_to_dict(chunk)

    payload: Dict[str, Any] = {
        "id": chunk_dict.get("id"),
        "created": chunk_dict.get("created"),
        "model": chunk_dict.get("model"),
        "object": chunk_dict.get("object"),
        "system_fingerprint": chunk_dict.get("system_fingerprint"),
        "provider_specific_fields": chunk_dict.get("provider_specific_fields"),
        "citations": chunk_dict.get("citations"),
        "choices": _convert_choices(chunk_dict.get("choices") or []),
    }

    if "usage" in chunk_dict:
        payload["usage"] = chunk_dict.get("usage")

    return payload


def _convert_choices(choices: List[Any]) -> List[Dict[str, Any]]:
    converted: List[Dict[str, Any]] = []
    for choice in choices:
        choice_dict = _model_to_dict(choice)
        choice_payload: Dict[str, Any] = {
            "index": choice_dict.get("index"),
            "finish_reason": choice_dict.get("finish_reason"),
            "logprobs": choice_dict.get("logprobs"),
        }

        if "delta" in choice_dict:
            choice_payload["delta"] = _convert_delta(choice_dict.get("delta"))

        if "provider_specific_fields" in choice_dict:
            choice_payload["provider_specific_fields"] = choice_dict.get("provider_specific_fields")

        converted.append(choice_payload)
    return converted


def _convert_delta(delta: Any) -> Any:
    if delta is None:
        return None

    delta_dict = _model_to_dict(delta)
    converted_delta: Dict[str, Any] = dict(delta_dict)

    if "tool_calls" in converted_delta and converted_delta["tool_calls"] is not None:
        tool_calls = converted_delta["tool_calls"]
        if isinstance(tool_calls, list):
            converted_delta["tool_calls"] = [_convert_tool_call(tc) for tc in tool_calls]

    return converted_delta


def _convert_tool_call(tool_call: Any) -> Any:
    if tool_call is None:
        return None

    tool_call_dict = _model_to_dict(tool_call)
    converted_tool_call: Dict[str, Any] = dict(tool_call_dict)

    if "function" in converted_tool_call:
        function_payload = converted_tool_call.get("function")
        converted_tool_call["function"] = _convert_tool_call_function(function_payload)

    return converted_tool_call


def _convert_tool_call_function(function_payload: Any) -> Any:
    if function_payload is None:
        return None

    function_dict = _model_to_dict(function_payload)
    return dict(function_dict)


def _model_to_dict(value: Any) -> Dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()  # type: ignore[no-any-return]
    raise TypeError(f"Unsupported value type for conversion: {type(value)!r}")
