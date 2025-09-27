# pylint: disable=too-many-branches,too-many-locals,too-many-statements,too-many-return-statements
# pylint: disable=too-many-nested-blocks
"""
NOTE: The utilities in this module were mostly vibe-coded without review.
"""
from copy import deepcopy
from typing import Any, Optional, Union
import json

from litellm import GenericStreamingChunk, ModelResponse


class ServerError(RuntimeError):
    def __init__(self, error: Union[BaseException, str], highlight: bool = True):
        if highlight:
            # Highlight error messages in red, so the actual problems are
            # easier to spot in long tracebacks
            super().__init__(f"\033[1;31m{error}\033[0m")
        else:
            super().__init__(error)


def to_generic_streaming_chunk(chunk: Any) -> GenericStreamingChunk:
    """
    Best-effort convert a LiteLLM ModelResponseStream chunk into GenericStreamingChunk.

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
                # { index: int, id: Optional[str], type: "function", function: {name: str|None, arguments: str|None} }
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
                        except Exception as e:
                            raise RuntimeError(
                                f"Failed to convert OpenAI tool_use to GenericStreamingChunk: {e}"
                            ) from e

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
                            except Exception as e:
                                raise RuntimeError(
                                    f"Failed to convert Anthropic tool_use to GenericStreamingChunk: {e}"
                                ) from e

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
                            except Exception as e:
                                raise RuntimeError(
                                    f"Failed to convert OpenAI function_call to GenericStreamingChunk: {e}"
                                ) from e

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
                is_finished = bool(fr)

            idx = getattr(choice, "index", None)
            if isinstance(idx, int):
                index = idx

        else:
            responses_data = _try_parse_responses_chunk(chunk)
            if responses_data is not None:
                text = responses_data["text"]
                finish_reason = responses_data["finish_reason"]
                is_finished = responses_data["is_finished"]
                index = responses_data["index"]
                if responses_data["tool_use"] is not None:
                    tool_use = responses_data["tool_use"]
                new_provider_fields = responses_data["provider_specific_fields"]
                if new_provider_fields is not None:
                    provider_specific_fields = new_provider_fields

        # Fallbacks
        if not isinstance(text, str):
            text = ""
        if not isinstance(finish_reason, str):
            finish_reason = ""
        if not isinstance(index, int):
            index = 0

    except Exception as e:
        raise RuntimeError(f"Failed to convert ModelResponseStream to GenericStreamingChunk: {e}") from e

    return {
        "text": text,
        "is_finished": is_finished,
        "finish_reason": finish_reason,
        "usage": None,  # TODO Do we have to put anything in here ?
        "index": index,
        "tool_use": tool_use,
        "provider_specific_fields": provider_specific_fields,
    }


_INPUT_TYPE_ALIASES = {
    "text": "input_text",
    "input_text": "input_text",
    "image": "input_image",
    "image_url": "input_image",
    "image_file": "input_image",
    "input_image": "input_image",
    "audio": "input_audio",
    "audio_url": "input_audio",
    "input_audio": "input_audio",
    "video": "input_video",
    "video_url": "input_video",
    "input_video": "input_video",
    "file": "input_file",
    "document": "input_file",
    "input_file": "input_file",
}


_OUTPUT_TYPE_ALIASES = {
    "text": "output_text",
    "output_text": "output_text",
    "image": "output_image",
    "image_url": "output_image",
    "output_image": "output_image",
    "audio": "output_audio",
    "audio_url": "output_audio",
    "output_audio": "output_audio",
    "video": "output_video",
    "video_url": "output_video",
    "output_video": "output_video",
}


_TOOL_TYPE_ALIASES = {
    "text": "tool_result",
    "tool_result": "tool_result",
    "input_text": "tool_result",
    "output_text": "tool_result",
}


_CONTENT_KEYS_TO_DROP = {"cache_control"}

_FUNCTION_METADATA_KEYS = ("description", "parameters", "strict")

_UNSUPPORTED_RESPONSES_PARAMS = {"stream_options"}


def convert_chat_params_to_responses(optional_params: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of optional params adjusted for the Responses API."""

    if optional_params is None:
        return {}
    if not isinstance(optional_params, dict):
        raise TypeError("optional_params must be a dictionary when targeting the Responses API")

    params = deepcopy(optional_params)

    tools = params.get("tools")
    if tools is not None:
        converted_tools = _convert_tools_list(tools)
        if converted_tools:
            params["tools"] = converted_tools
        else:
            params.pop("tools", None)

    functions = params.pop("functions", None)
    if functions:
        function_tools = _convert_functions_list(functions)
        if function_tools:
            params.setdefault("tools", [])
            params["tools"].extend(function_tools)

    tool_choice = params.get("tool_choice")
    if tool_choice is not None:
        converted_choice = _convert_tool_choice(tool_choice)
        if converted_choice is None:
            params.pop("tool_choice", None)
        else:
            params["tool_choice"] = converted_choice

    for key in list(params):
        if key in _UNSUPPORTED_RESPONSES_PARAMS:
            params.pop(key, None)

    return params


