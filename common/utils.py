# pylint: disable=too-many-branches,too-many-locals,too-many-statements,too-many-return-statements
# pylint: disable=too-many-nested-blocks
"""
NOTE: The utilities in this module were mostly vibe-coded without review.
"""
import os
from datetime import UTC, datetime
from collections.abc import Mapping, Sequence
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
    Generate timestamp in format YYYYmmdd_HHMMSS_fff_fff in UTC.

    An example of how these timestamps are used later:

    `.traces/20251005_140642_180_342_RESPONSE_STREAM.md`
    """
    now = datetime.now(UTC)

    str_repr = now.strftime("%Y%m%d_%H%M%S_%f")
    # Let's separate the milliseconds from the microseconds with an underscore
    # to make it more readable
    return f"{str_repr[:-3]}_{str_repr[-3:]}"


def to_generic_streaming_chunk(chunk: ModelResponseStream) -> GenericStreamingChunk:
    chunk_data = _as_dict(_coerce_to_plain_obj(chunk))
    chunk_payload = _build_chunk_payload(chunk_data)
    return GenericStreamingChunk(**chunk_payload)


def _build_chunk_payload(chunk_data: Dict[str, Any]) -> Dict[str, Any]:
    choices_raw = chunk_data.get("choices") or []
    choices = [_build_choice(choice) for choice in _as_list(choices_raw)]

    payload: Dict[str, Any] = {
        "id": chunk_data.get("id"),
        "created": chunk_data.get("created"),
        "model": chunk_data.get("model"),
        "object": chunk_data.get("object"),
        "system_fingerprint": chunk_data.get("system_fingerprint"),
        "provider_specific_fields": chunk_data.get("provider_specific_fields"),
        "citations": chunk_data.get("citations"),
        "choices": choices,
    }

    if "usage" in chunk_data:
        payload["usage"] = chunk_data.get("usage")

    return payload


def _build_choice(choice: Any) -> Dict[str, Any]:
    choice_dict = _as_dict(_coerce_to_plain_obj(choice))
    delta_dict = _build_delta(choice_dict.get("delta"))

    choice_payload: Dict[str, Any] = {
        "index": choice_dict.get("index"),
        "delta": delta_dict,
        "finish_reason": choice_dict.get("finish_reason"),
        "logprobs": choice_dict.get("logprobs"),
    }

    return choice_payload


def _build_delta(delta: Any) -> Dict[str, Any]:
    delta_dict = _as_dict(_coerce_to_plain_obj(delta))
    processed: Dict[str, Any] = {}

    for key, value in delta_dict.items():
        if key == "tool_calls":
            processed[key] = _build_tool_calls(value)
        else:
            processed[key] = value

    return processed


def _build_tool_calls(tool_calls: Any) -> Any:
    if tool_calls is None:
        return None

    calls_list = _as_list(tool_calls)
    return [_build_tool_call_delta(call) for call in calls_list]


def _build_tool_call_delta(tool_call: Any) -> Dict[str, Any]:
    tool_call_dict = _as_dict(_coerce_to_plain_obj(tool_call))
    processed: Dict[str, Any] = {}

    for key, value in tool_call_dict.items():
        if key == "function":
            processed[key] = _as_dict(_coerce_to_plain_obj(value)) if value is not None else None
        else:
            processed[key] = value

    return processed


def _coerce_to_plain_obj(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _coerce_to_plain_obj(val) for key, val in value.items()}

    if isinstance(value, list):
        return [_coerce_to_plain_obj(item) for item in value]

    for attr_name in ("model_dump", "dict", "to_dict"):
        attr = getattr(value, attr_name, None)
        if attr:
            if callable(attr):
                try:
                    result = attr(mode="python")  # type: ignore[call-arg]
                except TypeError:
                    try:
                        result = attr()
                    except TypeError:
                        result = attr
            else:
                result = attr
            return _coerce_to_plain_obj(result)

    if hasattr(value, "__iter__") and hasattr(value, "keys"):
        try:
            return {key: _coerce_to_plain_obj(value[key]) for key in value.keys()}  # type: ignore[index]
        except Exception:  # pylint: disable=broad-except
            pass

    if hasattr(value, "__dict__") and value.__dict__:
        return {key: _coerce_to_plain_obj(val) for key, val in vars(value).items() if not key.startswith("_")}

    return value


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return [value]