def convert_chat_messages_to_responses_items(messages: list[Any]) -> list[dict[str, Any]]:
    """Convert Chat Completions style messages into Responses API compatible items."""

    if not isinstance(messages, list):
        raise TypeError("messages must be provided as a list")

    converted: list[dict[str, Any]] = []
    for idx, message in enumerate(messages):
        if not isinstance(message, dict):
            raise TypeError(f"Chat message at index {idx} must be a mapping")

        role = message.get("role")
        if not isinstance(role, str) or not role:
            raise ValueError(f"Chat message at index {idx} is missing a valid role")

        new_message: dict[str, Any] = {k: deepcopy(v) for k, v in message.items() if k != "content"}
        content = message.get("content")
        new_message["content"] = _normalize_message_content(role, content)
        converted.append(new_message)

    return converted


def _normalize_message_content(role: str, content: Any) -> list[Any]:
    if isinstance(content, str):
        return [{"type": _default_content_type_for_role(role), "text": content}]

    if isinstance(content, dict):
        return [_convert_content_part(role, content)]

    if isinstance(content, list):
        normalized_parts: list[Any] = []
        for part in content:
            normalized_parts.append(_convert_content_part(role, part))
        return normalized_parts

    if content is None:
        return []

    # Fallback to string representation
    return [{"type": _default_content_type_for_role(role), "text": str(content)}]


def _convert_content_part(role: str, part: Any) -> dict[str, Any]:
    if isinstance(part, str):
        return {"type": _default_content_type_for_role(role), "text": part}

    if not isinstance(part, dict):
        return {"type": _default_content_type_for_role(role), "text": str(part)}

    new_part = deepcopy(part)
    for key in list(new_part):
        if key in _CONTENT_KEYS_TO_DROP:
            new_part.pop(key, None)
    part_type = new_part.get("type")
    normalized_type = _normalize_type_by_role(role, part_type)
    if normalized_type is not None:
        new_part["type"] = normalized_type
    elif "type" not in new_part:
        new_part["type"] = _default_content_type_for_role(role)
    else:
        new_part["type"] = str(new_part["type"])

    part_type_key = new_part["type"]

    if part_type_key in {"input_text", "output_text", "tool_result"}:
        if "text" not in new_part and "content" in new_part:
            new_part["text"] = new_part.pop("content")
        elif "text" not in new_part and "value" in new_part:
            new_part["text"] = new_part.pop("value")
        elif "text" not in new_part and "message" in new_part:
            new_part["text"] = new_part.pop("message")
        if "text" not in new_part:
            new_part["text"] = ""

    if part_type_key == "input_image":
        if "image_url" in new_part:
            image_payload = new_part["image_url"]
            if isinstance(image_payload, dict) and "url" in image_payload and len(image_payload) == 1:
                new_part["image_url"] = image_payload["url"]
        elif "image" in new_part:
            new_part["image_url"] = new_part.pop("image")

    if part_type_key == "input_audio" and "audio" in new_part and "audio_url" not in new_part:
        new_part["audio_url"] = new_part.pop("audio")

    if part_type_key == "input_video" and "video" in new_part and "video_url" not in new_part:
        new_part["video_url"] = new_part.pop("video")

    if part_type_key == "input_file" and "file" in new_part and "file_id" not in new_part:
        new_part["file_id"] = new_part.pop("file")

    return new_part


def _convert_tools_list(tools: Any) -> list[dict[str, Any]]:
    if tools is None:
        return []

    if isinstance(tools, dict):
        iterable = [tools]
    elif isinstance(tools, list):
        iterable = tools
    else:
        raise TypeError("tools must be a list or dict when targeting the Responses API")

    converted: list[dict[str, Any]] = []
    for idx, tool in enumerate(iterable):
        if not isinstance(tool, dict):
            raise TypeError(f"tool definition at index {idx} must be a mapping")

        # Already Responses format
        if tool.get("type") == "function" and "function" not in tool:
            name = tool.get("name")
            if isinstance(name, str) and name:
                converted.append(deepcopy(tool))
            continue

        if tool.get("type") == "function" or "function" in tool:
            fn_payload = tool.get("function") if isinstance(tool.get("function"), dict) else {}
            name = fn_payload.get("name") or tool.get("name")
            if not isinstance(name, str) or not name:
                continue

            new_tool = {k: deepcopy(v) for k, v in tool.items() if k not in {"function"}}
            new_tool["type"] = "function"
            new_tool["name"] = name

            for key in _FUNCTION_METADATA_KEYS:
                if key in fn_payload and key not in new_tool:
                    new_tool[key] = deepcopy(fn_payload[key])

            converted.append(new_tool)
            continue

        converted.append(deepcopy(tool))

    return converted


def _convert_functions_list(functions: Any) -> list[dict[str, Any]]:
    if functions is None:
        return []

    if isinstance(functions, dict):
        iterable = [functions]
    elif isinstance(functions, list):
        iterable = functions
    else:
        raise TypeError("functions must be a list or dict when targeting the Responses API")

    converted: list[dict[str, Any]] = []
    for idx, fn in enumerate(iterable):
        if not isinstance(fn, dict):
            raise TypeError(f"function definition at index {idx} must be a mapping")

        name = fn.get("name")
        if not isinstance(name, str) or not name:
            continue

        tool_def: dict[str, Any] = {"type": "function", "name": name}
        for key in _FUNCTION_METADATA_KEYS:
            if key in fn:
                tool_def[key] = deepcopy(fn[key])

        converted.append(tool_def)

    return converted


def _convert_tool_choice(tool_choice: Any) -> Optional[Any]:
    if isinstance(tool_choice, str):
        return tool_choice

    if isinstance(tool_choice, dict):
        if isinstance(tool_choice.get("function"), dict):
            fn_payload = tool_choice["function"]
            name = fn_payload.get("name")
            if not isinstance(name, str) or not name:
                return None

            converted = {"type": "function", "name": name}
            if "arguments" in fn_payload:
                converted["arguments"] = deepcopy(fn_payload["arguments"])
            if "output" in fn_payload:
                converted["output"] = deepcopy(fn_payload["output"])
            return converted

        if tool_choice.get("type") == "function":
            name = tool_choice.get("name")
            if not isinstance(name, str) or not name:
                return None
            converted = {"type": "function", "name": name}
            if "arguments" in tool_choice:
                converted["arguments"] = deepcopy(tool_choice["arguments"])
            if "output" in tool_choice:
                converted["output"] = deepcopy(tool_choice["output"])
            return converted

        return deepcopy(tool_choice)

    return None


def _normalize_type_by_role(role: str, part_type: Any) -> Optional[str]:
    if not isinstance(part_type, str):
        return None

    lowered = part_type.lower()
    if role == "assistant":
        return _OUTPUT_TYPE_ALIASES.get(lowered, lowered if lowered.startswith("output_") else None)
    if role == "tool":
        return _TOOL_TYPE_ALIASES.get(lowered, lowered if lowered.startswith("tool_") else None)
    return _INPUT_TYPE_ALIASES.get(lowered, lowered if lowered.startswith("input_") else None)


def _default_content_type_for_role(role: str) -> str:
    if role == "assistant":
        return "output_text"
    if role == "tool":
        return "tool_result"
    return "input_text"


def _try_parse_responses_chunk(chunk: Any) -> Optional[dict[str, Any]]:
    def _get(obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    chunk_type = _get(chunk, "type")
    if not isinstance(chunk_type, str) or not chunk_type:
        chunk_type = _get(chunk, "event")
    if not isinstance(chunk_type, str) or not chunk_type:
        return None
    if not chunk_type.startswith("response."):
        return None

    finish_reason = _get(chunk, "finish_reason")
    if not isinstance(finish_reason, str):
        finish_reason = ""

    index = _get(chunk, "output_index")
    if not isinstance(index, int):
        candidate_index = _get(chunk, "index")
        index = candidate_index if isinstance(candidate_index, int) else 0

    delta = _get(chunk, "delta")
    text = ""
    if isinstance(delta, str):
        text = delta
    elif isinstance(delta, dict):
        delta_text = delta.get("text")
        if isinstance(delta_text, str):
            text = delta_text

    if not text:
        text_candidate = _get(chunk, "text")
        if isinstance(text_candidate, str):
            text = text_candidate

    if not text:
        content_candidate = _get(chunk, "content")
        if isinstance(content_candidate, str):
            text = content_candidate

    if not text:
        response_obj = _get(chunk, "response")
        if isinstance(response_obj, dict):
            output_text = response_obj.get("output_text")
            if isinstance(output_text, list):
                text = "".join([part for part in output_text if isinstance(part, str)])

    tool_use = None
    if "tool_call" in chunk_type:
        payloads: list[dict[str, Any]] = []
        if isinstance(delta, dict):
            payloads.append(delta)
        tool_payload = _get(chunk, "tool_call")
        if isinstance(tool_payload, dict):
            payloads.append(tool_payload)
        for payload in payloads:
            name = payload.get("name")
            arguments = payload.get("arguments") or payload.get("input") or payload.get("input_json")
            if arguments is not None and not isinstance(arguments, str):
                try:
                    arguments = str(arguments)
                except Exception as e:
                    raise RuntimeError("Failed to convert Responses tool_call arguments to string") from e
            call_id = payload.get("id") or payload.get("call_id") or payload.get("tool_call_id")
            tool_use = {
                "index": index,
                "id": call_id if isinstance(call_id, str) else None,
                "type": "function",
                "function": {
                    "name": name if isinstance(name, str) else None,
                    "arguments": arguments if isinstance(arguments, str) else None,
                },
            }
            break

    terminal_suffixes = (".completed", ".failed", ".cancelled", ".canceled")
    is_finished = any(chunk_type.endswith(suffix) for suffix in terminal_suffixes)
    if chunk_type in {"response.completed", "response.error", "response.canceled", "response.cancelled"}:
        is_finished = True

    if chunk_type == "response.error" and not finish_reason:
        finish_reason = "error"
    elif is_finished and not finish_reason:
        finish_reason = "stop"

    provider_specific_fields: dict[str, Any] = {"responses_type": chunk_type}
    for key in ("response_id", "output_index", "item_id", "id", "status"):
        value = _get(chunk, key)
        if value is not None:
            provider_specific_fields[key] = deepcopy(value)
    if isinstance(delta, dict):
        provider_specific_fields["delta"] = deepcopy(delta)
    if not provider_specific_fields:
        provider_specific_fields = None

    if not isinstance(text, str):
        text = ""

    return {
        "text": text,
        "finish_reason": finish_reason,
        "is_finished": is_finished,
        "index": index,
        "tool_use": tool_use,
        "provider_specific_fields": provider_specific_fields,
    }


def convert_responses_to_model_response(responses_response: Any) -> ModelResponse:
    """Best-effort convert a LiteLLM ResponsesAPIResponse into a ModelResponse."""

    if responses_response is None:
        raise ValueError("responses_response cannot be None")

    def _get(obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    model_response: dict[str, Any] = {}

    # Top-level metadata
    model_response["id"] = _get(responses_response, "id")
    model_response["object"] = _get(responses_response, "object", "chat.completion")
    model_response["created"] = _get(responses_response, "created") or _get(responses_response, "created_at")
    model_response["model"] = _get(responses_response, "model")

    metadata = _get(responses_response, "metadata")
    if metadata is not None:
        model_response["metadata"] = deepcopy(metadata)

    # Usage
    usage = _get(responses_response, "usage")
    token_usage: dict[str, Any]
    if isinstance(usage, dict):
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")
        if prompt_tokens is not None and completion_tokens is not None:
            total_tokens = prompt_tokens + completion_tokens
        token_usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }
        model_response["usage"] = token_usage

    # Aggregate assistant content and optional tool calls
    text_segments: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    function_call: Optional[dict[str, Any]] = None
    output = _get(responses_response, "output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type") or item.get("event")
            if item_type == "message":
                content = item.get("content")
                text_value = _flatten_responses_text(content)
                if text_value:
                    text_segments.append(text_value)
            elif item_type == "tool_call":
                converted_tool = _convert_responses_tool_call(item)
                if converted_tool is not None:
                    tool_calls.append(converted_tool)
            elif item_type == "function_call" and function_call is None:
                maybe_call = _convert_responses_tool_call(item)
                if maybe_call is not None:
                    function_call = maybe_call["function"]

    message_content = "".join(text_segments) if text_segments else ""

    # Create choices entry
    choice_message: dict[str, Any] = {
        "role": "assistant",
        "content": message_content,
    }
    if tool_calls:
        choice_message["tool_calls"] = tool_calls
    if function_call is not None:
        choice_message["function_call"] = function_call

    finish_reason = None
    status = _get(responses_response, "status")
    if isinstance(status, str):
        if status == "completed":
            finish_reason = "stop"
        elif status in {"canceled", "cancelled"}:
            finish_reason = "cancelled"
        elif status == "failed":
            finish_reason = "error"

    model_response["choices"] = [
        {
            "index": 0,
            "finish_reason": finish_reason,
            "message": choice_message,
        }
    ]

    # Add response-level metadata for traceability
    provider_fields: dict[str, Any] = {}
    for key in ("response", "meta", "trace_id", "previous_response_id"):
        value = _get(responses_response, key)
        if value is not None:
            provider_fields[key] = deepcopy(value)
    if provider_fields:
        model_response["provider_specific_fields"] = provider_fields

    return ModelResponse(**model_response)


def _flatten_responses_text(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        segments: list[str] = []
        for part in content:
            if isinstance(part, dict):
                # Prefer explicit text fields
                for key in ("text", "input_text", "output_text"):
                    value = part.get(key)
                    if isinstance(value, str):
                        segments.append(value)
                        break
                else:
                    nested = part.get("content")
                    if nested is not None:
                        flattened = _flatten_responses_text(nested)
                        if flattened:
                            segments.append(flattened)
            elif isinstance(part, str):
                segments.append(part)
        return "".join(segments)

    if isinstance(content, dict):
        return _flatten_responses_text(content.get("content"))

    return "" if content is None else str(content)


def _convert_responses_tool_call(payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    name = payload.get("name") or payload.get("function_name")
    if not isinstance(name, str) or not name:
        return None

    call_id = payload.get("id") or payload.get("call_id") or payload.get("tool_call_id")

    raw_arguments = payload.get("arguments")
    if raw_arguments is None:
        raw_arguments = payload.get("input") or payload.get("input_arguments")

    arguments: Optional[str]
    if isinstance(raw_arguments, str):
        arguments = raw_arguments
    elif isinstance(raw_arguments, (list, dict)):
        flattened = _flatten_responses_text(raw_arguments)
        if flattened:
            arguments = flattened
        else:
            try:
                arguments = json.dumps(raw_arguments)
            except Exception as e:
                raise RuntimeError("Failed to JSON-encode Responses tool_call arguments") from e
    else:
        arguments = str(raw_arguments) if raw_arguments is not None else None

    tool_call = {
        "id": call_id if isinstance(call_id, str) else None,
        "type": "function",
        "function": {
            "name": name,
            "arguments": arguments or "",
        },
    }

    return tool_call
